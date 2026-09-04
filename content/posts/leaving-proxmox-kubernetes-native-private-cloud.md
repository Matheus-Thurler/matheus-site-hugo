---
title: "I created VirtFoundry: a Kubernetes operator on a path to CNCF Sandbox"
date: 2026-09-04
description: "I created VirtFoundry — operator + CRDs + UI for private cloud on KubeVirt. Architecture, what works today, an honest comparison, and the road to CNCF Sandbox."
cover: /images/covers/virtfoundry-logo-card.png
readingTime: "12"
katex: false
mermaid: false
draft: false
slug: leaving-proxmox-kubernetes-native-private-cloud
tags: ['kubernetes', 'kubevirt', 'virtfoundry', 'homelab', 'iaas', 'gitops', 'operator', 'cncf', 'proxmox']
categories: ['kubernetes', 'homelab']
---

**I created [VirtFoundry](https://github.com/virtfoundry).** It is a **Kubernetes operator** — `virtfoundry.io` CRDs — that turns a cluster you already run into a multi-tenant private cloud: tenants, VPCs, VMs, volumes, snapshots, IAM, REST API, and a UI.

The hypervisor is [KubeVirt](https://kubevirt.io/). Source of truth is not MySQL: it is Kubernetes. The destination is a **[CNCF Sandbox](https://github.com/cncf/sandbox)** application.

It is **not** a CNCF project yet. We are building the operator, charts, Terraform provider, and community so we can apply when the repo meets the maturity bar — not before.

![VirtFoundry VM list](/images/covers/virtfoundry-ui-vms.png)

## The problem I wanted to solve

If you already operate Kubernetes and still need VMs, the realistic options are:

1. **A second silo** — Proxmox (or similar) beside the cluster. Two backups, two networks, two sources of truth.
2. **Raw KubeVirt YAML** — an excellent hypervisor API and a terrible private-cloud product. Every tenant becomes a pile of `VirtualMachine`, NAD, PVC, and RBAC by hand.
3. **Full OpenStack / HCI** — it works, and you now operate another cloud next to Kubernetes.

I already wrote about the [CloudStack homelab path](/posts/about-my-homelab/). VirtFoundry is the other path: **Kubernetes-native**. If you already want the cluster, you should not need a second appliance just to treat VMs as cloud resources.

KubeVirt **runs the VM**. It does not give you day-2 private cloud:

- first-class tenants
- catalog (templates / offerings)
- volume and snapshot UX
- IAM plus an API that Terraform and GitOps can drive
- a UI that is not `kubectl apply`

## Architecture: operator first

The control plane is an **operator**. The API group is `virtfoundry.io`. Production store is Kubernetes only (`store.driver=kubernetes`) — no MySQL on the critical path.

| Layer | What it is |
|-------|------------|
| **Operator** | Controllers + CRDs (`Tenant`, `Instance`, `VPC`, `Disk`, snapshots, IAM, …) |
| **core** | REST `/api/v1` + React UI — clients of the same store |
| **Helm** | Two charts: `virtfoundry-operator` and `virtfoundry` (API + UI) |
| **Terraform** | First-party provider on the [Registry](https://registry.terraform.io/providers/virtfoundry/virtfoundry) |
| **Runtime** | KubeVirt (VM), Multus (tenant net), CSI (disks; Longhorn in the homelab) |

![VirtFoundry dashboard in the homelab](/images/posts/virtfoundry-dashboard.png)

The design is **compose CNCF building blocks**, not reinvent the hypervisor or CSI. The operator reconciles `Tenant` (namespace + status) and `Instance` (phase, IP, KubeVirt name). Other kinds already exist as CRDs; controllers close the gap over time. GitOps comes free: Helm + Argo CD, CRs as source of truth.

![Recommended topology: BYO cluster, Longhorn, Gateway, tenant VPC](/images/posts/virtfoundry-topology.svg)

## What you can use today

Current chart release: **0.7.0**. In the homelab that already covers the demo a TOC reviewer will click: VM + volume + snapshot + UI.

![VM snapshots in VirtFoundry](/images/posts/virtfoundry-snapshots.png)

![Per-tenant networks and VPCs](/images/posts/virtfoundry-networks.png)

| Capability | Status |
|------------|--------|
| Tenant + IAM (JWT, API keys, roles) | Works |
| VM (deploy, start/stop, console) | Works — KubeVirt |
| Volume + VM snapshot | Works; volume snapshots need CSI snapshot support (Longhorn, not `local-path`) |
| VPC / isolated net / public IP | Works with Multus; without Multus the UI comes up and tenant networking does not |
| L4 load balancer (VIP + listener) | Evolving on the roadmap |
| SSO / billing | Kept out of core on purpose |

Homelabs count. The three maintainers are already in [`ADOPTERS.md`](https://github.com/virtfoundry/core/blob/main/ADOPTERS.md). Sandbox still needs adopters **outside** `MAINTAINERS.md`.

## Honest comparison

| | Proxmox VE | “Just KubeVirt” | Harvester | VirtFoundry |
|--|------------|-----------------|-----------|-------------|
| Model | Hypervisor appliance | VM YAML | Full HCI | IaaS control plane on **your** cluster |
| Multi-tenant | Datacenter ACLs | You build it | Appliance | First-class tenant + IAM |
| GitOps | Not the product | Possible | ISO / HCI | Helm / Argo, CRDs |
| Best when | ISO, ZFS, PBS, no K8s | A few VMs, YAML is fine | You want HCI | You already run Kubernetes and want cloud UX |

**Proxmox still wins** if you want an ISO, PBS, ZFS datasets, or LXC as product features. Stay there. VirtFoundry is not a drop-in for those.

**Harvester** is HCI. VirtFoundry assumes BYO Kubernetes (kubeadm, kubespray, managed).

**CloudStack** remains classic IaaS — I still run it in the homelab. VirtFoundry is the cousin that lives on the same cluster as container workloads.

## CNCF Sandbox: destination, not status

CNCF Sandbox has a hard checklist: full Apache-2.0, governance, CoC, security, **repo age ≥ 6 months**, maintainers in ≥2 organizations, and evidence the project is reusable — not a reference architecture.

Already in place:

- Apache 2.0 + `NOTICE` on every official repo
- `GOVERNANCE.md`, `MAINTAINERS.md`, `CONTRIBUTING.md`, CNCF Code of Conduct, `SECURITY.md`
- Three maintainers, two orgs ([MAINTAINERS](https://github.com/virtfoundry/core/blob/main/MAINTAINERS.md))
- Operator + Helm + Terraform — a product, not a diagram
- Application draft: [`CNCF-SANDBOX-APPLICATION.md`](https://github.com/virtfoundry/core/blob/main/docs/CNCF-SANDBOX-APPLICATION.md)

Still open:

- Age of `core` — created **2026-08-03**, gate ~**2027-02-03**
- Adopters beyond maintainers
- Public talk / KubeVirt community intro (comes later)

Do not write “CNCF project”, “we are on the landscape”, or “we already applied”. The destination is Sandbox. Status today is Apache 2.0 open source, following foundation conventions.

![CRD store: kubectl get crd | grep virtfoundry.io](/images/posts/virtfoundry-crds.png)

## Try it

Docs: [virtfoundry.github.io/helm-charts](https://virtfoundry.github.io/helm-charts/docs/). Quickstart under 30 minutes. Pin the version — do not use `:latest`.

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

Order: cluster platform (KubeVirt + Multus + CSI) → **operator** → **API/UI**. Without Multus, VPC and public IP do not work. Without CSI snapshots, volume snapshots do not work — use VM snapshots in the lab.

Repos:

- [core](https://github.com/virtfoundry/core) — API + UI
- [operator](https://github.com/virtfoundry/operator) — CRDs + controllers
- [helm-charts](https://github.com/virtfoundry/helm-charts) — charts + docs
- [terraform-provider-virtfoundry](https://github.com/virtfoundry/terraform-provider-virtfoundry)

If you install in a homelab: file an issue, pick a `good first issue`, or open a PR on `ADOPTERS.md`. That weighs more than a like when the Sandbox application exists.

Canonical comparison: [Why VirtFoundry](https://virtfoundry.github.io/helm-charts/docs/guide/why/). Traction checklist: [CNCF-CHECKLIST.md](https://github.com/virtfoundry/core/blob/main/docs/CNCF-CHECKLIST.md).
