+++
title = "Self-hosting a blog site"
description = "How I self-hosted my website on my own hardware"
date = "2025-08-12"
[taxonomies]
categories = ["Write-up", "Tutorial"]
tags = ["Self-hosting", "Proxmox", "Caddy", "Cloudflare", "Zola"]
+++

Hosting a static site nowadays is almost too easy with all the hosting services available from Cloudflare, GitHub, Vercel, etc.

For a challenge, I decided to host my blog site on my own hardware using a **Caddy** server.
To ensure the security and reliability of the site, I used the **Cloudflare Zero Trust** service to tunnel the site to a public endpoint, ensuring that my server does not need open ports as well as having all the benefits of Cloudflare services.

Here is how you can replicate my setup.

If you want to follow along, this guide assumes you have **basic to intermediate Linux knowledge**, including how to install a typical Linux distro, how the operating system works, and command line usage (writing scripts, manipulating files, network configuration).
You'll also need a **domain name** and a piece of **hardware** for the server.

Let's begin!

## Setting Up the Site Repository

The first step is to create a public Git repository for the site.

If you already have a repo set up such as for GitHub Pages, then we're good to go.
Otherwise, pick a static site generator and create a new repo based on a template.

Personally I chose [Zola](https://www.getzola.org/) for my blog with the [Linkita](https://salif.github.io/linkita/en/) theme, which allows me to write blog posts in Markdown and generate a static site.

The choice of a static site generator and theme doesn't really matter too much, as long as it can generate static site files which we can serve with a web server.

{% admonition(type="info", title="Base URL") %}
Be sure to set the **base URL** of the site to the domain you will be hosting to in the config file of your static site generator!
Otherwise, navigation links will not work correctly.

In the case of Zola, this can be done with a line in `config.toml`:
```toml
base_url = "https://yourdomain.com"
```
{% end %}

## Automatically Building the Site

Once the repository is set up and you have a buildable website, we can now set up GitHub Actions (or any other CI/CD service) to automatically build our site into static files suitable for hosting.

Of course, this process can be done on our server.
However, this step eliminates the need to install build tools on our server, and allows our server to function independently of the static site generator we are using.

In `.github/workflows/build.yml`, set up a workflow to create a zip file containing the generated files.
Here is an example which I'm using to build my Zola sitelinks on your site will not work correctly.
```yaml
name: Build and Deploy Zola Site

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]
  workflow_dispatch:

jobs:
  build:
    name: Build Zola Site
    runs-on: ubuntu-latest

    steps:
      - name: Checkout repository
        uses: actions/checkout@v4
        with:
          submodules: true
          fetch-depth: 0

      - name: Setup Zola
        uses: taiki-e/install-action@v2
        with:
          tool: zola@0.21.0

      - name: Build site
        run: zola build

      - name: Upload build artifacts
        uses: actions/upload-artifact@v4
        with:
          name: zola-site
          path: public/
          retention-days: 30
```
The idea is to:
1. Checkout the repo
2. Build the site using the static site generator's build tool
3. Upload the output files as an artifact.

To test this, push a commit to the main branch and watch for the green checkmark, then verify that there is an artifact available for download in the Actions tab.

{% admonition(type="info", title="Other ways to build") %}
If you want a more pure self-hosted solution for building the site, you can alternatively set up a [**self-hosted runner**](https://docs.github.com/en/actions/concepts/runners/self-hosted-runners?learn=hosting_your_own_runners).
I'll investigate more about this method in the future.

Or, if you don't care about additional dependencies on the server, you can simply build the site on the server and deploy it directly.
{% end %}

## Proxmox Server Setup

To host the site on our own hardware, we'll need to install **Proxmox**.

Proxmox VE is a well-known open source platform based on **Debian** that comes with a web interface for managing VMs and containers, and is great for self-hosting and used in many modern datacenters.

Download a Proxmox VE installer ISO from the [Proxmox website](https://www.proxmox.com/en/downloads) and install it on your hardware following their install instructions.

After Proxmox is installed, we'll then install these two containers:
- [**Caddy**](https://community-scripts.github.io/ProxmoxVE/scripts?id=caddy): a simple web server for hosting the static site files
- [**Cloudflared**](https://community-scripts.github.io/ProxmoxVE/scripts?id=cloudflared): Cloudflare's tool for tunneling the site through Cloudflare Zero Trust (more on this later)

Linked are the corresponding Proxmox community install scripts.
Run them on the Proxmox host, which will automatically install and configure the containers for us.

Make sure to set a static IP address for at least the Caddy container, it will make accessing and the routing setup we do later easier.

## Downloading and Hosting the Site

Now that we have the Proxmox server set up, we'll download the latest artifact from GitHub Actions on our server.
If you're using other CI/CD services, this process should be similar.

To give our container access to the artifacts, create a **fine-grained GitHub token** with **read-only Actions** permission for our container to access and download the GitHub Actions artifacts.

After this is done, save the token to a file on our Caddy container at `/root/.github-token`.
Since this token has read-only permission on an already public resource, it should safe to just store it as is on the server.

We'll then write a script to download the site files from GitHub Actions.
```bash
#!/bin/bash

# Load GitHub token from file
GITHUB_TOKEN=$(cat /root/.github-token)

# Config: edit these values for your repo
GITHUB_USER="<user>"
REPO="zola-blog"
ARTIFACT_NAME="zola-site"
ARTIFACT_ID_FILE=".last_artifact_id"
WEBROOT="/var/www/html"

# Get latest successful workflow run ID for main branch
RUN_ID=$(curl -s \
  "https://api.github.com/repos/$GITHUB_USER/$REPO/actions/runs?status=success&branch=main" \
  | jq '.workflow_runs[0].id')

# Get artifact ID for 'zola-site'
ARTIFACT_ID=$(curl -s \
  "https://api.github.com/repos/$GITHUB_USER/$REPO/actions/runs/$RUN_ID/artifacts" \
  | jq ".artifacts[] | select(.name==\"$ARTIFACT_NAME\") | .id")

# Check if artifact ID has changed
if [[ -f "$ARTIFACT_ID_FILE" ]] && [[ "$(cat $ARTIFACT_ID_FILE)" == "$ARTIFACT_ID" ]]; then
  echo "Artifact has not changed. Skipping download and deployment."
  exit 0
fi

# Download artifact zip (token required)
curl -L -H "Authorization: token $GITHUB_TOKEN" \
  -o artifact.zip \
  "https://api.github.com/repos/$GITHUB_USER/$REPO/actions/artifacts/$ARTIFACT_ID/zip"

# Extract and write to web root
unzip -o artifact.zip -d /tmp/zola-site
rm -rf "$WEBROOT"/*
cp -r /tmp/zola-site/* "$WEBROOT"/
rm -rf /tmp/zola-site artifact.zip

# Save the latest artifact ID
echo "$ARTIFACT_ID" > "$ARTIFACT_ID_FILE"
```
Save the script as `/root/deploy-site.sh` and make it executable.
Also ensure the tools `curl`, `jq`, and `unzip` are installed.

If the token is set up correctly and there is an artifact available, this script will download the latest site files and extract them to the web root directory, effectively deploying the site.
Running it again will redeploy the site if a new artifact is available.

Make sure to also point Caddy to the webroot (`/var/www/html`) by editing the Caddyfile at `/etc/caddy/Caddyfile` in the container:
```
:80 {
    root * /var/www/html
    file_server
}
```
Now test the site by connecting to the Caddy container's IP address in the browser.

Congratulations! You now have a self-hosted blog site running on your Proxmox server.
Now we need to securely expose the site to the internet.

## Cloudflare Tunnel

The **Cloudflared** container we installed earlier will allow us to host the site without exposing any of our local network's ports.
This is good as it reduces the attack surface of our setup, and doesn't require any configuration on the router.

First sign in to **Cloudflare** and set up **Cloudflare Zero Trust** listed in the left panel.
The free plan should sufficient for our purposes.

After this is done, in Cloudflare Zero Trust, go to **Networks>Tunnels** and create a new tunnel.
Select the **Cloudflared** tunnel type and name it whatever you want.

Then, run the following command in the Cloudflared container to set up the tunnel:
```bash
cloudflared service install <Tunnel ID>
```
where the tunnel ID is provided by Cloudflare.

Continuing on the tunnel setup page, enter your domain name as the hostname and the private IP address of the Caddy container as the server address.

Once this is complete, and all containers are properly running, your site should be up at your domain name!

{% admonition(type="tip", title="Cloudflare caching") %}
We can significantly reduce the amount of traffic to our server by enabling **Cloudflare caching**.

To do this, go to **Caching>Configuration** in the Cloudflare dashboard, and add the rule "cache everything".

This may introduce some delays when you update your site, but I haven't tested the effects rigorously yet.
{% end %}

## Auto-Updating the Site

If you want your site to automatically update whenever you push to the main branch, you can simply run the downloader script periodically by configuring it as a systemd service.

First, create the systemd sevice at `/etc/systemd/system/site-deploy.service` in the Caddy container:
```conf
[Unit]
Description=Deploy site

[Service]
Type=oneshot
ExecStart=/root/deploy-site.sh
WorkingDirectory=/root
```

Then, set up a timer to run the service periodically, say every 15 minutes.
Write this to `/etc/systemd/system/site-deploy.timer`:
```conf
[Unit]
Description=Periodically deploy site artifact

[Timer]
OnUnitActiveSec=15min

[Install]
WantedBy=timers.target
```
Adjust the timing as necessary, and enable the timer by
```bash
systemctl daemon-reload
systemctl enable site-deploy.timer
```
Now, the site will automatically update with the latest artifact from GitHub Actions.

## Conclusion

We have set up a self-hosted website running on our own Proxmox server, using a Caddy container to serve the static site files, and a Cloudflared container to route the site via a Cloudflare tunnel.
The contents of the site are built using Github Actions, and the site itself should be up and running at our domain name.

I hope you found this write-up useful!
If you have any questions, feel free to leave a comment or check out the documentation on the tools and services used in this setup:
- [Proxmox](https://pve.proxmox.com/wiki/Main_Page)
- [Caddy](https://caddyserver.com/docs/)
- [Github Actions](https://docs.github.com/en/actions)
- [Cloudflare](https://developers.cloudflare.com/)
