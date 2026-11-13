---
title: "Jobs de GPU em paralelo num Mac só: a memória é o escalonador"
date: 2026-11-13
description: "A GPU da Apple não tem partições, então o KubeSilicon v0.4 divide ela por memória: um SiliconJob declara spec.memory, começa quando cabe ao lado dos outros e é morto se usar mais. Ganhos medidos, uma surpresa com o RSS e os limites."
cover: /images/covers/kubesilicon-parallel-jobs.webp
readingTime: "5"
katex: false
mermaid: false
draft: false
slug: parallel-gpu-jobs-mac-kubesilicon
tags: ['kubernetes', 'kubeflow', 'kubesilicon', 'apple-silicon', 'macos', 'mlx', 'gpu', 'mlops']
categories: ['kubernetes']
---

No [post anterior](/pt/posts/kubeflow-pipelines-apple-silicon-gpu-kubesilicon/) um passo do Kubeflow Pipelines treinou um modelo na GPU do Mac por meio de um `SiliconJob`. Ele terminava com uma lista de limites, e dois deles eram estes: um job de GPU por vez, e nenhum limite de memória por job.

O KubeSilicon v0.4 tira os dois. Este post conta como, e por que a resposta acabou sendo a memória, e não a GPU.

## A GPU da Apple não tem partições

Numa placa NVIDIA de datacenter dá para fatiar a GPU (MIG, time slicing) e dar um pedaço para cada job. A GPU da Apple não tem nada parecido. Todo processo que usa Metal divide a GPU inteira, e o macOS decide quem roda quando.

Então, antes de escrever um escalonador, medi se rodar jobs lado a lado vale a pena. MLX num M5 Pro com 24 GB, uma rodada de 6 s por caso:

| Carga | 1 job | 2 jobs (total) | 4 jobs (total) |
|---|---|---|---|
| Treino de MLP pequena, passos/s | 1.170 | 1.603 | 2.057 |
| Loop de matmul 4096x4096, matmuls/s | 121 | 102 | 104 |

Quatro treinos pequenos ao mesmo tempo fizeram 1,8x o trabalho de um. Quatro loops de matmul grande fizeram 0,85x: pior que um. Um modelo pequeno deixa a GPU ociosa entre os kernels, e um segundo job preenche esses buracos. Um grande já mantém a GPU ocupada, e um segundo job só acrescenta troca de contexto.

Ou seja, jobs em paralelo ajudam exatamente onde o Mac costuma ser usado para ML: modelos pequenos, experimentos, varredura de hiperparâmetros. Eles não deixam um treino grande mais rápido.

## O que acaba de verdade é a memória

No Apple Silicon a GPU não tem memória própria. Ela divide a memória unificada com a CPU e com todo o resto do Mac, inclusive o navegador e o cluster kind. Dois jobs que querem 10 GB cada num Mac de 24 GB não ficam só um pouco mais lentos: o Mac começa a usar swap, e tudo fica lento.

Por isso a memória é o recurso a escalonar. Na v0.4 o job declara quanto precisa:

```yaml
apiVersion: kubesilicon.io/v1
kind: SiliconJob
metadata: { name: sweep-lr-0-01 }
spec:
  memory: 6Gi
  dependencies: [mlx]
  script: |
    ...
```

O daemon segue três regras:

1. **O job começa quando cabe.** O que o macOS informa como disponível, menos o que os jobs em execução declararam e ainda não usaram, menos uma reserva, precisa cobrir o `spec.memory`. A reserva é 10% da RAM, no mínimo 2 Gi (`-memory-reserve` muda isso).
2. **O job é morto quando mente.** O runner mede o job a cada 2 s, memória de CPU e GPU juntas, e mata o job se ele passar do declarado: `Failed`, "memory limit exceeded". O pico vai para o fim do log do job, para você dimensionar a próxima rodada.
3. **Os jobs começam na ordem de criação**, para um job grande não ficar esperando para sempre atrás dos pequenos. Um job sem `spec.memory` roda sozinho, como antes.

Nada é configurado por Mac. O mesmo YAML roda mais jobs ao mesmo tempo num Mac maior ou mais ocioso, e menos num Mac ocupado. Eu não quis uma opção de "máximo de jobs em paralelo", porque esse número é diferente em cada Mac e muda toda vez que você abre o navegador.

## A surpresa: o RSS não enxerga a GPU

A primeira versão do vigia de memória usava o RSS, o número que a maioria das ferramentas mostra como memória do processo. Testei com um job que alocava 4 GiB com MLX. O RSS dizia 19 MB.

O RSS conta páginas mapeadas no processo. As alocações do Metal ficam fora dessa conta, então para um job de GPU o RSS quase não serve. O que funciona é o physical footprint (`ri_phys_footprint`, de `proc_pid_rusage`), o mesmo número que o Monitor de Atividade chama de "Memória". Para o mesmo job ele marcou 4.113 MB.

O vigia soma o footprint de todos os processos do grupo do job, então um script que abre workers é medido inteiro.

## O quanto o "disponível" oscila?

O lado do "disponível" vem do `kern.memorystatus_level`, o número por trás do medidor de pressão de memória. Amostrei uma vez por segundo durante alguns minutos num Mac que não estava ocioso. Sem nada começando, ele variou até 1,2 GB em um segundo e 2,4 GB em dez. É o tamanho da reserva.

Ele também mede pressão, não bytes: um job segurando 4 GB quase sumiu dele depois de uns dez segundos, porque o macOS comprimiu e jogou outra memória para o swap para abrir espaço. É por isso que a conta também desconta o que os jobs em execução declararam e ainda não usaram. Quem protege de verdade os jobs que já estão rodando é o limite por job, não o número global.

## Limites

- **Números meus, um Mac.** Uma rodada por caso, só MLX, fp32. Ainda não há números de PyTorch MPS em paralelo, nem de consumo de energia ou temperatura.
- **Paralelo não acelera modelo grande.** A tabela acima mostra isso.
- **O vigia amostra a cada 2 s.** Um job pode passar do limite entre duas amostras. É uma proteção contra job descontrolado, não uma parede como um cgroup; o macOS não tem cgroups.
- **Continua não sendo uma barreira de segurança.** Os jobs rodam sob `sandbox-exec`. Não rode código em que você não confia.

## Teste

```sh
git clone https://github.com/Matheus-Thurler/KubeSilicon
cd KubeSilicon
make install CTX=kind-<seu-cluster>
kubectl apply -f examples/mlx-matmul.yaml
```

Coloque `memory: 4Gi` em duas cópias de um job e veja os dois rodarem juntos com `kubectl get sjob -w`. Os detalhes estão no README, em "Parallel jobs". O código está em [github.com/Matheus-Thurler/KubeSilicon](https://github.com/Matheus-Thurler/KubeSilicon).
