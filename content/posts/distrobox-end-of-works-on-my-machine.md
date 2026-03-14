---
title: "The End of 'It Works on My Machine': How Distrobox Saves Your PC!"
date: 2026-03-16T10:00:00-03:00
description: "Learn how to stop breaking your OS with conflicting packages. Use Distrobox to create isolated and perfectly integrated development environments."
cover: /images/covers/distrobox-video.png
readingTime: "5"
katex: false
mermaid: false
draft: false
slug: distrobox-end-of-works-on-my-machine
tags: ['linux', 'devops', 'docker', 'podman', 'distrobox', 'sysadmin', 'tutorial', 'video']
categories: ['infrastructure', 'tutorials', 'linux']
---
Have you ever experienced the frustration of having to install an older version of Python to maintain a legacy project, and then immediately needing the latest version of Node.js for another project, only to see your system packages conflict? 

Your local machine, once clean and sacred, begins to turn into the famous **"it works on my machine"** scenario. Full of broken PPAs, version managers fighting each other, and accumulated junk. 

In this post, I will show you the definitive solution for developers and DevOps engineers: **Distrobox**.

## What is Distrobox?

We use Docker to isolate applications in production. But what about our daily development environment?

Distrobox uses the Podman or Docker you already have installed to create **containers highly integrated with your current system**. The big difference is that, in Distrobox, you "enter" the container and feel like you are on your physical machine. Your bash/zsh configurations, your network, your Home folder files, SSH keys, and even graphical interfaces are already inside, ready for use.

## Practical Use Cases

- **Avoid Conflicts:** Need a pure Ubuntu 20.04 environment while using a Fedora Host? Just create a container, run `apt-get` and install Terraform, Ansible, AWS CLI, etc., without dirtying your base system.
- **Specific Tools:** Need a package that only exists in the Arch User Repository (AUR)? Create an Arch Linux container with a single command.
- **Graphical Apps:** You can run IDEs like VS Code, Lens or browsers from inside the container and export the shortcut directly to the start menu of your physical system!

## Watch the Full Video

If you want to see the step-by-step in practice, take a look at the full video I prepared on the subject:

{{< youtube 5_fiNmpHYNE >}}

## Download the distrobox.ini File

To make it easier, I've made available the `distrobox.ini` configuration file that I use in the class. You can use it as a base to declare your containers and create your infrastructure as code also on your local machine.

**👉 [Click here to download the distrobox.ini file](https://drive.google.com/file/d/14Ws-GPtUygZZ6tiepUwc3kuEDq_uCLmW/view?usp=sharing)**


---

*Did you like the tip? Let me know in the comments of this post or the video how you organize your development environments today!*
