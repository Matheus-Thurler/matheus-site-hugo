---
title: "KubeVirt não roda em Apple Silicon, então criei o KubeSilicon"
date: 2026-10-23
description: "O KubeVirt precisa de KVM, e o macOS não tem. O KubeSilicon cria VMs Linux a partir de objetos Kubernetes em um Mac com chip M, no kind, usando o Virtualization.framework da Apple."
cover: /images/covers/kubesilicon-card.webp
readingTime: "6"
katex: false
mermaid: false
draft: false
slug: kubevirt-on-apple-silicon-kubesilicon
tags: ['kubernetes', 'kubevirt', 'kubesilicon', 'apple-silicon', 'macos', 'kind', 'virtfoundry', 'golang', 'opensource']
categories: ['kubernetes']
---

**O KubeVirt não roda em um Mac com Apple Silicon.** Ele precisa de KVM, e o macOS não tem KVM.

Eu mantenho o [VirtFoundry](/posts/leaving-proxmox-kubernetes-native-private-cloud/), um operator de nuvem privada em cima do KubeVirt. Isso significa que, toda vez que eu queria testar algo que cria VMs, precisava de um servidor Linux. Meu M5 Pro roda o cluster, mas não as VMs.

Então criei o **[KubeSilicon](https://github.com/Matheus-Thurler/KubeSilicon)**: você declara um objeto `SiliconVM`, e um daemon no Mac sobe uma VM Linux ARM64 com o [`Virtualization.framework`](https://developer.apple.com/documentation/virtualization) da Apple. Os pods do seu cluster local acessam a VM por IP ou por nome DNS.

<video src="/videos/kubesilicon-tutorial.mp4" controls muted playsinline width="100%"></video>

*Instalação do zero, 3,5 minutos: cluster kind, instalação, primeira VM, SSH, pod para a VM, stop/start.*

## Como funciona

```
 kind (VM do Docker Desktop)           host macOS
 ┌──────────────────────┐              ┌────────────────────────────────────┐
 │ objetos SiliconVM    │◄─ API watch ─┤ kubesilicond                        │
 │ (CRD kubesilicon.io) │── status ───►│   baixa + converte a imagem         │
 │                      │              │   ISO do cloud-init                 │
 │ pod ──────── ping/ssh ─────────────►│   Virtualization.framework  ──► VM  │
 └──────────────────────┘              └────────────────────────────────────┘
```

O daemon roda no Mac, fora do cluster. Ele observa os objetos `SiliconVM`, inicia um processo separado por VM e escreve `status.phase` e `status.ip` de volta. Também publica um Service headless, então `demo.default.svc.cluster.local` resolve de qualquer pod. O daemon pode parar ou cair e as VMs continuam rodando.

## Três comandos

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
          ssh_authorized_keys: [ssh-ed25519 AAAA... voce@host]
```

Nos meus testes a VM chega em `Running` em cerca de 6 segundos com a imagem já em cache, e um pod busybox faz ping nela em 1 a 2 ms.

## kind, minikube e outras opções

O daemon precisa só de duas coisas: a API Kubernetes do seu cluster e um caminho de rede entre os pods e a VM (as VMs recebem um endereço NAT no Mac, `192.168.64.x`).

- **Testado:** kind no Docker Desktop. É o único setup que validei.
- **Deveria funcionar, não testado:** minikube, Colima, OrbStack, k3d. Qualquer um em que o cluster rode em uma VM ou container no mesmo Mac e alcance essa faixa NAT.
- **Não se aplica:** cluster na nuvem. As VMs vivem no seu Mac.

Se você testar outro, me conta o que aconteceu. Eu registro nas notas de validação de qualquer forma.

## Relação com KubeVirt e VirtFoundry

O KubeSilicon **não** é o KubeVirt e não usa os CRDs dele. Tem a própria API `kubesilicon.io/v1`, no formato do KubeVirt, porque o launcher do KubeVirt é feito em volta de KVM e QEMU.

| | KubeVirt | KubeSilicon |
|--|----------|-------------|
| Hypervisor | KVM + QEMU | Apple Virtualization.framework |
| Onde as VMs rodam | Dentro de pods, em nós Linux | Processos no Mac, fora do cluster |
| Guests | Linux, Windows e mais | Só Linux ARM64 |
| Live migration, hotplug, snapshots | Sim | Não |
| Roda em Apple Silicon | Não | Sim |
| Maturidade | CNCF incubating | Early, um Mac, um mantenedor |

O KubeVirt é a escolha certa em servidores Linux. O KubeSilicon é para o notebook: desenvolvimento, demos e CI no seu próprio Mac.

O VirtFoundry fica uma camada acima. Ele entrega tenants, VPCs, IAM e UI por cima do hypervisor. Mapear quais recursos do KubeVirt o VirtFoundry usa, para ele poder dirigir `SiliconVM` em um Mac, é a ideia que quero explorar a seguir. **Ainda não foi feito.**

## Uma nota honesta sobre estabilidade

No começo, os guests quebravam aleatoriamente: kernel Oops e `SIGILL` em 3 de 4 boots com o modo de disco padrão da Apple. Trocar o disco para cached com fsync deu 0 crashes em 9 boots. A amostra é pequena e não sei a causa abaixo do framework, então trate como evidência forte, não como prova. Os números estão em [docs/validation.md](https://github.com/Matheus-Thurler/KubeSilicon/blob/main/docs/validation.md).

## Limites hoje

- Um Mac, um worker. Vários Macs como nós é meta de design, não recurso.
- O Service não tem portas. Use o IP da VM ou ping.
- Uma VM cujo processo launcher morreu não é reiniciada automaticamente.
- Só guests Linux ARM64. Guests macOS estão fora do escopo.
- API `v1` só no nome. Vai mudar.

## Teste

- Repo: [github.com/Matheus-Thurler/KubeSilicon](https://github.com/Matheus-Thurler/KubeSilicon), Apache-2.0.
- Precisa de um Mac Apple Silicon, Go, `qemu-img`, um cluster kind rodando e `kubectl`.
- Issues e pull requests são bem-vindos, principalmente relatos de outras ferramentas de cluster.
