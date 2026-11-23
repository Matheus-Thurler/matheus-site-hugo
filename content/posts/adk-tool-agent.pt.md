---
title: "Tool Agent no Google ADK: dando ferramentas em Python ao seu agente"
date: 2026-11-25
slug: adk-tool-agent
description: "Como dar tools ao agente no Google ADK: duas funções Python (hora e clima), o parâmetro tools, a instrução que guia a escolha e o adk web mostrando qual ferramenta foi chamada."
cover: /images/covers/adk-tool-agent.webp
readingTime: "5"
katex: false
mermaid: false
draft: false
tags: ['google-adk', 'ai-agents', 'python', 'tools', 'tutorial', 'video']
categories: ['python']
---

{{< youtube 5CJIcKP0Xf4 >}}

No [primeiro episódio](/posts/adk-primeiro-agent/) criamos um agente que só conversa. Agora ele ganha **tools**: ferramentas que nada mais são do que funções Python. O modelo lê a pergunta, escolhe qual função chamar e usa o retorno para responder. Este é o segundo vídeo da série **ADK, do iniciante ao avançado**, e o código está no [repositório](https://github.com/Matheus-Thurler/youtube-projects/tree/master/ADK-Iniciante%20ao%20Avancado/02-tool-agent).

## Tool é uma função Python

Duas funções, uma para a hora e outra para o clima, ambas usando a API gratuita do [Open-Meteo](https://open-meteo.com/) para achar a cidade:

```python
def get_current_time(city: str) -> dict:
    """Returns the current real-time date and time in a specified city.

    Args:
        city: Name of the city.
    """
    places = json.load(urlopen(GEO + city)).get("results")
    if not places:
        return {"status": "error", "message": f"City '{city}' not found."}
    now = datetime.now(ZoneInfo(places[0]["timezone"]))
    return {"status": "success", "city": city, "time": now.strftime("%H:%M:%S")}
```

O que o modelo enxerga é a **assinatura, a docstring e o retorno**. É a docstring que diz para ele quando usar a função, então escreva como uma instrução. Retornar um `dict` com `status` deixa claro para o agente se deu certo ou errou, e o erro (cidade não encontrada) volta como dado em vez de quebrar tudo.

## Passando as tools ao agente

```python
root_agent = Agent(
    model="gemini-flash-latest",
    name="root_agent",
    description="Tells the current time and weather in a specified city.",
    instruction=(
        "You are a helpful assistant that tells the current time and weather in cities. "
        "Use 'get_current_time' for time and 'get_current_weather' for weather. "
        "Translate the WMO weather_code into plain words."
    ),
    tools=[get_current_time, get_current_weather],
)
```

A lista `tools` é o que registra as funções. A `instruction` orienta a escolha entre elas e pede para traduzir o `weather_code` (padrão WMO) em palavras.

## Rodando no adk web

```bash
uv run adk web
```

Pergunte "qual o horário de Tóquio?". Nos eventos, à esquerda, você vê o agente chamando `get_current_time("Tokyo")` e o nó da ferramenta acendendo no grafo. Depois pergunte o clima, e por fim as duas coisas na mesma frase: o modelo chama as duas ferramentas em uma só resposta.

## Cuidados

- A API externa pode falhar ou devolver vazio. Valide e retorne um erro claro, como no exemplo.
- Docstring ruim gera chamada errada. Descreva o que a função faz e cada argumento.
- Ferramentas que alteram coisas (escrever, apagar, enviar) pedem aprovação e guardrails, assunto de um episódio mais para frente.

## Próximos passos

No próximo vídeo rodamos o agente com outros modelos, inclusive local, sem depender da API paga do Gemini. Qual ferramenta ou API você conectaria primeiro ao seu agente? Conta nos comentários do vídeo.

- Playlist: [ADK, do iniciante ao avançado](https://www.youtube.com/playlist?list=PLSajB-Xd-S50)
- Site do Google ADK: [adk.dev](https://adk.dev/)
- Código deste episódio: [youtube-projects/ADK-Iniciante ao Avancado/02-tool-agent](https://github.com/Matheus-Thurler/youtube-projects/tree/master/ADK-Iniciante%20ao%20Avancado/02-tool-agent)
