---
title: "Dois tenants, uma bridge: como achamos e corrigimos um vazamento entre tenants no VirtFoundry"
date: 2026-11-13
slug: virtfoundry-0-13-tenant-isolation
description: "Uma auditoria própria mostrou que as redes isoladas de tenants diferentes do VirtFoundry usavam a mesma bridge Linux. Aqui estão a prova, o conserto com uma bridge por tenant, as três coisas que quebraram no teste com VMs reais e o resto da 0.13.0."
cover: /images/covers/virtfoundry-tenant-isolation.webp
readingTime: "6"
katex: false
mermaid: false
draft: false
tags: ['kubernetes', 'kubevirt', 'multus', 'networking', 'security', 'virtfoundry', 'homelab']
categories: ['kubernetes']
---

<video src="/videos/virtfoundry-0.13-tenant-isolation.mp4" controls muted playsinline width="100%"></video>

O [VirtFoundry](https://github.com/virtfoundry) é o IaaS multi-tenant que eu construo sobre Kubernetes: uma API em Go grava CRDs e um operator transforma isso em VMs KubeVirt e redes Multus. Antes de fechar a 0.13.0 auditei o projeto inteiro, e o primeiro achado foi o que mais importa num produto multi-tenant: **as redes "isoladas" de tenants diferentes usavam a mesma bridge Linux.**

## A prova

Ler código é indício, não resultado, então testei no homelab. Criei um segundo tenant, subi VMs nos dois e deixei cair no mesmo nó. Uma VM de sonda no tenant `default` deu ping numa VM do tenant `smoke`:

```text
ping 10.0.0.3   -> 3 packets transmitted, 3 received, 0% packet loss
arp  10.0.0.3   -> fa:6b:0a:61:17:59   (o MAC da VM do outro tenant)
```

Toda rede isolada gerava uma NetworkAttachmentDefinition apontando para `virtfoundry-br0`, sem VLAN e com o mesmo CIDR padrão. Mesmo nó, mesmo domínio de broadcast, então nada barrava o ARP. (VMs em nós diferentes não se viam, porque a bridge não tinha uplink. O vazamento era entre tenants no mesmo nó.)

## O conserto

- **Uma bridge por tenant.** O operator a nomeia como `vfb` mais 8 caracteres hex do hash do namespace, e o core usa a mesma regra. O nome da rede CNI vira `<namespace>-<nome>`, então cada tenant também ganha o seu escopo de IPAM.
- **Um CIDR único por tenant.** O core agora recusa um CIDR de VPC que se sobreponha ao de outro tenant. Antes, todo tenant recebia `10.0.0.0/16`.
- **O host nunca roteia entre bridges de tenants.** O DaemonSet bridge-keeper mantém `FORWARD -i vfb+ -o vfb+ -j DROP` acima das regras ACCEPT de entrada e saída de `vfb+`. Sem esse DROP, o próprio nó roteava de um tenant para o outro.

## O que quebrou no teste

O conserto foi a parte fácil. Três coisas só apareceram com VMs reais:

1. **A saída morreu.** A policy `FORWARD` do host era DROP, e a regra que deixava as VMs saírem tinha sido posta à mão no nó, fora do chart. O keeper agora cuida dessas regras, e o NAD usa `isGateway` e `ipMasq`.
2. **O keeper ignorava regras novas.** Ele lia o script uma vez, na partida. Agora relê a cada ciclo, então uma mudança no ConfigMap vale sem reiniciar o pod.
3. **Um endereço legado voltava sempre.** Tirei o `10.0.0.1/24` da bridge antiga três vezes e ele voltou. O `ip monitor` e o journal do NetworkManager mostraram um perfil, e por trás dele um DaemonSet de spike esquecido que recolocava o endereço a cada ciclo. Remover o DaemonSet pelo Argo CD resolveu de vez.

## Depois

Com dois tenants vivos ao mesmo tempo, cada VM varreu a faixa do outro tenant e só alcançou a si mesma, e as duas alcançaram o gateway da LAN e a internet. Repeti o teste depois que a configuração durável chegou pelo GitOps.

## Também na 0.13.0

- Um `service_offering_id` desconhecido devolve 400. Antes, subia uma VM de 1 vCPU sem avisar ninguém.
- Uma falha ao gravar o Instance não responde mais 201 para uma VM que só existia no cache.
- Criar uma VPC com nome que já existe devolve 409 em vez de sobrescrever.
- Os namespaces do control plane do VKS não colidem mais entre clusters, e o token de join dos workers é renovado antes de expirar.

## Nota de upgrade

Defina `platform.networking.isolated.bridge.address` como string vazia. As bridges dos tenants recebem o gateway pelo NAD, e um endereço fixo na bridge legada faz o host rotear aquele CIDR por uma bridge sem portas. Tenants que já compartilham um CIDR o mantêm, então dê a cada um uma faixa distinta antes de rodarem VMs no mesmo nó.

As notas da release estão no [changelog](https://github.com/virtfoundry/helm-charts/blob/main/CHANGELOG.md). Se você roda VMs multi-tenant em Kubernetes, confira qual bridge as suas redes isoladas realmente usam.
