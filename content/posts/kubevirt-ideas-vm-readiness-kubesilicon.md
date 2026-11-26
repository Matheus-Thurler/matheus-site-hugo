---
title: "Running is not Ready: KubeVirt ideas for VMs on a Mac, without KubeVirt"
date: 2026-11-26
description: "KubeSilicon v0.5 adds a Ready condition, restartPolicy, nested virtualization and start/stop/restart to VMs on Apple Silicon, and closes four things its job sandbox left open."
cover: /images/covers/kubesilicon-vm-readiness.webp
readingTime: "5"
katex: false
mermaid: false
draft: false
slug: kubevirt-ideas-vm-readiness-kubesilicon
tags: ['kubernetes', 'kubevirt', 'kubesilicon', 'apple-silicon', 'macos', 'virtualization']
categories: ['kubernetes']
---

A `SiliconVM` in [KubeSilicon](/posts/kubevirt-on-apple-silicon-kubesilicon/) could say `Running` while SSH inside it was still not answering. And if its process died, it stayed dead until I noticed.

Both are solved problems in KubeVirt. KubeVirt does not run on an Apple Silicon Mac the way I need it to, which is why this project exists, but its ideas travel well. v0.5 borrows four of them without adding KubeVirt as a dependency.

## What was borrowed

| KubeVirt | KubeSilicon v0.5 |
|---|---|
| `Ready` condition, readiness probes | `Ready` condition, TCP port only (`spec.readinessPort`, default 22) |
| `runStrategy` | `spec.running` plus `spec.restartPolicy` |
| Nested virtualization | `spec.nestedVirtualization` |
| `virtctl start / stop / restart` | `kubesilicon start / stop / restart` |

What it does not have: live migration, hotplug, snapshots, CDI, more than one node. It is one Mac and one daemon.

## Ready means something answers

`Running` only says the virtual machine is up. `Ready` is True while the guest accepts TCP connections on a port, so scripts can stop sleeping and wait:

```sh
kubectl wait --for=condition=Ready svm/demo --timeout=5m
```

## A crash is not a shutdown

`restartPolicy` is `Never` by default, so nothing changes if you do not ask for it. `OnFailure` starts the VM again when it dies. `Always` also does it after the guest shuts itself down.

The interesting part is telling those two apart. The process that owns each VM writes down how the guest ended. A `poweroff` typed inside the guest is respected, even if the daemon restarts later. A killed process is a failure, and the VM comes back after a delay that doubles from 10 seconds up to 5 minutes, counted in `status.restartCount`.

My first test of this failed for a reason I had not thought about. I killed the VM process with `kill -9` right after the first boot, and the guest came back without SSH. For the guest, that is pulling the power cord: whatever it had not written to disk yet was gone. The test now waits for cloud-init and runs `sync` before the kill. Keep that in mind about your own guests too.

## A VM inside the VM

On an M3 or newer with macOS 15 or newer, `nestedVirtualization: true` gives the guest `/dev/kvm`. On my M5 Pro the end-to-end test checks that the device is there.

## The sandbox left doors open

`SiliconJob` runs Python natively on the Mac to reach the GPU, inside a `sandbox-exec` profile. The v0.4 profile started from "allow everything", then denied writes and reads of the home directory. I tested what that leaves open, with throwaway targets, running the same probe against both profiles:

| From inside a job | v0.4.0 | v0.5.0 |
|---|---|---|
| Read a file in `/tmp` | allowed | denied |
| Connect to a unix socket outside the job directory | allowed | denied |
| Kill a process outside the sandbox | allowed | denied |
| Write a macOS preference | allowed | denied |

The last one surprised me. All file writes were already denied, but `defaults write` still worked, because the write is done by another process on your behalf. That is the pattern: a sandbox on files does not stop a program from asking someone else to act. It needed its own rule, `(deny user-preference-write)`.

PyTorch MPS, MLX and `multiprocessing` still work inside the new profile, and the end-to-end test checks them.

## Tests that could not fail

While adding those checks I found that some of my older ones were decorative. In a shell script with `set -e`, a failing `! command` does not stop the script. Neither does a failing command in the middle of `a && b`. Those assertions printed success no matter what. They are now small helper functions that exit when they fail.

## Limits

- **One Mac.** Tested on an M5 Pro with 24 GB and a kind cluster. Not on M1 or M2, not on other macOS versions, not on other clusters.
- **Readiness is a TCP port.** No HTTP or exec probes.
- **The restart delay only resets when you stop the VM.** A long healthy run does not reset it.
- **Still not a security boundary.** `sandbox-exec` is deprecated by Apple, the network is open, and everything not listed is allowed. Do not run code you do not trust.

## Try it

```sh
git clone https://github.com/Matheus-Thurler/KubeSilicon
cd KubeSilicon
make install CTX=kind-<your-cluster>
SSH_PUBKEY="$(cat ~/.ssh/id_ed25519.pub)" envsubst < examples/vm.yaml | kubectl apply -f -
kubectl wait --for=condition=Ready svm/demo --timeout=5m
```

Upgrading from v0.4: apply the CRDs again. A `SiliconJob` now needs `script` or `command`, and only `spec.running` can change after it is created. The full list is in the [release notes](https://github.com/Matheus-Thurler/KubeSilicon/releases/tag/v0.5.0), and the previous post is about [running GPU jobs in parallel](/posts/parallel-gpu-jobs-mac-kubesilicon/).
