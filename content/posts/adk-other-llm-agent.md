---
title: "Google ADK with a local model: an agent without Gemini (LM Studio + LiteLLM)"
date: 2026-11-27
slug: adk-other-llm-agent
description: "How to run a Google ADK agent on a local model: LiteLlm in the LlmAgent, Gemma 4 served by LM Studio on the OpenAI-compatible API (/v1), the .env variables and adk web calling the tool with zero API cost."
cover: /images/covers/adk-other-llm-agent.webp
readingTime: "5"
katex: false
mermaid: false
draft: false
tags: ['google-adk', 'ai-agents', 'python', 'litellm', 'lm-studio', 'tutorial', 'video']
categories: ['python']
---

{{< youtube 0JEAWbpLbag >}}

ADK is made by Google, but your agent does not have to use Gemini. In the [previous episode](/posts/adk-tool-agent/) the agent got tools; now it runs on a **local model**, served by LM Studio on my machine, with no API key and no per-call cost. This is the third video of the series **ADK, from beginner to advanced** (in Portuguese), and the code is in the [repository](https://github.com/Matheus-Thurler/youtube-projects/tree/master/ADK-Iniciante%20ao%20Avancado/03-other-llm-agent).

## The piece that swaps the model: LiteLlm

Instead of passing a Gemini model name in `model=`, we pass a `LiteLlm`. [LiteLLM](https://adk.dev/agents/models/litellm/) is an OpenAI-compatible layer that talks to 100+ providers, local servers included.

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

The model comes from the `LLM_MODEL` variable. If it is not set, it falls back to Gemma 4 E4B on LM Studio. The `roll_die` tool is a plain Python function, just like in episode 2.

## The .env: no Google key

```bash
LLM_MODEL="lm_studio/google/gemma-4-e4b"
LM_STUDIO_API_BASE="http://localhost:1234/v1"
LM_STUDIO_API_KEY="lm-studio"
```

- `LLM_MODEL` uses the LiteLLM format: `provider/model`.
- `LM_STUDIO_API_BASE` is the LM Studio server address, OpenAI style (ends in `/v1`).
- `LM_STUDIO_API_KEY` can hold **any value**: LM Studio does not require a key, but LiteLLM expects the variable to be set.

Note that `GOOGLE_API_KEY` is not used here. To switch models just change `LLM_MODEL`; the repository's `.env.example` has examples for `ollama_chat/gemma3:latest`, `openai/gpt-4o` and `anthropic/claude-3-haiku-20240307`.

## Running it

1. In LM Studio, load the model (I used `google/gemma-4-e4b`) and start the local server.
2. In the project:

```bash
uv run adk web
```

Ask "hi, what do you do?" and then ask it to roll a six-sided die. While the agent thinks, LM Studio shows the prompt being processed on your machine; adk web shows the `roll_die(sides=6)` call and the result.

## Caveats

- A small local model is slower and picks tools less reliably than a large cloud model. Test your task before deciding.
- LM Studio must have the model loaded and the server running, or the agent fails on the first call.
- For deployment, ADK still makes Google's infrastructure the easy path, but nothing stops you from running it anywhere else.

## Next steps

In the next video we cover **structured outputs**: making the agent answer in a fixed format. Which local model would you pair with ADK: Gemma, Qwen, Llama? Tell me in the video comments.

- Playlist: [ADK, from beginner to advanced](https://www.youtube.com/playlist?list=PLSajB-Xd-S50)
- ADK docs on models: [adk.dev/agents/models](https://adk.dev/agents/models/)
- Code for this episode: [youtube-projects/ADK-Iniciante ao Avancado/03-other-llm-agent](https://github.com/Matheus-Thurler/youtube-projects/tree/master/ADK-Iniciante%20ao%20Avancado/03-other-llm-agent)
