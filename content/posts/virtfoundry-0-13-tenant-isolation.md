---
title: "Two tenants, one bridge: how we found and fixed a cross-tenant leak in VirtFoundry"
date: 2026-11-13
slug: virtfoundry-0-13-tenant-isolation
description: "A self-audit found that the isolated networks of different VirtFoundry tenants shared one Linux bridge. This is the proof, the per-tenant bridge fix, the three things that broke while testing it on real VMs, and what else ships in 0.13.0."
cover: /images/covers/virtfoundry-tenant-isolation.webp
readingTime: "6"
katex: false
mermaid: false
draft: false
tags: ['kubernetes', 'kubevirt', 'multus', 'networking', 'security', 'virtfoundry', 'homelab']
categories: ['kubernetes']
---

<video src="/videos/virtfoundry-0.13-tenant-isolation.mp4" controls muted playsinline width="100%"></video>

[VirtFoundry](https://github.com/virtfoundry) is the multi-tenant IaaS I build on Kubernetes: a Go API writes CRDs, an operator turns them into KubeVirt VMs and Multus networks. Before cutting 0.13.0 I audited the whole project, and the first finding was the one that matters most for a multi-tenant product: **the "isolated" networks of different tenants all used the same Linux bridge.**

## The proof

Reading code is a hint, not a result, so I tested it on the homelab. I created a second tenant, started VMs in both tenants and let them land on the same node. A probe VM in tenant `default` pinged a VM in tenant `smoke`:

```text
ping 10.0.0.3   -> 3 packets transmitted, 3 received, 0% packet loss
arp  10.0.0.3   -> fa:6b:0a:61:17:59   (the MAC of the other tenant's VM)
```

Every isolated network generated a NetworkAttachmentDefinition pointing at `virtfoundry-br0`, with no VLAN and the same default CIDR. Same node, same broadcast domain, so nothing stopped ARP. (VMs on different nodes did not see each other, because the bridge had no uplink. The leak was between tenants on the same node.)

## The fix

- **One bridge per tenant.** The operator names it `vfb` plus 8 hex characters of the namespace hash, and core uses the same rule. The CNI network name becomes `<namespace>-<name>`, so each tenant also gets its own IPAM scope.
- **A unique CIDR per tenant.** Core now refuses a VPC CIDR that overlaps any other tenant's VPC. Before, every tenant got `10.0.0.0/16`.
- **The host never routes between tenant bridges.** The bridge-keeper DaemonSet keeps `FORWARD -i vfb+ -o vfb+ -j DROP` above the ACCEPT rules for traffic to and from `vfb+`. Without that DROP, the node itself routed from one tenant to the other.

## What broke while testing it

The fix was the easy half. Three things only showed up on real VMs:

1. **Egress died.** The host `FORWARD` policy was DROP, and the rule that let VMs out had been added by hand on the node, outside the chart. The keeper now owns those rules, and the NAD sets `isGateway` and `ipMasq`.
2. **The keeper ignored new rules.** It sourced its script once at start. It now re-sources it every cycle, so a ConfigMap change applies without a pod restart.
3. **A legacy address kept coming back.** I removed `10.0.0.1/24` from the old bridge three times and it returned. `ip monitor` and the NetworkManager journal showed a profile, and behind it a forgotten spike DaemonSet that re-added the address every cycle. Removing the DaemonSet through Argo CD fixed it for good.

## After

With two tenants alive at the same time, each VM scanned the other tenant's range and reached nothing but itself, and both reached the LAN gateway and the internet. I repeated the test after the durable configuration had shipped through GitOps.

## Also in 0.13.0

- An unknown `service_offering_id` returns 400. It used to boot a 1 vCPU VM without telling anyone.
- A failed Instance write no longer answers 201 for a VM that only existed in the cache.
- Creating a VPC with a name that already exists returns 409 instead of overwriting it.
- VKS control-plane namespaces can no longer collide between clusters, and the worker join token is renewed before it expires.

## Upgrade note

Set `platform.networking.isolated.bridge.address` to an empty string. Tenant bridges get their gateway from the NAD, and a fixed address on the legacy bridge makes the host route that CIDR through a bridge with no ports. Tenants that already share a CIDR keep it, so give each one a distinct range before they run VMs on the same node.

The release notes are in the [changelog](https://github.com/virtfoundry/helm-charts/blob/main/CHANGELOG.md). If you run multi-tenant VMs on Kubernetes, check which bridge your isolated networks really use.
