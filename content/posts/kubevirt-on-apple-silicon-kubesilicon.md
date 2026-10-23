---
title: "KubeVirt does not run on Apple Silicon, so I built KubeSilicon"
date: 2026-10-23
description: "KubeVirt needs KVM, and macOS has none. KubeSilicon runs Linux VMs from Kubernetes objects on an M-series Mac, on kind, using Apple's Virtualization.framework."
cover: /images/covers/kubesilicon-card.webp
readingTime: "6"
katex: false
mermaid: false
draft: false
slug: kubevirt-on-apple-silicon-kubesilicon
tags: ['kubernetes', 'kubevirt', 'kubesilicon', 'apple-silicon', 'macos', 'kind', 'virtfoundry', 'golang', 'opensource']
categories: ['kubernetes']
---

**KubeVirt does not run on a Mac with Apple Silicon.** It needs KVM, and macOS has no KVM.

I maintain [VirtFoundry](/posts/leaving-proxmox-kubernetes-native-private-cloud/), a private cloud operator built on KubeVirt. That means every time I wanted to test something that creates VMs, I needed a Linux server. My M5 Pro could run the cluster, but not the VMs.

So I built **[KubeSilicon](https://github.com/Matheus-Thurler/KubeSilicon)**: you declare a `SiliconVM` object, and a daemon on the Mac boots a Linux ARM64 VM with Apple's [`Virtualization.framework`](https://developer.apple.com/documentation/virtualization). Pods in your local cluster reach the VM by IP or DNS name.

<video src="/videos/kubesilicon-tutorial.mp4" controls muted playsinline width="100%"></video>

*From-scratch install, 3.5 minutes: kind cluster, install, first VM, SSH, pod to VM, stop/start.*

## How it works

```
 kind (Docker Desktop VM)              macOS host
 ┌──────────────────────┐              ┌────────────────────────────────────┐
 │ SiliconVM objects    │◄─ API watch ─┤ kubesilicond                        │
 │ (CRD kubesilicon.io) │── status ───►│   download + convert image          │
 │                      │              │   cloud-init ISO                    │
 │ pod ──────── ping/ssh ─────────────►│   Virtualization.framework  ──► VM  │
 └──────────────────────┘              └────────────────────────────────────┘
```

The daemon runs on the Mac, outside the cluster. It watches `SiliconVM` objects, starts one detached process per VM, and writes `status.phase` and `status.ip` back. It also publishes a headless Service, so `demo.default.svc.cluster.local` resolves from any pod. The daemon can stop or crash and the VMs keep running.

## Three commands

```bash
kind create cluster --name kubesilicon
make install CTX=kind-kubesilicon
kubectl --context kind-kubesilicon apply -f examples/vm.yaml
```

```yaml
apiVersion: kubesilicon.io/v1
kind: SiliconVM
metadata: { name: demo }
spec:
  cpu: 2
  memory: 2Gi
  disk:
    source: https://cloud-images.ubuntu.com/releases/noble/release/ubuntu-24.04-server-cloudimg-arm64.img
    size: 10Gi
  cloudInit:
    userData: |
      #cloud-config
      users:
        - name: ubuntu
          sudo: ALL=(ALL) NOPASSWD:ALL
          ssh_authorized_keys: [ssh-ed25519 AAAA... you@host]
```

In my tests the VM reaches `Running` in about 6 seconds once the image is cached, and a busybox pod pings it in 1 to 2 ms.

## kind, minikube, and others

The daemon only needs two things: the Kubernetes API of your cluster, and a network path between the pods and the VM (the VMs get a NAT address on the Mac, `192.168.64.x`).

- **Tested:** kind on Docker Desktop. This is the only setup I have validated.
- **Should work, not tested:** minikube, Colima, OrbStack, k3d. Anything where the cluster runs in a VM or container on the same Mac and can reach that NAT range.
- **Does not apply:** a cluster in the cloud. The VMs live on your Mac.

If you try another one, tell me what happened. I will add it to the validation notes either way.

## How it relates to KubeVirt and VirtFoundry

KubeSilicon is **not** KubeVirt and does not use its CRDs. It has its own `kubesilicon.io/v1` API, shaped like KubeVirt's, because KubeVirt's launcher is built around KVM and QEMU.

| | KubeVirt | KubeSilicon |
|--|----------|-------------|
| Hypervisor | KVM + QEMU | Apple Virtualization.framework |
| Where VMs run | Inside pods, on Linux nodes | Processes on the Mac, outside the cluster |
| Guests | Linux, Windows, more | Linux ARM64 only |
| Live migration, hotplug, snapshots | Yes | No |
| Runs on Apple Silicon | No | Yes |
| Maturity | CNCF incubating | Early, one Mac, one maintainer |

KubeVirt is the right choice on Linux servers. KubeSilicon is for the laptop: development, demos, and CI on your own Mac.

VirtFoundry sits one layer above. It gives you tenants, VPCs, IAM, and a UI on top of the hypervisor. Mapping which KubeVirt resources VirtFoundry uses, so it could drive `SiliconVM` on a Mac, is the idea I want to explore next. It is **not built yet**.

## An honest note on stability

Early on, guests crashed at random: kernel Oops and `SIGILL` in 3 of 4 boots with Apple's default disk mode. Switching the disk attachment to cached with fsync gave 0 crashes in 9 boots. The sample is small and I do not know the cause below the framework, so treat it as strong evidence, not proof. The numbers are in [docs/validation.md](https://github.com/Matheus-Thurler/KubeSilicon/blob/main/docs/validation.md).

## Limits today

- One Mac, one worker. Multiple Macs as nodes is a design goal, not a feature.
- The Service has no ports. Use the VM IP or ping.
- A VM whose launcher process died is not restarted automatically.
- Linux ARM64 guests only. macOS guests are out of scope.
- API `v1` in name only. It will change.

## Try it

- Repo: [github.com/Matheus-Thurler/KubeSilicon](https://github.com/Matheus-Thurler/KubeSilicon), Apache-2.0.
- Needs an Apple Silicon Mac, Go, `qemu-img`, a running kind cluster, and `kubectl`.
- Issues and pull requests are welcome, especially reports from other cluster tools.
