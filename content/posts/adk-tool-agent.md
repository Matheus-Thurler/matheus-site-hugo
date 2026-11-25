---
title: "Tool Agent in Google ADK: giving your agent Python tools"
date: 2026-11-25
slug: adk-tool-agent
description: "How to give an agent tools in Google ADK: two Python functions (time and weather), the tools parameter, the instruction that guides the choice, and adk web showing which tool was called."
cover: /images/covers/adk-tool-agent.webp
readingTime: "5"
katex: false
mermaid: false
draft: false
tags: ['google-adk', 'ai-agents', 'python', 'tools', 'tutorial', 'video']
categories: ['python']
---

{{< youtube EI9kTlUM7KY >}}

In the [first episode](/posts/adk-primeiro-agent/) we built an agent that only talks. Now it gets **tools**: nothing more than Python functions. The model reads the question, picks which function to call and uses the result to answer. This is the second video of the series **ADK, from beginner to advanced**, and the code is in the [repository](https://github.com/Matheus-Thurler/youtube-projects/tree/master/ADK-Iniciante%20ao%20Avancado/02-tool-agent).

## A tool is a Python function

Two functions, one for time and one for weather, both using the free [Open-Meteo](https://open-meteo.com/) API to find the city:

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

What the model sees is the **signature, the docstring and the return value**. The docstring tells it when to use the function, so write it like an instruction. Returning a `dict` with `status` makes it clear whether the call worked, and the error (city not found) comes back as data instead of crashing everything.

## Passing the tools to the agent

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

The `tools` list registers the functions. The `instruction` guides the choice between them and asks the model to translate the `weather_code` (WMO standard) into plain words.

## Running in adk web

```bash
uv run adk web
```

Ask "what time is it in Tokyo?". In the events on the left you see the agent calling `get_current_time("Tokyo")` and the tool node lighting up in the graph. Then ask about the weather, and finally both in the same sentence: the model calls both tools in one answer.

## Watch out for

- The external API can fail or return nothing. Validate and return a clear error, as in the example.
- A bad docstring causes wrong calls. Describe what the function does and each argument.
- Tools that change things (write, delete, send) need approval and guardrails, covered in a later episode.

## Next steps

In the next video we run the agent with other models, including a local one, without depending on the paid Gemini API. Which tool or API would you connect to your agent first? Tell me in the video comments. The video is in Portuguese.

- Playlist: [ADK, from beginner to advanced](https://www.youtube.com/playlist?list=PLSajB-Xd-S50)
- Google ADK site: [adk.dev](https://adk.dev/)
- Code for this episode: [youtube-projects/ADK-Iniciante ao Avancado/02-tool-agent](https://github.com/Matheus-Thurler/youtube-projects/tree/master/ADK-Iniciante%20ao%20Avancado/02-tool-agent)
