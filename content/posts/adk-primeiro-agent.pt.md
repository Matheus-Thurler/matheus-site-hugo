---
title: "Seu primeiro agente de IA com Google ADK, Python e uv"
date: 2026-11-23
slug: adk-primeiro-agent
description: "Do uv init ao adk web: como criar, configurar e rodar seu primeiro agente com o Agent Development Kit do Google, e o que é um agente além de uma chamada de API."
cover: /images/covers/adk-primeiro-agent.webp
readingTime: "5"
katex: false
mermaid: false
draft: false
tags: ['google-adk', 'ai-agents', 'python', 'uv', 'sre', 'tutorial', 'video']
categories: ['python']
---

{{< youtube rljX5f02BIc >}}

Chamar um LLM por API é fácil. Um agente de verdade não é: ele precisa de ferramentas, memória, orquestração, teste e deploy. O [Google ADK](https://adk.dev/) (Agent Development Kit) é um framework open source que traz essas peças prontas, com o lema **build, evaluate, deploy**. Este é o primeiro vídeo da série **ADK, do iniciante ao avançado**, e o código está no [repositório](https://github.com/Matheus-Thurler/youtube-projects/tree/master/ADK-Iniciante%20ao%20Avancado/01-basic-agent).

## Um agente em cinco peças

A analogia que uso no vídeo:

- **Modelo**: o cérebro.
- **Tools**: as ferramentas que o agente pode usar.
- **Session state**: o bloco de notas da conversa.
- **Memory**: o caderno de anotações de longo prazo.
- **Runner**: o gerente que executa o loop (pergunta, modelo escolhe a tool, resposta volta para a sessão) e devolve a resposta.

Callbacks entram como as regras de negócio do agente. Tudo isso vira o assunto dos próximos vídeos.

## Passo a passo

Crie o projeto e instale o ADK com uv:

```bash
uv init
uv add google-adk
uv run adk --help
```

O `--help` lista os comandos da CLI: `create`, `run`, `web`, `eval`, `deploy` e outros. Para gerar o agente:

```bash
uv run adk create agente_basico
```

O ADK pergunta qual modelo usar (Gemini ou outro) e cria a pasta com três arquivos:

- `__init__.py`, que importa o agente;
- `.env`, para a chave da API;
- `agent.py`, com o agente.

O nome da pasta é o nome do agente: é por ele que você escolhe qual agente rodar. A única peça obrigatória é a variável `root_agent`:

```python
from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-3.8-flash',
    name='root_agent',
    description='Você é um agente de boas vindas.',
    instruction='Você é um agente de boas vindas. Seu objetivo é receber o usuário e fornecer informações sobre o sistema.',
)
```

## A chave da API

Crie uma chave no [Google AI Studio](https://aistudio.google.com/app/apikey) e coloque no `.env` da pasta do agente:

```bash
GOOGLE_API_KEY="sua-chave"
```

Os modelos do Gemini por API são pagos (e baratos). Teste, rode e apague a chave se quiser. Também dá para rodar com modelo local, o que vemos mais para frente na série.

## Rodando

No terminal:

```bash
uv run adk run agente_basico
```

E na interface web, a partir da pasta pai do agente:

```bash
uv run adk web
```

O `adk web` mostra o fluxo do agente e, à esquerda, os **eventos** de cada passo até a resposta. É a melhor ferramenta de debug que o ADK dá de graça. Ela é só para desenvolvimento, nunca para produção.

## Próximos passos

No próximo vídeo o agente ganha tools. Se você tem um processo de SRE, DevOps ou automação que gostaria de ver virar agente, conta nos comentários.

- Site do Google ADK: [adk.dev](https://adk.dev/)
- Código deste episódio: [youtube-projects/ADK-Iniciante ao Avancado/01-basic-agent](https://github.com/Matheus-Thurler/youtube-projects/tree/master/ADK-Iniciante%20ao%20Avancado/01-basic-agent)
