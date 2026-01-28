---
title: "How to Install Apache CloudStack with Ansible - Video Tutorial"
date: 2026-01-28
description: "Learn how to install and configure Apache CloudStack from scratch using Ansible in a complete video tutorial. Automate your entire homelab cloud infrastructure."
cover: /images/covers/cloudstack-ansible-video.png
readingTime: "5"
katex: false
mermaid: false
draft: false
slug: cloudstack-ansible-video-tutorial
tags: ['cloudstack', 'ansible', 'automation', 'video', 'homelab', 'tutorial']
categories: ['automation', 'cloud', 'tutorials']
---

If you want to learn how to install **Apache CloudStack** in an automated way using **Ansible**, I've prepared a complete video tutorial showing the entire process step by step.

## What you will learn

In this video tutorial, I demonstrate in practice how to:

- 🚀 Set up the environment for CloudStack installation
- ⚙️ Use Ansible to automate the entire installation
- 🗄️ Configure MySQL Server for CloudStack
- 📦 Configure NFS for Primary and Secondary Storage
- 🖥️ Install and configure the Management Server
- 🔧 Download and configure System VM Templates
- ✅ Validate the installation and access the web interface
- ☸️ **Live Demo:** Install a Kubernetes cluster using CloudStack CKS

## Why automate with Ansible?

Manual CloudStack installation is a complex process that can take hours and is prone to errors. With Ansible, you can:

- ✅ **Reproduce** the installation as many times as needed
- ✅ **Ensure** consistency across environments
- ✅ **Save time** with complete automation
- ✅ **Version** your infrastructure as code
- ✅ **Document** the installation process

## About the Ansible Project

The automation project I use in the video is available as **open-source** on GitHub:

🔗 **[ansible-cloudstack](https://github.com/Matheus-Thurler/ansible-cloudstack)**

It was developed to simplify CloudStack installation in homelab and PoC environments, automatically configuring:

- **CloudStack Management Server** (version 4.22+)
- **Optimized MySQL Server**
- **NFS Server** for storage
- **System VM Templates** for KVM, XenServer, and ESXi
- **Cloudmonkey CLI** for command-line management

## Watch the Tutorial

{{< youtube joP5JzS9Bro >}}

*Don't forget to like, comment, and subscribe to the channel for more content about DevOps, Cloud, and Homelab!*

## Environment Requirements

To follow the tutorial, you will need:

- **Operating System:** Rocky Linux 9 (tested and recommended)
  - *Note:* Roles for Debian/Ubuntu also exist, but have not been fully tested yet
- **CPU:** 4 vCPUs (minimum) - *In the video I use 8 vCPUs for the Kubernetes demo*
- **Memory:** 8GB RAM (recommended)
- **Disk:** 250GB (recommended for storage)
- **Ansible:** Version 2.10+

## Demo: Kubernetes on CloudStack

One of the most interesting parts of the video is the demonstration of how to install a **Kubernetes cluster** directly using CloudStack CKS (CloudStack Kubernetes Service).

For this, I use the official Kubernetes v1.33.1 ISO with Calico:

🔗 **[setup-v1.33.1-calico-x86_64.iso](https://download.cloudstack.org/cks/setup-v1.33.1-calico-x86_64.iso)**

With CloudStack configured, you can create complete Kubernetes clusters with just a few clicks, leveraging the full power of your private cloud infrastructure!

## Quick Installation

If you're already familiar with Ansible, here's the basic command for installation:

```bash
# Clone the repository
git clone https://github.com/Matheus-Thurler/ansible-cloudstack.git
cd ansible-cloudstack

# Run the playbook
ansible-playbook -i inventory ./cloudstack-install.yml
```

## Next Steps

After watching the video and installing CloudStack, you can:

1. **Configure a Zone** to start creating VMs
2. **Add KVM hosts** for compute
3. **Configure networks** with VLANs (optional)
4. **Create custom VM templates**
5. **Integrate with Terraform** for complete IaC

## Additional Resources

- 📖 [Official CloudStack Documentation](https://docs.cloudstack.apache.org/)
- 💻 [Ansible Installer Repository](https://github.com/Matheus-Thurler/ansible-cloudstack)
- 🏠 [My Homelab Setup]({{< ref "about-my-homelab" >}})

## Contribute!

The project is **Open Source** and accepts contributions. If you find any issues or have suggestions for improvements:

- 🐛 Open an **Issue** on GitHub
- 🔧 Submit a **Pull Request** with improvements
- 💬 Share your experiences in the video comments

---

I hope this tutorial helps you get started with Apache CloudStack! If you have any questions, leave them in the video comments or open an issue on the repository.

**Happy Clouding! ☁️**
