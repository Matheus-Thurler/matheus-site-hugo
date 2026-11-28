---
title: "Two daemons, one disk: the bugs that show up after day one"
date: 2026-11-27
description: "KubeSilicon v0.5.1 fixes what goes wrong once the daemon has been up for a while: a second daemon on the same disk, a crashed VM booted again, a status that overwrote itself, a missing Service, long socket paths and a quiet Kubeflow log."
cover: /images/covers/kubesilicon-one-daemon.webp
readingTime: "5"
katex: false
mermaid: false
draft: false
slug: two-daemons-one-disk-kubesilicon
tags: ['kubernetes', 'kubevirt', 'kubesilicon', 'apple-silicon', 'macos', 'virtualization']
categories: ['kubernetes']
---

The [last post](/posts/kubevirt-ideas-vm-readiness-kubesilicon/) added a `Ready` condition and `restartPolicy` to the VMs in KubeSilicon. A fresh boot looked fine. The problems in this one start later: a second daemon, a VM that died while nobody was watching, a Service someone deleted.

v0.5.1 is a patch release. No new features, no CRD changes.

## What was wrong

| Situation | v0.5.0 | v0.5.1 |
|---|---|---|
| A second `kubesilicond` starts | both manage the same VM and its `disk.raw` | the second one exits |
| Daemon restarts after a VM recorded an error | booted again, even with `restartPolicy: Never` | follows `restartPolicy` |
| A VM cannot be provisioned | `Provisioning` half the time | stays `Failed` |
| The VM's Service is deleted | never came back, `Ready` froze | published on every pass |
| Long VM directory path | console socket fails to bind, VM stays `Stopped` | works |
| Kubeflow step, log over 4 KiB | stops printing | says the tail is truncated |

## Two daemons, one disk

`make install` runs the daemon at login. The README also showed how to start it by hand. Do both and two processes watch the same objects: each starts a launcher for the same VM directory, the second overwrites the `pid` file, and two guests open one disk image.

The fix is an `flock` on `~/.kubesilicon/lock`:

```
another kubesilicond is running (pid 52186, lock /Users/you/.kubesilicon/lock): stop it first
```

I chose a lock on an open file over a pid file because the kernel drops it when the process ends, even on `SIGKILL`. There is no stale lock to clean up. The pid written inside is only there to make the message useful.

## Never meant never, except after a restart

The process that owns each VM writes down how the guest ended. While the daemon was watching, `restartPolicy` was respected. After a daemon restart, only a clean shutdown was. A VM that had recorded an error looked like a VM that had never started, so it was provisioned again: `Never` was ignored, and `restartCount` and the restart delay were skipped.

Now both paths take the same decision.

## A status that overwrote itself

One reconcile pass can write twice: `Provisioning`, then `Failed`. The second write compared itself with the object the pass started from, which already said `Failed` from the previous pass. So it concluded nothing had changed and skipped the write. The result was a broken VM showing `Provisioning` half the time.

The Service had a related problem. It was applied only when the IP changed, so deleting it by hand meant it was gone for good, and a failed apply returned before the status was written. Both the Service and the EndpointSlice are now applied on every pass, and a failure is logged without blocking the status.

## About 104 bytes

The serial console is a unix socket inside the VM directory. macOS limits a socket path to about 104 bytes. Past that the launcher failed with `bind: invalid argument`. A namespace like `virtfoundry-tenant-default` left only a couple dozen characters for the VM name.

The daemon and the client now bind and connect by file name from inside the directory. I booted an Ubuntu VM on a disposable kind cluster with a 220-byte socket path and logged in with `kubesilicon console`.

## A quiet log that was not quiet

In Kubeflow Pipelines, the step prints `status.logTail`, which is the last 4 KiB of the job log. Once the log passed that size, the tail stopped growing and the step printed nothing more. A training run looked idle exactly when it was noisiest. The step now says the output is truncated and points to `kubesilicon logs`. It does not stream the rest.

## Limits

- **The end-to-end suite was not re-run for this release.** The unit tests run against a fake Kubernetes client. I ran `go test -race ./...` on the v0.5.1 tag (macOS 27.0.1, Go 1.27.1) and it passed. An end-to-end assertion for the restart case was added to `main` after the tag and has not run yet.
- **The restart fix needs a record.** If the VM process itself is killed while the daemon is down, it writes nothing, and the next daemon tries to boot the VM again whatever `restartPolicy` says. I checked this with a throwaway unit test.
- **The lock only works between v0.5.1 daemons.** A v0.5.0 daemon takes no lock, so stop any you started by hand before upgrading. The lock is also per state directory.
- **Same limits as before:** one Mac, TCP-only readiness, no live migration, and the job sandbox is not a security boundary.

## Try it

```sh
git clone https://github.com/Matheus-Thurler/KubeSilicon
cd KubeSilicon
make check
make install CTX=kind-<your-cluster>
```

Upgrading from v0.5.0: stop any `kubesilicond` you started by hand, then run `make install` again, which reloads the login agent. If you use the Kubeflow component, recompile your pipeline from `examples/kubeflow/pipeline.py`. Details are in the [release notes](https://github.com/Matheus-Thurler/KubeSilicon/releases/tag/v0.5.1).
