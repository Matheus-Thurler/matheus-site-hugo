---
title: "Google ADK com modelo local: agente sem depender do Gemini (LM Studio + LiteLLM)"
date: 2026-11-27
slug: adk-other-llm-agent
description: "Como rodar um agente do Google ADK com modelo local: LiteLlm no LlmAgent, Gemma 4 no LM Studio servindo no padrão OpenAI (/v1), variáveis no .env e o adk web chamando a ferramenta sem custo de API."
cover: /images/covers/adk-other-llm-agent.webp
readingTime: "5"
katex: false
mermaid: false
draft: false
tags: ['google-adk', 'ai-agents', 'python', 'litellm', 'lm-studio', 'tutorial', 'video']
categories: ['python']
---

{{< youtube 0JEAWbpLbag >}}

O ADK é do Google, mas o agente não precisa usar o Gemini. No [episódio anterior](/posts/adk-tool-agent/) o agente ganhou ferramentas; agora ele roda com um **modelo local**, servido pelo LM Studio na minha máquina, sem chave de API e sem custo por chamada. Este é o terceiro vídeo da série **ADK, do iniciante ao avançado**, e o código está no [repositório](https://github.com/Matheus-Thurler/youtube-projects/tree/master/ADK-Iniciante%20ao%20Avancado/03-other-llm-agent).

## A peça que troca o modelo: LiteLlm

Em vez de passar o nome de um modelo Gemini em `model=`, passamos um `LiteLlm`. O [LiteLLM](https://adk.dev/agents/models/litellm/) é uma camada compatível com a API da OpenAI que fala com mais de 100 provedores, inclusive servidores locais.

```python
import os
import random

from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm


def roll_die(sides: int) -> dict:
    """Rolls a die with the given number of sides."""
    return {"status": "success", "result": random.randint(1, sides)}


root_agent = LlmAgent(
    model=LiteLlm(model=os.getenv("LLM_MODEL", "lm_studio/google/gemma-4-e4b")),
    name="dice_agent",
    description="Rolls dice.",
    instruction="You roll dice and answer questions about the outcome of the dice rolls.",
    tools=[roll_die],
)
```

O modelo vem da variável `LLM_MODEL`. Se ela não existir, cai no padrão: Gemma 4 E4B no LM Studio. A ferramenta `roll_die` é uma função Python comum, igual às do episódio 2.

## O .env: nenhuma chave do Google

```bash
LLM_MODEL="lm_studio/google/gemma-4-e4b"
LM_STUDIO_API_BASE="http://localhost:1234/v1"
LM_STUDIO_API_KEY="lm-studio"
```

- `LLM_MODEL` segue o formato do LiteLLM: `provedor/modelo`.
- `LM_STUDIO_API_BASE` é o endereço do servidor do LM Studio, no padrão da OpenAI (termina em `/v1`).
- `LM_STUDIO_API_KEY` pode ter **qualquer valor**: o LM Studio não exige chave, mas o LiteLLM espera a variável preenchida.

Repare que a `GOOGLE_API_KEY` não é usada aqui. Para trocar de modelo basta mudar `LLM_MODEL`; o `.env.example` do repositório traz exemplos com `ollama_chat/gemma3:latest`, `openai/gpt-4o` e `anthropic/claude-3-haiku-20240307`.

## Rodando

1. No LM Studio, carregue o modelo (usei o `google/gemma-4-e4b`) e ligue o servidor local.
2. No projeto:

```bash
uv run adk web
```

Pergunte "olá, o que você faz?" e depois peça para rolar um dado de 6 lados. Enquanto o agente pensa, o LM Studio mostra o prompt sendo processado na sua máquina; no adk web aparece a chamada `roll_die(sides=6)` e o resultado.

## Cuidados

- Modelo pequeno local é mais lento e erra mais na escolha de ferramentas que um modelo grande na nuvem. Teste a sua tarefa antes de decidir.
- O LM Studio precisa estar com o modelo carregado e o servidor ligado; senão o agente falha na primeira chamada.
- Na hora do deploy, o ADK continua facilitando ir para a infraestrutura do Google, mas nada impede rodar em qualquer outro lugar.

## Próximos passos

No próximo vídeo vemos **structured outputs**: fazer o agente responder num formato fixo. Qual modelo local você usaria com o ADK: Gemma, Qwen, Llama? Conta nos comentários do vídeo.

- Playlist: [ADK, do iniciante ao avançado](https://www.youtube.com/playlist?list=PLSajB-Xd-S50)
- Doc do ADK sobre modelos: [adk.dev/agents/models](https://adk.dev/agents/models/)
- Código deste episódio: [youtube-projects/ADK-Iniciante ao Avancado/03-other-llm-agent](https://github.com/Matheus-Thurler/youtube-projects/tree/master/ADK-Iniciante%20ao%20Avancado/03-other-llm-agent)
