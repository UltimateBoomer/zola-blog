+++
title = "My Rocscience co-op project. Part 1: Turning Linux into Windows"
description = "How I built an entire container architecture for running Rocscience software on ECS"
date = "2025-08-15"
[taxonomies]
categories = ["Write-up"]
tags = ["Linux", "Docker", "Cloud", "AWS", "ECS", "Wine"]
+++

Between January to April 2026, I had the opportunity to work as a software developer in AI platform at Rocscience, a company in Toronto that develops advanced geotechnical engineering software.

During my time there, I was tasked with building a container architecture for running their software on ECS.
The goal was to enhance their RSInsight platform, allowing users to access their licensed software through a chat interface, without requiring them to install or run anything on their local computers.

The agentic chat interface, *RSInsight*, already exists in a relatively mature form that can connect to a user's computer with Rocscience software installed and interact with it remotely via MCP.
The main focus of my project was to build the cloud infrastructure that would allow it to run Rocscience software in a containerized environment on AWS, essentially moving the "compute" from the user's local machine to the cloud.
And ideally, the solution should be scalable, have low per-user cost, and start up quickly without excessive latency.
Additionally, we want to supports these two features:
- User can upload project files to the container
- Rocscience Software running within the container can be monitored and audited

At first glance, this might sound like an impossible task: while Rocscience software (e.g. RS2, RSPile, etc.) have existing MCP server support, they are **Windows-only**. 
How would it be possible to containerize them and run them on a primarily Linux-based platform, let alone in a lightweight Docker/ECS container?

In this blog post, I will share the architecture I designed and implemented and how I ultimately solved the containerization problem.
Note that I've simplified or changed several details to make the architecture easier to understand and to not not give away any proprietary information, but the main ideas are all still present.

## Dockerizing Rocscience software

### Issues with Windows containers

