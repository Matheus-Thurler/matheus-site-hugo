---
title: "Criei o VirtFoundry: operator Kubernetes rumo ao CNCF Sandbox"
date: 2026-09-04
description: "Eu criei o VirtFoundry — operator + CRDs + UI para nuvem privada no KubeVirt. Arquitetura, o que já funciona, comparação honesta e o caminho até o CNCF Sandbox."
cover: /images/covers/virtfoundry-logo-card.png
readingTime: "12"
katex: false
mermaid: false
draft: false
slug: leaving-proxmox-kubernetes-native-private-cloud
tags: ['kubernetes', 'kubevirt', 'virtfoundry', 'homelab', 'iaas', 'gitops', 'operator', 'cncf', 'proxmox']
categories: ['kubernetes', 'homelab']
---

**Eu criei o [VirtFoundry](https://github.com/virtfoundry).** É um **operator Kubernetes** — CRDs `virtfoundry.io` — que transforma um cluster que você já opera em nuvem privada multi-tenant: tenant, VPC, VM, volume, snapshot, IAM, API REST e UI.

O hypervisor é o [KubeVirt](https://kubevirt.io/). A fonte da verdade não é MySQL: é o próprio Kubernetes. O destino do projeto é **candidatar ao [CNCF Sandbox](https://github.com/cncf/sandbox)**.

Ainda **não** é um projeto da CNCF. Estamos construindo operator, charts, provider Terraform e comunidade para submeter quando o repositório completar a maturidade mínima — não antes.

![Lista de VMs no VirtFoundry](/images/covers/virtfoundry-ui-vms.png)

## O problema que eu queria resolver

Se você já opera Kubernetes e ainda precisa de VMs, as opções reais costumam ser:

1. **Um segundo silo** — Proxmox (ou similar) ao lado do cluster. Dois backups, duas redes, duas fontes da verdade.
2. **YAML cru do KubeVirt** — excelente hypervisor API, péssimo produto de nuvem privada. Cada tenant vira um exercício de `VirtualMachine`, NAD, PVC e RBAC na mão.
3. **OpenStack / HCI completo** — funciona, mas você passa a operar uma nuvem inteira além do Kubernetes.

Eu já escrevi sobre o caminho [CloudStack no homelab](/pt/posts/about-my-homelab/). O VirtFoundry é o outro caminho: **Kubernetes-native**. Quem *já* quer o cluster não deveria precisar de um segundo appliance só para tratar VM como recurso de cloud.

KubeVirt resolve **rodar a VM**. Não resolve o dia 2:

- tenant e isolamento
- catálogo (template / offering)
- volume e snapshot com UX de cloud
- IAM e API para Terraform / GitOps
- uma UI que não é `kubectl apply`

## Arquitetura: operator primeiro

O control plane é um **operator**. O grupo de API é `virtfoundry.io`. Hoje o store de produção é só Kubernetes (`store.driver=kubernetes`) — sem MySQL no caminho crítico.

| Camada | O que é |
|--------|---------|
| **Operator** | Controllers + CRDs (`Tenant`, `Instance`, `VPC`, `Disk`, snapshots, IAM…) |
| **core** | API REST `/api/v1` + UI React — clientes do mesmo store |
| **Helm** | Dois charts: `virtfoundry-operator` e `virtfoundry` (API + UI) |
| **Terraform** | Provider de primeira parte no [Registry](https://registry.terraform.io/providers/virtfoundry/virtfoundry) |
| **Runtime** | KubeVirt (VM), Multus (rede de tenant), CSI (disco; Longhorn no homelab) |

![Dashboard do VirtFoundry no homelab](/images/posts/virtfoundry-dashboard.png)

A ideia é **compor blocos CNCF**, não reinventar hypervisor nem CSI. O operator reconcilia `Tenant` (namespace + status) e `Instance` (fase, IP, nome KubeVirt). Os outros kinds já existem como CRD; os controllers vão fechando o gap. GitOps entra de graça: Helm + Argo CD, CR como fonte da verdade.

![Topologia recomendada: cluster BYO, Longhorn, Gateway, VPC de tenant](/images/posts/virtfoundry-topology.svg)

## O que já dá para usar

Release atual dos charts: **0.7.0**. No homelab isso já cobre o ciclo que o TOC vai perguntar num demo: VM + volume + snapshot + UI.

![Snapshots de VM no VirtFoundry](/images/posts/virtfoundry-snapshots.png)

![Redes e VPCs por tenant](/images/posts/virtfoundry-networks.png)

| Recurso | Estado |
|---------|--------|
| Tenant + IAM (JWT, API key, roles) | Funciona |
| VM (deploy, start/stop, console) | Funciona — KubeVirt |
| Volume + snapshot de VM | Funciona; snapshot de volume precisa CSI com snapshot (Longhorn, não `local-path`) |
| VPC / rede isolada / IP público | Funciona com Multus; sem Multus a UI sobe e a rede de tenant não |
| L4 load balancer (VIP + listener) | Em evolução no roadmap |
| SSO / billing | Fora do core por enquanto, de propósito |

Homelab conta. Os três maintainers já estão no [`ADOPTERS.md`](https://github.com/virtfoundry/core/blob/main/ADOPTERS.md). O que falta para o Sandbox é adopter **fora** do `MAINTAINERS.md`.

## Comparação honesta

| | Proxmox VE | “Só KubeVirt” | Harvester | VirtFoundry |
|--|------------|---------------|-----------|-------------|
| Modelo | Appliance de hypervisor | YAML de VM | HCI completo | Control plane IaaS no **seu** cluster |
| Multi-tenant | ACL de datacenter | Você monta | Appliance | Tenant + IAM de primeira classe |
| GitOps | Não é o produto | Possível | ISO / HCI | Helm / Argo, CRDs |
| Melhor quando | ISO, ZFS, PBS, zero K8s | Poucas VMs, você aceita YAML | Quer HCI pronto | Já opera Kubernetes e quer UX de cloud |

**Proxmox ainda ganha** se você quer ISO, PBS, dataset ZFS ou LXC como produto. Fique lá. VirtFoundry não é um drop-in dessas coisas.

**Harvester** é HCI. VirtFoundry assume BYO Kubernetes (kubeadm, kubespray, managed).

**CloudStack** continua sendo IaaS clássico — e eu uso no homelab. VirtFoundry é o primo que mora no mesmo cluster das workloads de container.

## CNCF Sandbox: alvo, não status

O Sandbox da CNCF tem um checklist duro: licença Apache-2.0 completa, governança, CoC, security, **idade do repo ≥ 6 meses**, maintainers em ≥2 organizações, e evidência de que o projeto é reutilizável — não um reference architecture.

O que já está no lugar:

- Apache 2.0 + `NOTICE` em todos os repos oficiais
- `GOVERNANCE.md`, `MAINTAINERS.md`, `CONTRIBUTING.md`, CNCF Code of Conduct, `SECURITY.md`
- Três maintainers, duas orgs ([MAINTAINERS](https://github.com/virtfoundry/core/blob/main/MAINTAINERS.md))
- Operator + Helm + Terraform — produto, não um diagrama
- Draft da application: [`CNCF-SANDBOX-APPLICATION.md`](https://github.com/virtfoundry/core/blob/main/docs/CNCF-SANDBOX-APPLICATION.md)

O que **não** está:

- Idade do `core` — criado em **2026-08-03**, gate ~**2027-02-03**
- Adopters além dos maintainers
- Talk pública / intro na comunidade KubeVirt (isso vem depois)

Não escreva “projeto da CNCF”, “estamos no landscape” nem “já submetemos”. O destino é o Sandbox. O status hoje é open source Apache 2.0, alinhado às convenções da fundação.

![Store em CRD: kubectl get crd \| grep virtfoundry.io](/images/posts/virtfoundry-crds.png)

## Como experimentar

Docs: [virtfoundry.github.io/helm-charts](https://virtfoundry.github.io/helm-charts/docs/). Quickstart < 30 min. Pin a versão — não use `:latest`.

```bash
helm repo add virtfoundry https://virtfoundry.github.io/helm-charts
helm repo update

helm install virtfoundry-operator virtfoundry/virtfoundry-operator \
  --version 0.7.0 \
  -n virtfoundry-system --create-namespace

helm install virtfoundry virtfoundry/virtfoundry \
  --version 0.7.0 \
  -n virtfoundry-system \
  --set secrets.rootPassword='change-me' \
  --set secrets.jwtSecret='change-me'
```

Ordem: plataforma no cluster (KubeVirt + Multus + CSI) → **operator** → **API/UI**. Sem Multus, VPC e IP público não funcionam. Sem CSI com snapshot, snapshot de volume não funciona — use snapshot de VM no lab.

Repos:

- [core](https://github.com/virtfoundry/core) — API + UI
- [operator](https://github.com/virtfoundry/operator) — CRDs + controllers
- [helm-charts](https://github.com/virtfoundry/helm-charts) — charts + docs
- [terraform-provider-virtfoundry](https://github.com/virtfoundry/terraform-provider-virtfoundry)

Se instalar no homelab: abra uma issue, um `good first issue`, ou um PR em `ADOPTERS.md`. Isso pesa mais do que um like quando a application do Sandbox existir.

Comparação canônica no produto: [Why VirtFoundry](https://virtfoundry.github.io/helm-charts/docs/guide/why/). Checklist de tração: [CNCF-CHECKLIST.md](https://github.com/virtfoundry/core/blob/main/docs/CNCF-CHECKLIST.md).
