---
title: "Your first AI agent with Google ADK, Python and uv"
date: 2026-11-23
slug: adk-primeiro-agent
description: "From uv init to adk web: how to create, configure and run your first agent with Google's Agent Development Kit, and what an agent is beyond an API call."
cover: /images/covers/adk-primeiro-agent.webp
readingTime: "5"
katex: false
mermaid: false
draft: false
tags: ['google-adk', 'ai-agents', 'python', 'uv', 'sre', 'tutorial', 'video']
categories: ['python']
---

{{< youtube rljX5f02BIc >}}

Calling an LLM through an API is easy. A real agent is not: it needs tools, memory, orchestration, testing and deployment. [Google ADK](https://adk.dev/) (Agent Development Kit) is an open source framework that ships those pieces, with the motto **build, evaluate, deploy**. This is the first video of the series **ADK, from beginner to advanced**, and the code is in the [repository](https://github.com/Matheus-Thurler/youtube-projects/tree/master/ADK-Iniciante%20ao%20Avancado/01-basic-agent). The video is in Portuguese.

## An agent in five parts

The analogy I use in the video:

- **Model**: the brain.
- **Tools**: what the agent is allowed to use.
- **Session state**: the notepad of the conversation.
- **Memory**: the long-term notebook.
- **Runner**: the manager that runs the loop (question, the model picks a tool, the answer goes back to the session) and returns the reply.

Callbacks are the business rules of the agent. Each of these gets its own video later in the series.

## Step by step

Create the project and install ADK with uv:

```bash
uv init
uv add google-adk
uv run adk --help
```

`--help` lists the CLI commands: `create`, `run`, `web`, `eval`, `deploy` and more. To generate the agent:

```bash
uv run adk create agente_basico
```

ADK asks which model to use (Gemini or another) and creates a folder with three files:

- `__init__.py`, which imports the agent;
- `.env`, for the API key;
- `agent.py`, with the agent.

The folder name is the agent name: it is how you choose which agent to run. The only required piece is the `root_agent` variable:

```python
from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-3.8-flash',
    name='root_agent',
    description='You are a welcome agent.',
    instruction='You are a welcome agent. Your goal is to greet the user and give information about the system.',
)
```

## The API key

Create a key in [Google AI Studio](https://aistudio.google.com/app/apikey) and put it in the `.env` inside the agent folder:

```bash
GOOGLE_API_KEY="your-key"
```

Gemini models through the API are paid (and cheap). Test, run, and delete the key if you want. You can also run a local model, which comes later in the series.

## Running it

In the terminal:

```bash
uv run adk run agente_basico
```

And in the web UI, from the agent's parent folder:

```bash
uv run adk web
```

`adk web` shows the agent flow and, on the left, the **events** of every step until the answer. It is the best debugging tool ADK gives you for free. It is for development only, never for production.

## Next

In the next video the agent gets tools. If you have an SRE, DevOps or automation process you would like to see turned into an agent, tell me in the comments.

- Google ADK site: [adk.dev](https://adk.dev/)
- Code for this episode: [youtube-projects/ADK-Iniciante ao Avancado/01-basic-agent](https://github.com/Matheus-Thurler/youtube-projects/tree/master/ADK-Iniciante%20ao%20Avancado/01-basic-agent)