At first, I researched about Windows containers.
I discovered two main options: using a full Windows [Server](https://hub.docker.com/r/microsoft/windows-server) image, or using the lighter Windows [NanoServer](https://hub.docker.com/r/microsoft/windows-nanoserver) image.

The full Windows server image should work, but it is quite heavy for a single container ([~5 GB!](https://github.com/microsoft/Windows-Containers/issues/584)).
I turned to the Nanoserver image, which is much lighter, but it turned out that it does not support a graphical environment, meaning the software never even starts up.

Further, Windows container are generally not well supported on cloud platforms, and they have an additional non-trivial cost associated with Windows licenses.
Because of this, I realized that Windows containers are likely not a viable path for this project, and I need to find a way to run the software in a Linux container instead.

### Linux containers with Wine

[Wine](https://www.winehq.org/) is a compatibility layer that allows Windows applications to run on Unix-like operating systems.
It is popular tool that has been used and tested extensively in Linux gaming, meaning that nowadays it is very mature, performant, and compatible with a wide range of Windows applications.
Personally, I have been using [Proton](https://github.com/ValveSoftware/Proton) (based on Wine) for a while now to play Steam games on Linux, and it has been pretty much perfect for the majority of singleplayer games.

Recently, with the introduction of [NTSync in Wine](https://gitlab.winehq.org/wine/wine/-/merge_requests/7226) along with kernel driver merged in [Linux kernel 6.14](https://www.phoronix.com/news/Linux-6.14-NTSYNC-Driver-Ready), Wine has received a significant performance boost in multi-threaded applications. 

Upon discovering this, I figured this is perfect timing to try out Wine for containerizing Rocscience software, which are all compute-intensive applications that leverage multiple threads and are likely to be previously bottlenecked by its used of Windows synchronization primitives.

### Installing the software

Getting Rocscience software installed with Wine on Ubuntu WSL was fairly straightforward.
All I had to do was set up a *Wine prefix*, then run the installer in the prefix.
The good thing with WSL is that it has a graphical environment already with WSLg, so I could easily install the software with its intended install GUI just like Windows.
With this, the software has been installed on the Wine prefix, which is essentially a self-contained Windows install that contains all the necessary files, registry entries, and configurations for running the software.

The software ran just fine on the WSLg desktop, and I verified that the built-in Python server used for scripting and MCP works as expected.
What's more, the Windows MCP servers that connect to each software works perfectly too on Wine, and can even launch the software.
This would become the basis for the container architecture, which I will discuss in the next part.

### Moving to Docker: Webtop

The next step was to automate the installation process and create a Docker image that can be later be deployed on ECS.

First, I found that software installation can be automated by Bash script with the silent-install ISS file which Rocscience publicly provides.
Due to the large size of the software install and the frequency of updates, it was not ideal to include the installed software in the base image.
I decided to decouple the Wine prefix data from the Docker image and attach it has a volume instead, so the image can be reused and the prefix data can be easily updated without rebuilding the image.

Regarding the base image, there are many ways to run a contained X11 graphical environment with Wine.
An existing solution which I thought had the most promise as a starting point was [Webtop by LinuxServer](https://docs.linuxserver.io/images/docker-webtop/).
This particular Docker image provides a full desktop environment with [Selkies](https://selkies-project.github.io/selkies/), another incredible software that provides remote desktop accessible through browser.

Using the Webtop image, I created two Docker images: one for building the Wine prefix locally or in some CI/CD step, and the other for running the actual software with the prefix attached as a volume.

## Controlling and securing the containers

Now that we could run the software in a container, the next step was to connect the container to the existing RSInsight cloud architecture.

More details on the complete architecture will be shared in the next part, but the core idea is that the container needs a way to communicate with the backend server bidirectionally.
This required a separate **controller** software that can manage the lifecycle of the task and provide an interface for the backend to send commands to the container.

Moreover, the security of the container has been a big concern.
The main clients of RSInsight are engineering firms that likely have strict security requirements, and the Rocscience software themselves are licensed and proprietary.
We certainly don't want to leak the source code to the users!

Therefore, it was crucial to ensure that the container is secure and does not expose any vulnerabilities or attack surfaces to the users.
In particular, the user should only have access to the software running in the container from the MCP tool calls, and not the underlying system or other containers.
We don't want users to have unrestricted access to the container or the underlying host machine.

### The controller, dual-container architecture

Faced with these constraints, I realized that as a defense-in-depth measure, the controller should run in a separate sidecar container alongside the main Wine/desktop container.
The controller would receive commands from backend and communicate with a desktop connector on the desktop container, which then deploys the MCP servers to launch the software and send commands to it.

We already have such as desktop connector as an Electron app, which was originally intended to be run on user's computers to connect the locally-run MCP server to RSInsight.
I modified the connector and decoupled the MCP connection from the graphical Electron frontend.
What remains is a Websocket client that initializes the MCP connection to RSInsight backend and provides an interface for dispatching commands to the software.

Within the containers, I leveraged Linux's user-based access control to restrict the permissions of the controller and desktop connector, making the Rocscience software and MCP servers run as a regular user with limited permissions.

### Moving to Wayland (labwc)

While I was thing about the security of the container, I realized that X11's security model is also not ideal for our use case.
Any process can trivially capture the screen or send input events to other applications, which could be a potential attack vector as the user does technically have access to the X11 socket in the desktop container for the software to display its GUI.
Because of this, I explored some other options for the graphical environment.

[Labwc](https://labwc.github.io/) stood out to me as a lightweight Wayland compositor that can provide a more secure graphical environment.
It has already been used in Raspberry Pi's OS, and its codebase is minimal and efficient.
So, I converted the Docker images to use Labwc instead of the original X11-based desktop environment.
LinuxServer's **baseimage-selkies** image, which the Webtop image is based on actually has an option to use Wayland with Labwc, so I was able to just use that and modify it to fit our needs.

The result is that the software now runs in a Wayland session with Labwc, which provides better isolation and security for the applications running in the container.
Wine also recently added support for running natively in Wayland, so I flipped on the Wayland support in Wine and it works just fine, and it was likely even more efficient than running in X11 previously.

### User workspace and video recording

This architecture made it easy to solve the two features mentioned at the beginning.
Users can upload files to S3 by presigned URL which controller then download to a task shared volume.
We can audit the software and tool call usage by monitoring the MCP server logs on CloudWatch.

Another feature I implemented was video recording of the desktop environment, after I moved the container to Labwc.
I used [wf-recorder](https://github.com/ammen99/wf-recorder) to record the Wayland session while the RSInsight agent is running, and upload the recording to S3 for users to view later.
This gave significant transparency to users about what is happening in the container, and also provided a way to debug any issues that may arise in runtime.

## The result

Overall, the project was a success and I was able to build and demo a container architecture that can run Rocscience software on ECS with Wine.
All of this was achieved within a 4-month co-op term, thanks to all the incredible open-source software that I was able to leverage.
As the open-source software continues to improve, especially with the recent advancements in Wine's performance and compatibility, I anticipate this architecture will be be further optimized in the future.

In the next part, I will explore the complete architecture in more detail, including my key decisions in how the container connects to the existing RSInsight backend, how the chat interface interacts with the software running in the container, and how the entire infrastructure is deployed and managed on AWS.
