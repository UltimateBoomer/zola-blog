+++
title = "About me"
description = ""
path = "about"
[extra]
toc = false
comment = false
+++

My name is Steven Cao.
I'm a fourth-year Computer Science student at the University of Waterloo specializing in AI and optimization, with a passion for building software that makes a real impact.

## Résumé

For a detailed overview of my education, experience, projects, and technical skills, <a href="/resume.pdf" download>download my resume (PDF)</a>.

## Experience

I've had the opportunity to work across various tech stacks in my co-ops:

- **Software Engineer at Pinterest**, where I worked on the Metric Quality team overseeing Android, iOS, and Web clients. I deployed a domain-specific code generator for type-safe constants, optimized Android impression batching, and built tooling to track DSL key usage across repositories.
- **AI Developer at Rocscience**, where I containerized Windows geotechnical software for on-demand Linux execution through an MCP server and developed AWS ECS infrastructure backed by Go, Redis, and PostgreSQL.
- **Mobile Developer at Compass Digital**, where I developed Flutter food-ordering apps, built meal plan ordering workflows, and integrated Google Pay / Apple Pay on Web.
- **Android Platform Software Developer at Ford**, where I built driver-assist features for next-generation infotainment systems, including real-time C++20 hardware-abstraction services and Android interfaces written in Kotlin and Java.
- **Web Developer at Caribou Contests**, where I managed an online mathematics competition platform serving 50,000 K–12 students worldwide.

## Projects

### Applications and infrastructure

- **Pixiverse** is a multiplayer productivity-tracker game built with Godot and Nakama.
- **Jonsole** is a hardware project for the Jonsole desktop console. I wrote ESP32 firmware using FreeRTOS, along with a Tauri desktop app which enables connecting the hardware to CLI coding agents on a computer by bluetooth.
- **Proxmox Server** is my self-hosted infrastructure for DNS, media streaming, file synchronization, game servers, Kubernetes workloads, and CUDA-accelerated local LLMs.

### Hackathon projects

- **[BailMeOut](https://github.com/cxc-2026-waterlose/BailMeOut)**, from CXC 2026, is a personal safety app built with React Native and Expo. It uses ElevenLabs for real-time transcription and Gemini for context analysis, triggering a simulated incoming call when it detects a threat or custom trigger word.

### Machine learning

- **[Attention-DQN RPS Agent](https://github.com/UltimateBoomer/attn-dqn-rps-agent)** is a RL model for repeated Rock–Paper–Scissors against a fixed pool of opponents. It uses multi-head attention to learn patterns in action histories and a Deep Q-Network with prioritized experience replay to adapt to a set of opponent strategies.

### Mathematical visualization

- **Simple Fractal Viewer** is a C++ and OpenGL application that renders Mandelbrot sets in real time using GPU shaders, with interactive navigation.
- **Penrose Tile Generator** creates mathematical art in Python by recursively subdividing shapes into Penrose tilings.

### Developer tools and language projects

- **Vm** is a Vim-like terminal text editor written in modern C++ following functional programming concepts, with motions, editing commands, search, and undo/redo support.
- **Ruse Interpreter** is a full-stack implementation of a custom Lisp-inspired language, with a Spring Boot execution API and React code editor.

### Rust terminal games

- **Wordle-Rust** is a terminal Wordle implementation with colored feedback, dictionary validation, and configurable word lists.
- **Rust-Sweeper** is a customizable terminal Minesweeper game with Vim-style keyboard navigation.

### Minecraft mods

- **Smooth Boot** is a Minecraft performance mod that optimizes thread counts and priorities during startup.
- **Low Fire** reduces the obstruction and opacity of Minecraft's on-screen fire overlay.
- **TexTweaks** provides texture scaling, enhanced mipmap generation, and configurable LOD bias for high-resolution Minecraft resource packs.
- **ResolutionControl+** adds custom internal resolution scaling to Minecraft for performance tuning and improved visuals.
