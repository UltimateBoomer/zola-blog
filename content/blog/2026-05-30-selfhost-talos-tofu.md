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
But over time, several annoyances surfaced.
- It's **difficult to audit** the scripts.
  While they are open-source, the contents of the scripts aren't laid out in front of you immediately.
  And every time we need to update, if we really want to be vigilant, we have to look over the script again in addition to vetting the app itself.
  With the rise of supply-chain attacks, one must be more careful in handling updates, so this is a real and valid issue.
- There is a lack of **declarative infra management**, and I suppose also a lack of abstraction.
  The app hosting LXCs are presented as is, and we can do whatever we want within the containers.
  But this amount of freedom at the same time makes it harder to track the current state of the app deployment.

For these reasons, I decided to move from the simple community script/LXC approach to using a more complex too, **Kubernetes**.
While it was quite complex to set up at first, eventually it made managing and maintaining the app deployments many times easier.

## Infra: Talos OS and Terraform/OpenTofu templates

I first discovered **Talos Linux** during my research on how to provision and deploy Kubernetes workers and control plane nodes.
Talos is a complete immutable Linux distro by Sidero packaged around Kubernetes.
As such, by deploying Talos, all of the work of installing and maintaining Kubernetes has already been done.
Due to the immutable nature, we can easily upgrade/downgrade Talos and add plugins, and the process will pretty much never break.
There's even a `talosctl` CLI tool for managing Talos.

