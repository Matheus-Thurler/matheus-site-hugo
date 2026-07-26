"""Chamadas Gemini com retry e fallback de modelos."""

from __future__ import annotations

import time

from django.conf import settings

DEFAULT_MODEL_FALLBACKS = (
    'gemini-3.5-flash',
    'gemini-3.6-flash',
    'gemini-3.1-flash-lite',
    'gemini-flash-latest',
)

RETRYABLE_MARKERS = (
    '503',
    '429',
    'UNAVAILABLE',
    'RESOURCE_EXHAUSTED',
    'high demand',
    'overloaded',
)


def _model_chain() -> list[str]:
    primary = getattr(settings, 'GEMINI_MODEL', 'gemini-3.5-flash')
    fallbacks = getattr(settings, 'GEMINI_MODEL_FALLBACKS', DEFAULT_MODEL_FALLBACKS)
    chain: list[str] = []
    for model in (primary, *fallbacks):
        if model and model not in chain:
            chain.append(model)
    return chain


def _is_retryable(exc: BaseException) -> bool:
    msg = str(exc).upper()
    return any(marker.upper() in msg for marker in RETRYABLE_MARKERS)


def _friendly_error(exc: BaseException) -> str:
    if _is_retryable(exc):
        return (
            'Gemini sobrecarregado no momento. Aguarde ~30s e clique em '
            '"Ver preview" ou "Regenerar com IA" de novo.'
        )
    return str(exc)


def generate_text(prompt: str, *, max_retries: int = 2) -> tuple[str, str]:
    """
    Gera texto via Gemini. Retorna (texto, model_usado).
    Tenta modelos em cadeia e repete em erros 503/429.
    """
    from google import genai

    api_key = getattr(settings, 'GEMINI_API_KEY', '')
    if not api_key:
        raise ValueError('GEMINI_API_KEY is not configured')

    client = genai.Client(api_key=api_key)
    models = _model_chain()
    last_exc: BaseException | None = None

    for model in models:
        for attempt in range(max_retries + 1):
            try:
                response = client.models.generate_content(model=model, contents=prompt)
                text = (response.text or '').strip()
                if not text:
                    raise ValueError(f'Empty response from {model}')
                return text, model
            except Exception as exc:
                last_exc = exc
                if not _is_retryable(exc):
                    raise ValueError(_friendly_error(exc)) from exc
                if attempt < max_retries:
                    time.sleep(2 ** attempt)
                    continue
                break

    raise ValueError(_friendly_error(last_exc or RuntimeError('Gemini unavailable')))
