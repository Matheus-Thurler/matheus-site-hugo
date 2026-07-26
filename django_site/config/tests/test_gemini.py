from unittest.mock import MagicMock, patch

from config.gemini import generate_text, _is_retryable


def test_is_retryable_detects_503():
    assert _is_retryable(Exception("503 UNAVAILABLE high demand"))


@patch('config.gemini.time.sleep')
@patch('google.genai.Client')
def test_generate_text_falls_back_on_503(mock_client_cls, _sleep):
    client = MagicMock()
    mock_client_cls.return_value = client
    ok = MagicMock(text='{"title":"ok"}')
    client.models.generate_content.side_effect = [
        Exception('503 UNAVAILABLE high demand'),
        ok,
    ]

    with patch('config.gemini._model_chain', return_value=['gemini-3.5-flash']):
        text, model = generate_text('hello', max_retries=1)

    assert text == '{"title":"ok"}'
    assert model == 'gemini-3.5-flash'
    assert client.models.generate_content.call_count == 2