What makes Talos even more useful however is that it's very easy to provision using **OpenTofu**.
To set this up, I first created a basic Ubuntu LXC on Proxmox and installed the necessary tools to use OpenTofu and Kubernetes tools.
I then connected it up to the Proxmox server using the [`bpg/proxmox`](https://search.opentofu.org/provider/bpg/proxmox/latest) provider.
This LXC will become the main base of hosting and maintaining the IaC files for the deployment.

To deploy a Kubernetes cluster proper, we need both a **worker** and **control plane** node.
To do this, I created an OpenTofu template declaring the configuration of the worker and the control place.
This provisions two Talos VMs on the Proxmox host, one for the worker and the other for the control plane.

<!-- ```tf -->
<!-- # Proxmox provider configuration -->
<!-- provider "proxmox" { -->
<!--   endpoint  = var.proxmox_endpoint -->
<!--   api_token = var.proxmox_api_token -->
<!--   insecure  = var.proxmox_insecure -->
<!---->
<!--   ssh { -->
<!--     agent    = true -->
<!--     username = "root" -->
<!--   } -->
<!-- } -->
<!---->
<!-- provider "talos" {} -->
<!---->
<!-- # Download Talos qcow2 image -->
<!-- resource "proxmox_download_file" "talos_image" { -->
<!--   node_name    = var.target_node -->
<!--   datastore_id = var.image_datastore_id -->
<!--   content_type = "import" -->
<!--   file_name    = var.talos_image_file_name -->
<!--   url          = var.talos_image_url -->
<!-- } -->
<!---->
<!-- # Control plane VM -->
<!-- resource "proxmox_virtual_environment_vm" "talos" { -->
<!--   name      = var.vm_name -->
<!--   vm_id     = var.vm_id -->
<!--   node_name = var.target_node -->
<!---->
<!--   cpu { -->
<!--     cores = var.controlplane_cpu_cores -->
<!--     type  = "host" -->
<!--   } -->
<!---->
<!--   memory { -->
<!--     dedicated = var.controlplane_memory_mb -->
<!--   } -->
<!---->
<!--   disk { -->
<!--     datastore_id = var.disk_datastore_id -->
<!--     interface    = "virtio0" -->
<!--     import_from  = proxmox_download_file.talos_image.id -->
<!--     size         = var.controlplane_disk_size_gb -->
<!--   } -->
<!---->
<!--   efi_disk { -->
<!--     datastore_id = var.disk_datastore_id -->
<!--     type         = "4m" -->
<!--   } -->
<!---->
<!--   network_device { -->
<!--     bridge = var.network_bridge -->
<!--     model  = "virtio" -->
<!--   } -->
<!-- } -->
<!---->
<!-- # Worker VM -->
<!-- resource "proxmox_virtual_environment_vm" "worker" { -->
<!--   name      = var.worker_vm_name -->
<!--   vm_id     = var.worker_vm_id -->
<!--   node_name = var.target_node -->
<!---->
<!--   cpu { -->
<!--     cores = var.worker_cpu_cores -->
<!--     type  = "host" -->
<!--   } -->
<!---->
<!--   memory { -->
<!--     dedicated = var.worker_memory_mb -->
<!--   } -->
<!---->
<!--   disk { -->
<!--     datastore_id = var.disk_datastore_id -->
<!--     interface    = "virtio0" -->
<!--     import_from  = proxmox_download_file.talos_image.id -->
<!--     size         = var.worker_disk_size_gb -->
<!--   } -->
<!---->
<!--   efi_disk { -->
<!--     datastore_id = var.disk_datastore_id -->
<!--     type         = "4m" -->
<!--   } -->
<!---->
<!--   network_device { -->
<!--     bridge = var.network_bridge -->
<!--     model  = "virtio" -->
<!--   } -->
<!-- } -->
<!---->
<!-- # Generate Talos machine secrets -->
<!-- resource "talos_machine_secrets" "this" { -->
<!--   talos_version = var.talos_version -->
<!-- } -->
<!---->
<!-- # Apply control plane configuration -->
<!-- resource "talos_machine_configuration_apply" "this" { -->
<!--   depends_on = [proxmox_virtual_environment_vm.talos] -->
<!---->
<!--   node                        = local.controlplane_node_ip -->
<!--   endpoint                    = local.controlplane_node_ip -->
<!--   client_configuration        = talos_machine_secrets.this.client_configuration -->
<!--   machine_configuration_input = data.talos_machine_configuration.controlplane.machine_configuration -->
<!--   config_patches = [ -->
<!--     yamlencode({ -->
<!--       machine = { -->
<!--         install = { -->
<!--           disk = var.talos_install_disk -->
<!--         } -->
<!--       } -->
<!--     }) -->
<!--   ] -->
<!-- } -->
<!---->
<!-- # Bootstrap cluster -->
<!-- resource "talos_machine_bootstrap" "this" { -->
<!--   depends_on = [talos_machine_configuration_apply.this] -->
<!---->
<!--   node                 = local.controlplane_node_ip -->
<!--   client_configuration = talos_machine_secrets.this.client_configuration -->
<!-- } -->
<!---->
<!-- # Apply worker configuration -->
<!-- resource "talos_machine_configuration_apply" "worker" { -->
<!--   depends_on = [ -->
<!--     proxmox_virtual_environment_vm.worker, -->
<!--     talos_machine_bootstrap.this, -->
<!--   ] -->
<!---->
<!--   node                        = local.worker_node_ip -->
<!--   endpoint                    = local.worker_node_ip -->
<!--   client_configuration        = talos_machine_secrets.this.client_configuration -->
<!--   machine_configuration_input = data.talos_machine_configuration.worker.machine_configuration -->
<!--   config_patches = [ -->
<!--     yamlencode({ -->
<!--       machine = { -->
<!--         install = { -->
<!--           disk = var.talos_install_disk -->
<!--         } -->
<!--       } -->
<!--     }) -->
<!--   ] -->
<!-- } -->
<!---->
<!-- # Fetch kubeconfig -->
<!-- resource "talos_cluster_kubeconfig" "this" { -->
<!--   depends_on = [talos_machine_bootstrap.this] -->
<!---->
<!--   node                 = local.controlplane_node_ip -->
<!--   client_configuration = talos_machine_secrets.this.client_configuration -->
<!-- } -->
<!-- ``` -->

With `tofu apply`, the two VMs spun up and I was able to verify its status by `talosctl stats`.
It is important to let OpenTofu generate `talosctl` credentials for you with a `talosconfig` file so that we can directly manage them later.

## Apps: Kustomization and Helm templates

Now that the Kubernetes cluster is healthy, we can now deploy some apps on it.
The simplest way to do this is to create some Kubernetes yaml templates and apply it.
A few things to note however:
- It's very important to have a dedicated **namespace** for each app, so the resources and scope of an app can be easily determined.
- Since a lot of the apps are going to share a very similar software infrastructure (e.g. database), we can factor out the common features into separate deployments.
- We need a dedicated load balancer or reverse proxy, so we can securely connect to the apps from the outside.
- We also need to mount a disk for **persistent storage**.

### Traefik, Cert-manager

First we need to set up an ingress controller / reverse proxy for all the apps.
I found that **Traefik** is a pretty good tool for this task.

Using its [Helm chart](https://traefik.github.io/charts/) along with Kustomize templates, we can set up a Traefik namespace and have it act as the main ingress control for the cluster.
All inbound connections will go through Traefik, and based on the URL it will route the connection to one of the apps.
This is quite convenient since we only need one such reverse proxy for all the apps, and the DNS configuration is simple as well: just add a [Wildcard DNS record](https://en.wikipedia.org/wiki/Wildcard_DNS_record) pointing to the Talos worker node IP.

Of course we also need to set up SSL so the app connections are secure.
Again there is a good tool for it: **cert-manager**, along with its [Helm chart](https://cert-manager.io/docs/installation/helm/).
Combined with Traefik, we can now connect to our apps over HTTPS via its URL.

### App containers

My core app stack consists of Immich, Jellyfin and Matrix (Synapse).
Some of them have official **Helm charts** which can be conveniently used, but for those that don't, I chose to write my own **Kustomize** templates for them.

[Immich](https://immich.app/) has its own [Helm chart](https://github.com/immich-app/immich-charts).
We can use this to generate a `workloads.yaml` file, which includes the full infrastructure required to host Immich's microservice architecture.

### CloudNativePG

The apps of course require persistent content to be stored in databases.
While we can very easily have each app set up their own database storage, it's better to have a centralized *operator* to manage this resource.

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

In addition to database, some apps like Jellyfin need our media library or to store media files.

If I had a separate NAS server, it would be very easy to set up an NFS share.
Since my current storage setup is simply some HDDs mounted on the Proxmox host, the practical solution was to pass the directories into the Talos VM.

The directory passthrough can be configured in Proxmox host.
Then, we can set up a [local path provisioner](https://github.com/rancher/local-path-provisioner) backed by the directory.
This allows us to dedicate a specific place in the HDD to store our media files.

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
My server has an Nvidia GPU, but Talos does not support Nvidia out of the box, it requires an Nvidia driver extension.
This can be configured in the [Talos Linux Image Factory](https://factory.talos.dev), by adding the Nvidia container toolkit and the Nvidia kernel driver.
Then, update the Talos worker VM using `talosctl upgrade --image <url>`.

Besides configuring the Talos worker VM, we'll also need to setup GPU passthrough on the Proxmox host side.
After this is done, the GPU will be available in the VM.

To separate the deployments that require a GPU or not, which can be useful for Kubernetes clusters, we can define a runtime class for Nvidia.

```yaml
apiVersion: node.k8s.io/v1
kind: RuntimeClass
metadata:
  name: nvidia
handler: nvidia
```

Then, in a service Helm chart which requires an Nvidia GPU,

```yaml
runtimeClassName: nvidia

resources:
  limits:
    nvidia.com/gpu: 1
```

### Monitoring

We can also add a monitoring stack to collect various runtime metrics and alert on abnormalities.

Beginning with Prometheus, 

## Conclusion

By provisioning Talos VMs with Tofu and managing the apps with Kustomize templates and Helm charts along with several services to simplify the process, I successfully migrated all my app deployments to Kubernetes.
This makes it much easier to understand what the infrastructure looks like by simply reading the various levels of IaC templates, and having Kubernetes makes the deployment more robust and scalable.
It was also nice ditching the community scripts, which while were very easy to use and good enough for simple self-hosting purposes, moving to Kubernetes has taught me how to manage my own deployment stack.
