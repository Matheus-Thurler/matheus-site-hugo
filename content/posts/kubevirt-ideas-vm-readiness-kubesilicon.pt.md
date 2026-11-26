---
title: "Running não é Ready: ideias do KubeVirt para VMs no Mac, sem o KubeVirt"
date: 2026-11-26
description: "O KubeSilicon v0.5 traz condição Ready, restartPolicy, virtualização aninhada e start/stop/restart para VMs em Apple Silicon, e fecha quatro brechas do sandbox dos jobs."
cover: /images/covers/kubesilicon-vm-readiness.webp
readingTime: "5"
katex: false
mermaid: false
draft: false
slug: kubevirt-ideas-vm-readiness-kubesilicon
tags: ['kubernetes', 'kubevirt', 'kubesilicon', 'apple-silicon', 'macos', 'virtualization']
categories: ['kubernetes']
---

Uma `SiliconVM` do [KubeSilicon](/pt/posts/kubevirt-on-apple-silicon-kubesilicon/) podia mostrar `Running` enquanto o SSH dentro dela ainda não respondia. E se o processo dela morresse, ficava morta até eu perceber.

No KubeVirt, os dois problemas já estão resolvidos. O KubeVirt não roda num Mac com Apple Silicon do jeito que eu preciso, e é por isso que este projeto existe, mas as ideias dele viajam bem. A v0.5 pega quatro delas sem colocar o KubeVirt como dependência.

## O que veio emprestado

| KubeVirt | KubeSilicon v0.5 |
|---|---|
| Condição `Ready`, readiness probes | Condição `Ready`, só porta TCP (`spec.readinessPort`, padrão 22) |
| `runStrategy` | `spec.running` mais `spec.restartPolicy` |
| Virtualização aninhada | `spec.nestedVirtualization` |
| `virtctl start / stop / restart` | `kubesilicon start / stop / restart` |

O que ele não tem: live migration, hotplug, snapshots, CDI, mais de um nó. É um Mac e um daemon.

## Ready quer dizer que alguém responde

`Running` só diz que a máquina virtual está ligada. `Ready` fica True enquanto o guest aceita conexões TCP numa porta, então os scripts podem parar de dar sleep e esperar:

```sh
kubectl wait --for=condition=Ready svm/demo --timeout=5m
```

## Uma queda não é um desligamento

O `restartPolicy` é `Never` por padrão, então nada muda se você não pedir. `OnFailure` liga a VM de novo quando ela morre. `Always` também faz isso depois que o próprio guest se desliga.

A parte interessante é separar os dois casos. O processo dono de cada VM anota como o guest terminou. Um `poweroff` digitado dentro do guest é respeitado, mesmo que o daemon reinicie depois. Um processo morto é uma falha, e a VM volta depois de uma espera que dobra de 10 segundos até 5 minutos, contada em `status.restartCount`.

Meu primeiro teste disso falhou por um motivo em que eu não tinha pensado. Matei o processo da VM com `kill -9` logo depois do primeiro boot, e o guest voltou sem SSH. Para o guest, isso é puxar o fio da tomada: o que ainda não tinha ido para o disco se perdeu. Agora o teste espera o cloud-init e roda `sync` antes do kill. Vale lembrar disso nos seus guests também.

## Uma VM dentro da VM

Num M3 ou mais novo, com macOS 15 ou mais novo, `nestedVirtualization: true` entrega `/dev/kvm` ao guest. No meu M5 Pro o teste ponta a ponta confere que o dispositivo está lá.

## O sandbox deixava portas abertas

O `SiliconJob` roda Python nativo no Mac para alcançar a GPU, dentro de um perfil do `sandbox-exec`. O perfil da v0.4 partia de "permite tudo" e então negava escritas e leituras da pasta do usuário. Testei o que isso deixa aberto, com alvos descartáveis, rodando a mesma sonda nos dois perfis:

| De dentro de um job | v0.4.0 | v0.5.0 |
|---|---|---|
| Ler um arquivo em `/tmp` | permitido | negado |
| Conectar num unix socket fora da pasta do job | permitido | negado |
| Matar um processo fora do sandbox | permitido | negado |
| Gravar uma preferência do macOS | permitido | negado |

A última me surpreendeu. Toda escrita em arquivo já era negada, mas o `defaults write` continuava funcionando, porque quem grava é outro processo, a seu pedido. Esse é o padrão: um sandbox de arquivos não impede um programa de pedir que outro faça o serviço. Precisou de uma regra própria, `(deny user-preference-write)`.

PyTorch MPS, MLX e `multiprocessing` continuam funcionando no perfil novo, e o teste ponta a ponta confere isso.

## Testes que não tinham como falhar

Ao adicionar essas verificações, descobri que algumas das antigas eram enfeite. Num script de shell com `set -e`, um `! comando` que falha não interrompe o script. Um comando que falha no meio de um `a && b` também não. Essas asserções imprimiam sucesso em qualquer caso. Agora são pequenas funções que saem com erro quando falham.

## Limites

- **Um Mac.** Testado num M5 Pro com 24 GB e um cluster kind. Não em M1 ou M2, nem em outras versões do macOS, nem em outros clusters.
- **Readiness é uma porta TCP.** Não há probe HTTP nem exec.
- **A espera entre reinícios só zera quando você para a VM.** Rodar muito tempo sem problema não zera.
- **Continua não sendo uma fronteira de segurança.** O `sandbox-exec` está obsoleto segundo a Apple, a rede fica aberta e tudo o que não está listado é permitido. Não rode código em que você não confia.

## Para testar

```sh
git clone https://github.com/Matheus-Thurler/KubeSilicon
cd KubeSilicon
make install CTX=kind-<your-cluster>
SSH_PUBKEY="$(cat ~/.ssh/id_ed25519.pub)" envsubst < examples/vm.yaml | kubectl apply -f -
kubectl wait --for=condition=Ready svm/demo --timeout=5m
```

Atualizando da v0.4: aplique os CRDs de novo. Um `SiliconJob` agora precisa de `script` ou `command`, e só `spec.running` pode mudar depois de criado. A lista completa está nas [notas da release](https://github.com/Matheus-Thurler/KubeSilicon/releases/tag/v0.5.0), e o post anterior é sobre [jobs de GPU em paralelo](/pt/posts/parallel-gpu-jobs-mac-kubesilicon/).
