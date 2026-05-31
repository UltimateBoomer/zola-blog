+++
title = "Self-hosting apps on Kubernetes with OpenTofu"
description = "How I self-hosted a complete suite of apps on Kubernetes using a "
date = "2026-05-30"
draft = true
[taxonomies]
categories = ["Write-up"]
tags = ["Proxmox", "OpenTofu", "Kubernetes", "Self-hosting"]
+++

Like many others, I first began self hosting on Proxmox using [Community Scripts](https://community-scripts.org/scripts).
These scripts were very easy to use: by simply pasting in a curl-bash script, it will automatically set up an app for you, including the complete infra and the software deployment.
But over time, some annoyances surfaced:
- It's **difficult to audit** the scripts.
  While they are open-source, the contents of the scripts aren't laid out in front of you immediately.
  And every time we need to update, if we want to be vigilant, we have to look over the script again in addition to vetting the app itself.
  With the rise of supply-chain attacks, one must be more careful when handling updates, so this is a valid issue if we want to be err on the side of caution.
- There is a lack of **declarative management** and a lack of abstraction between infrastructure and app layers.
  The app hosting LXCs are presented as is, and we can do whatever we want within the containers.
  But this really makes it harder to track the current state of the app deployment.

For these reasons, I decided to move from the simple community script/LXC approach to using **IaC** (infrastructure as Code) with **Kubernetes**.
While it was quite complex to set up at first, eventually it made managing and maintaining the app deployments many times easier.
It even unlocked the possibility of using **AI coding agents** to manage the whole deployment by solving the state management problem.

This post gives a high-level overview of my current Proxmox infrastructure setup using **Talos Linux** to manage Kubernetes and **Kustomize** & **Helm** templates for deploying apps.

## Infra: Talos Linux and Terraform/OpenTofu templates

I first discovered **Talos Linux** during my research on how to provision and deploy Kubernetes workers and control plane nodes.

Talos is an immutable Linux distro by *Sidero Labs* for the sole purpose of running Kubernetes.
As such, by deploying Talos, all of the work of installing Kubernetes has already been done for you.
There's also a CLI tool, `talosctl`, for managing Talos.
We can use this to easily upgrade/downgrade the OS and add plugins to help with virtualization or GPU hardware, and the process will pretty much never break.

But what makes Talos even more useful is that it's very easy to provision using **OpenTofu**.
Sidero provides a [Terraform/OpenTofu template](https://search.opentofu.org/provider/siderolabs/talos/latest) for this.
To set this up, I created a basic Ubuntu LXC for dev purposes on Proxmox and installed the necessary tools to use OpenTofu and Kubernetes tools.
This is generally a good idea if you want to work on the project from multiple computers, just so we don't need to copy the Tofu state files around.
I then connected it up to the Proxmox server using the [bpg/proxmox](https://search.opentofu.org/provider/bpg/proxmox/latest) provider.

To deploy a Kubernetes cluster proper, we need both a **worker** and **control plane** node, so two Talos Linux VMs.
To do this, I created an OpenTofu template declaring the configuration of the worker and the control place.
This provisions two Talos VMs on the Proxmox host, one for the worker and the other for the control plane.
For example, the control plane part of the template looks something like this:

```tf
data "talos_machine_configuration" "controlplane" {
  cluster_name     = var.talos_cluster_name
  cluster_endpoint = local.talos_cluster_endpoint
  machine_type     = "controlplane"
  machine_secrets  = talos_machine_secrets.this.machine_secrets
  talos_version    = var.talos_version
}

data "talos_client_configuration" "this" {
  cluster_name         = var.talos_cluster_name
  client_configuration = talos_machine_secrets.this.client_configuration
  nodes                = [local.controlplane_node_ip]
  endpoints            = [local.talos_cluster_endpoint]
}

resource "talos_machine_configuration_apply" "this" {
  depends_on = [proxmox_virtual_environment_vm.talos]

  node                        = local.controlplane_node_ip
  endpoint                    = local.controlplane_node_ip
  client_configuration        = talos_machine_secrets.this.client_configuration
  machine_configuration_input = data.talos_machine_configuration.controlplane.machine_configuration
  config_patches = [
    yamlencode({
      machine = {
        install = {
          disk = var.talos_install_disk
        }
      }
    })
  ]
}
```

With `tofu apply` and some minutes of waiting, the two VMs spun up and I was able to verify its status by `talosctl stats` and that it shows up in PVE.
It is important to let OpenTofu generate the Talos credentials for you and output a `talosconfig` file so we can manage the Talos VMs later.

## Apps: Kustomize and Helm templates

Now that the basic Kubernetes cluster is healthy, we can now deploy some apps on it.

The simplest way to do this was to create some Kubernetes YAML templates and apply it.
A few things to note however:
- It's very important to have a dedicated **namespace** for each app, so the resources and scope of an app can be easily determined.
- Since a lot of the apps are going to share a very similar software infrastructure (e.g. database), we can factor out the common features into separate deployments.
- We need a dedicated reverse proxy, so we can securely connect to the apps from the outside.
- We also need to mount a disk for **persistent storage**.

### Traefik, Cert-manager

First we need to set up an **ingress controller** or **reverse proxy** for all the apps.
I found that **Traefik** is a pretty good tool for this requirement.

Using its [Helm chart](https://traefik.github.io/charts/) along with additional Kustomize templates, I created a Traefik deployment and have it act as the main ingress control for the cluster.

```
helmCharts:
  - name: traefik
    repo: https://traefik.github.io/charts
    releaseName: traefik
    namespace: traefik
    valuesFile: ../../helm/values/traefik.yaml
```

All inbound connections will go through Traefik, and based on the URL it will route the connection to one of the apps.
This is quite convenient since we only need one such reverse proxy for all the apps.
The DNS configuration is simple as well: just add a [Wildcard DNS record](https://en.wikipedia.org/wiki/Wildcard_DNS_record) pointing to the Talos worker node IP.

Of course we also need to set up SSL so the app connections are secure.
Again there is a good tool for it: **cert-manager**, along with its [Helm chart](https://cert-manager.io/docs/installation/helm/).

```
helmCharts:
  - name: cert-manager
    repo: https://charts.jetstack.io
    releaseName: cert-manager
    namespace: cert-manager
    valuesFile: ../../helm/values/cert-manager.yaml
```

Combined with Traefik, I was able to set up the complete reverse proxy setup with SSL, and we can now connect to the apps over HTTPS via its URL.

### App containers

My core app stacks consist of Immich, Jellyfin and Matrix (Synapse).
Some of them have official **Helm charts** which can be conveniently used, but for those that don't, I chose to write my own **Kustomize** templates for them.

[Immich](https://immich.app/) has its own [Helm chart](https://github.com/immich-app/immich-charts).
We can use this to generate a `workloads.yaml` file, which includes the full Immich microservice architecture with a backend, machine learning and Valkey service.
But for most apps with a Helm chart, an explicit generation process is not required, we can simply use `kubectl kustomize --enable-helm` to render the Helm chart into Kustomize templates automatically.
This downloads the charts and generates the Kustomize templates without storing it locally.

For apps that don't have an official Helm chart such as Synapse, I simply wrote a plain Kustomize YAML and applied it via `kubectl kustomize`.

### CloudNativePG

The apps also require persistent content to be stored in databases.
While we can very easily have each app set up their own database storage, it's better to have a centralized *operator* to manage all of this.

**CloudNativePG** adds a way for apps to provision databases as a resource.
This greatly simplifies database configuration with apps, they now can declare database usage using the `Cluster` resource.

```yaml
apiVersion: v1
kind: PersistentVolumeClaim
metadata:
  name: synapse-media
  namespace: matrix
spec:
  accessModes:
    - ReadWriteOnce
  storageClassName: ""
  volumeName: synapse-media
  resources:
    requests:
      storage: 20Gi
---
apiVersion: postgresql.cnpg.io/v1
kind: Cluster
metadata:
  name: synapse-database
  namespace: matrix
spec:
  instances: 1
  imageName: ghcr.io/cloudnative-pg/postgresql:16.8
  storage:
    size: 10Gi
    pvcTemplate:
      accessModes:
        - ReadWriteOnce
      storageClassName: ""
      volumeName: synapse-database-data
      resources:
        requests:
          storage: 10Gi
  bootstrap:
    initdb:
      database: synapse
      owner: synapse
      secret:
        name: synapse-database-app

```

### Persistent storage

In addition to databases, apps like Jellyfin need to attach a dedicated persistent media library.

If I had a separate NAS server, the best option would be something like setting up an NFS provisioner in Kubernetes.
Since my current storage setup is simply some HDDs mounted on the Proxmox host, the more practical solution was to pass the mounted directories into the Talos VM.
Another alternative would have been to pass in the SATA controller for the drives; this would give better performance but is harder to set up.

I configured the directory passthrough in the Proxmox host, allowing the Talos worker VM to access the drives.
Then, I configured [local path provisioner](https://github.com/rancher/local-path-provisioner) for Kubernetes backed by the drive directory.
This allowed us to point the PV to the media directory, which enabled Jellyfin to access our media files.

```yaml
apiVersion: v1
kind: PersistentVolume
metadata:
  name: jellyfin-media
spec:
  capacity:
    storage: 100Gi
  accessModes:
    - ReadWriteOnce
  persistentVolumeReclaimPolicy: Retain
  storageClassName: ""
  volumeMode: Filesystem
  local:
    path: /var/mnt/media/jellyfin
  nodeAffinity:
    required:
      nodeSelectorTerms:
        - matchExpressions:
            - key: kubernetes.io/hostname
              operator: In
              values:
                - talos-worker-01
  claimRef:
    namespace: jellyfin
    name: jellyfin-media
```

### Nvidia GPU Passthrough

Immich and Jellyfin benefit from a GPU for hardware accelerated video codecs and ML workloads.
My server has an Nvidia GPU, but Talos does not include Nvidia drivers out of the box, it requires an Nvidia driver extension.
This can be configured in the [Talos Linux Image Factory](https://factory.talos.dev), by adding the Nvidia container toolkit and the Nvidia kernel driver.
So I updated the Talos worker VM using `talosctl upgrade --image <url>`, which essentially installed the Nvidia drivers.

Besides configuring the worker, we also needed to set up GPU passthrough on the Proxmox host side.
This is a common process done in many Proxmox VM setups.
After this, the Nvidia GPU showed up in the VM like this with `talosctl get devices --nodes <worker_ip>`:

```
192.168.0.100   hardware    PCIDevice   0000:01:00.0   1         Display controller         VGA compatible controller   NVIDIA Corporation   GA106M [GeForce RTX 3060 Mobile / Max-Q]
192.168.0.100   hardware    PCIDevice   0000:01:00.1   1         Multimedia controller      Audio device                NVIDIA Corporation   GA106 High Definition Audio Controller
```

For multi-computer Kubernetes clusters, to separate deployments that require a GPU or not, we can define a runtime class for Nvidia.

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: nvidia
handler: nvidia
```

Then, for a service that requires an Nvidia GPU,

```yaml
runtimeClassName: nvidia

resources:
  limits:
    nvidia.com/gpu: 1
```

## Conclusion

By provisioning Talos VMs with OpenTofu and managing the apps with Kustomize templates and Helm charts along with several services to simplify the process, I successfully migrated all my app deployments to Kubernetes.
This made it much easier to understand what the infrastructure looks like, by simply reading the various levels of IaC templates, and having Kubernetes makes the deployment more robust and scalable.

Not only this, IaC templates makes it feasible to use **coding agents** to manage our deployment.
While it's certainly not a good idea to use it for production, if you have a good review and backup strategy, coding agents can be used to quickly write templates for new apps.
For example, I used OpenCode with GPT-5.5 to create the Kubernetes templates for Immich, and it was able to do so quickly and accurately with the help of linting tools.
After deployment, the app worked identically as before, and it even managed to perform the database import successfully without intervention.
