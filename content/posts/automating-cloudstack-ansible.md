---
title: "Automating Apache CloudStack Installation with Ansible"
date: 2025-11-28
description: "Tired of complex manual installations? Meet my open-source project that automates the complete deployment of Apache CloudStack using Ansible."
cover: /images/covers/cloudstack-ansible.png
readingTime: "8"
katex: false
mermaid: false
tags: ['cloudstack', 'ansible', 'automation', 'devops', 'homelab']
slug: automating-cloudstack-ansible
categories: ['automation', 'cloud']
---

If you've ever tried to install **Apache CloudStack** manually, you know it's not a trivial task. Configuring the Management Server, MySQL database, NFS for Primary and Secondary Storage, and downloading System VM Templates can take hours – and a small mistake can compromise everything.

To solve this in my homelab and make life easier for those who want to study CloudStack, I created the project **[ansible-cloudstack-installer](https://github.com/Matheus-Thurler/ansible-cloudstack-installer)**.

## The Problem: Manual Installation is Slow and Error-Prone

A typical CloudStack installation involves:
1. Configuring apt/yum repositories
2. Installing and tuning MySQL (my.cnf)
3. Configuring NFS exports
4. Installing `cloudstack-management`
5. Configuring the database (`cloudstack-setup-databases`)
6. Configuring the management server (`cloudstack-setup-management`)
7. Downloading and seeding System VM Templates (which are large files)

Repeating this every time you want to spin up a new lab is unfeasible.

## The Solution: Ansible Playbook

My installer automates **this entire** process on a single host (All-in-One), perfect for Homelabs or Proof of Concept (PoC) environments.

### What does it do?

The playbook configures an Ubuntu 22.04 LTS server with:
- ✅ **CloudStack Management Server** (version 4.22+)
- ✅ **MySQL Server** (configured and optimized)
- ✅ **NFS Server** (for Primary and Secondary Storage)
- ✅ **System VM Templates** (KVM, XenServer, ESXi) downloaded and installed
- ✅ **Cloudmonkey CLI** configured for immediate use

### Project Structure

The project is modular, divided into *roles* for easier maintenance:

```yaml
- name: Cloudstack Management Server Deployment
  hosts: acs-manager
  roles:
    - role: mysql
      when: install_local_db | default(false) | bool
    - nfs-server
    - cloudstack-manager
    - cloudmonkey
```

## How to Use

### 1. Prerequisites

You will need a machine (physical or virtual) with:
- Ubuntu 22.04 LTS
- 4 vCPUs
- 4GB RAM (minimum)
- 250GB disk (recommended for storage)

### 2. Installation

First, clone the repository and install Ansible on your control machine (can be the server itself):

```bash
git clone https://github.com/Matheus-Thurler/ansible-cloudstack-installer.git
cd ansible-cloudstack-installer
sudo apt update && sudo apt install -y ansible sshpass
```

### 3. Running the Playbook

For an "All-in-One" installation with local database:

```bash
ansible-playbook deploy-cloudstack.yml \
  -i hosts \
  -k \
  -u root \
  -e "mysql_root_password=YourRootPass mysql_cloud_password=YourCloudPass install_local_db=true"
```

The playbook will ask for the SSH root password and do the rest. In a few minutes, you will have CloudStack running!

## Flexibility: Galera Cluster Support

If you are setting up a more robust environment, the installer also supports using an external database or a MariaDB Galera cluster. Just pass the `nodetype` and `db_endpoint` parameters:

```bash
# Example for Master Node
ansible-playbook deploy-cloudstack.yml ... -e "nodetype=master db_endpoint=10.35.10.78"
```

## Contribute!

This project is **Open Source** and available on GitHub. Feel free to open Issues, submit Pull Requests, or suggest improvements.

🔗 **Repository:** [github.com/Matheus-Thurler/ansible-cloudstack-installer](https://github.com/Matheus-Thurler/ansible-cloudstack-installer)

Automating infrastructure is the first step to becoming an efficient cloud engineer. I hope this project helps in your CloudStack studies!
