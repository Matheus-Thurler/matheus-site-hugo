---
title: "Dois daemons, um disco: os bugs que aparecem depois do primeiro dia"
date: 2026-11-27
description: "O KubeSilicon v0.5.1 corrige o que dá errado depois que o daemon está rodando há um tempo: um segundo daemon no mesmo disco, uma VM com erro ligada de novo, um status que se sobrescrevia, um Service sumido, caminhos longos de socket e um log mudo no Kubeflow."
cover: /images/covers/kubesilicon-one-daemon.webp
readingTime: "5"
katex: false
mermaid: false
draft: false
slug: two-daemons-one-disk-kubesilicon
tags: ['kubernetes', 'kubevirt', 'kubesilicon', 'apple-silicon', 'macos', 'virtualization']
categories: ['kubernetes']
---

O [post anterior](/pt/posts/kubevirt-ideas-vm-readiness-kubesilicon/) trouxe a condição `Ready` e o `restartPolicy` para as VMs do KubeSilicon. No primeiro boot tudo parecia certo. Os problemas deste aqui começam depois: um segundo daemon, uma VM que morreu sem ninguém olhando, um Service que alguém apagou.

A v0.5.1 é uma release de correção. Sem funcionalidade nova, sem mudança nos CRDs.

## O que estava errado

| Situação | v0.5.0 | v0.5.1 |
|---|---|---|
| Um segundo `kubesilicond` sobe | os dois cuidam da mesma VM e do `disk.raw` dela | o segundo encerra |
| O daemon reinicia depois de uma VM registrar erro | ligada de novo, mesmo com `restartPolicy: Never` | segue o `restartPolicy` |
| A VM não pode ser provisionada | `Provisioning` metade do tempo | continua `Failed` |
| O Service da VM é apagado | nunca voltava, `Ready` congelava | publicado a cada passada |
| Caminho longo no diretório da VM | o socket do console não faz bind, VM fica `Stopped` | funciona |
| Passo do Kubeflow, log acima de 4 KiB | para de imprimir | avisa que o trecho foi truncado |

## Dois daemons, um disco

O `make install` roda o daemon no login. O README também mostrava como iniciar na mão. Faça os dois e dois processos observam os mesmos objetos: cada um sobe um launcher para o mesmo diretório da VM, o segundo sobrescreve o arquivo `pid`, e dois guests abrem uma única imagem de disco.

A correção é um `flock` em `~/.kubesilicon/lock`:

```
another kubesilicond is running (pid 52186, lock /Users/you/.kubesilicon/lock): stop it first
```

Escolhi um lock em arquivo aberto, e não um arquivo de pid, porque o kernel solta o lock quando o processo termina, mesmo com `SIGKILL`. Não sobra lock velho para limpar. O pid escrito dentro serve só para a mensagem ser útil.

## Never era nunca, menos depois de reiniciar

O processo dono de cada VM anota como o guest terminou. Com o daemon olhando, o `restartPolicy` era respeitado. Depois de reiniciar o daemon, só o desligamento limpo era. Uma VM que tinha registrado erro parecia uma VM que nunca tinha subido, então era provisionada de novo: o `Never` era ignorado, e o `restartCount` e o intervalo entre reinícios eram pulados.

Agora os dois caminhos tomam a mesma decisão.

## Um status que se sobrescrevia

Uma passada do reconcile pode escrever duas vezes: `Provisioning` e depois `Failed`. A segunda escrita se comparava com o objeto do começo da passada, que já dizia `Failed` por causa da passada anterior. Então concluía que nada tinha mudado e pulava a escrita. O resultado era uma VM quebrada aparecendo como `Provisioning` metade do tempo.

O Service tinha um problema parecido. Ele só era aplicado quando o IP mudava, então apagar na mão era apagar de vez, e um apply com falha retornava antes de o status ser escrito. Agora o Service e o EndpointSlice são aplicados a cada passada, e uma falha vai para o log sem travar o status.

## Cerca de 104 bytes

O console serial é um unix socket dentro do diretório da VM. O macOS limita o caminho de um socket a cerca de 104 bytes. Passando disso, o launcher falhava com `bind: invalid argument`. Um namespace como `virtfoundry-tenant-default` deixava só umas duas dezenas de caracteres para o nome da VM.

O daemon e o cliente agora fazem bind e conectam pelo nome do arquivo, de dentro do diretório. Subi uma VM Ubuntu em um cluster kind descartável com um caminho de socket de 220 bytes e entrei com `kubesilicon console`.

## Um log mudo que não estava mudo

No Kubeflow Pipelines, o passo imprime o `status.logTail`, que são os últimos 4 KiB do log do job. Quando o log passava desse tamanho, o trecho parava de crescer e o passo não imprimia mais nada. Um treino parecia parado justamente quando mais escrevia. Agora o passo avisa que a saída foi truncada e aponta para `kubesilicon logs`. Ele não transmite o resto.

## Limites

- **A suíte ponta a ponta não foi rodada de novo nesta release.** Os testes unitários usam um cliente Kubernetes falso. Rodei `go test -race ./...` na tag v0.5.1 (macOS 27.0.1, Go 1.27.1) e passou. Uma asserção ponta a ponta para o caso do reinício entrou na `main` depois da tag e ainda não rodou.
- **A correção do reinício precisa de um registro.** Se o próprio processo da VM for morto com o daemon desligado, ele não escreve nada, e o próximo daemon tenta ligar a VM de novo, diga o que disser o `restartPolicy`. Conferi isso com um teste unitário descartável.
- **O lock só funciona entre daemons v0.5.1.** O daemon da v0.5.0 não pega lock, então pare os que você iniciou na mão antes de atualizar. O lock também é por diretório de estado.
- **Os limites de antes continuam:** um Mac, readiness só por TCP, sem live migration, e o sandbox dos jobs não é uma fronteira de segurança.

## Experimente

```sh
git clone https://github.com/Matheus-Thurler/KubeSilicon
cd KubeSilicon
make check
make install CTX=kind-<your-cluster>
```

Vindo da v0.5.0: pare qualquer `kubesilicond` iniciado na mão e rode `make install` de novo, que recarrega o agente de login. Se você usa o componente do Kubeflow, recompile sua pipeline a partir de `examples/kubeflow/pipeline.py`. Os detalhes estão nas [notas da release](https://github.com/Matheus-Thurler/KubeSilicon/releases/tag/v0.5.1).
