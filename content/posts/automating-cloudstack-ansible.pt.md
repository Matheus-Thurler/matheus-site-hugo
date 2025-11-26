---
title: "Automatizando a Instalação do Apache CloudStack com Ansible"
date: 2025-11-28
description: "Cansado de instalações manuais complexas? Conheça meu projeto open-source que automatiza o deploy completo do Apache CloudStack usando Ansible."
cover: /images/covers/cloudstack-ansible.png
readingTime: "8"
katex: false
mermaid: false
slug: automating-cloudstack-ansible
tags: ['cloudstack', 'ansible', 'automation', 'devops', 'homelab']
categories: ['automation', 'cloud']
---

Se você já tentou instalar o **Apache CloudStack** manualmente, sabe que não é uma tarefa trivial. Configurar o Management Server, banco de dados MySQL, NFS para Primary e Secondary Storage, e baixar os System VM Templates pode levar horas – e um erro pequeno pode comprometer tudo.

Para resolver isso no meu homelab e facilitar a vida de quem quer estudar CloudStack, criei o projeto **[ansible-cloudstack-installer](https://github.com/Matheus-Thurler/ansible-cloudstack-installer)**.

## O Problema: Instalação Manual é Lenta e Propensa a Erros

Uma instalação típica de CloudStack envolve:
1. Configurar repositórios apt/yum
2. Instalar e tunar o MySQL (my.cnf)
3. Configurar exportações NFS
4. Instalar o `cloudstack-management`
5. Configurar o banco de dados (`cloudstack-setup-databases`)
6. Configurar o servidor de gerenciamento (`cloudstack-setup-management`)
7. Baixar e semear (seed) os System VM Templates (que são arquivos grandes)

Repetir isso toda vez que você quer subir um laboratório novo é inviável.

## A Solução: Ansible Playbook

Meu instalador automatiza **todo** esse processo em um único host (All-in-One), perfeito para Homelabs ou ambientes de prova de conceito (PoC).

### O que ele faz?

O playbook configura um servidor Ubuntu 22.04 LTS com:
- ✅ **CloudStack Management Server** (versão 4.22+)
- ✅ **MySQL Server** (configurado e otimizado)
- ✅ **NFS Server** (para Primary e Secondary Storage)
- ✅ **System VM Templates** (KVM, XenServer, ESXi) baixados e instalados
- ✅ **Cloudmonkey CLI** configurado para uso imediato

### Estrutura do Projeto

O projeto é modular, dividido em *roles* para facilitar a manutenção:

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

## Como Usar

### 1. Pré-requisitos

Você vai precisar de uma máquina (física ou virtual) com:
- Ubuntu 22.04 LTS
- 4 vCPUs
- 4GB RAM (mínimo)
- 250GB disco (recomendado para storage)

### 2. Instalação

Primeiro, clone o repositório e instale o Ansible na sua máquina de controle (pode ser o próprio servidor):

```bash
git clone https://github.com/Matheus-Thurler/ansible-cloudstack-installer.git
cd ansible-cloudstack-installer
sudo apt update && sudo apt install -y ansible sshpass
```

### 3. Executando o Playbook

Para uma instalação "All-in-One" com banco de dados local:

```bash
ansible-playbook deploy-cloudstack.yml \
  -i hosts \
  -k \
  -u root \
  -e "mysql_root_password=SuaSenhaRoot mysql_cloud_password=SuaSenhaCloud install_local_db=true"
```

O playbook vai pedir a senha de root SSH e fará todo o resto. Em alguns minutos, você terá o CloudStack rodando!

## Flexibilidade: Suporte a Galera Cluster

Se você está montando um ambiente mais robusto, o instalador também suporta usar um banco de dados externo ou um cluster MariaDB Galera. Basta passar os parâmetros `nodetype` e `db_endpoint`:

```bash
# Exemplo para Master Node
ansible-playbook deploy-cloudstack.yml ... -e "nodetype=master db_endpoint=10.35.10.78"
```

## Contribua!

Este projeto é **Open Source** e está disponível no GitHub. Sinta-se à vontade para abrir Issues, enviar Pull Requests ou sugerir melhorias.

🔗 **Repositório:** [github.com/Matheus-Thurler/ansible-cloudstack-installer](https://github.com/Matheus-Thurler/ansible-cloudstack-installer)

Automatizar a infraestrutura é o primeiro passo para se tornar um engenheiro de cloud eficiente. Espero que este projeto ajude nos seus estudos de CloudStack!
