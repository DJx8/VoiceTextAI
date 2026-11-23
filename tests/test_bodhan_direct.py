from pathlib import Path
from unittest.mock import Mock

import backend.bodhan_direct as bodhan


def mock_response(data=None, content=b"fake-audio"):
    response = Mock()
    response.raise_for_status.return_value = None
    response.json.return_value = data or {}
    response.content = content
    return response


def setup_keys(monkeypatch):
    monkeypatch.setenv("BODHAN_TRANSCRIBE_KEY", "test-transcribe-key")
    monkeypatch.setenv("BODHAN_TRANSLATE_KEY", "test-translate-key")
    monkeypatch.setenv("BODHAN_SPEAK_KEY", "test-speak-key")


def test_transcription_api(monkeypatch):
    setup_keys(monkeypatch)

    monkeypatch.setattr(
        bodhan,
        "convert_audio",
        lambda audio, filename: (b"fake-wav", 5.0),
    )

    response = mock_response(
        {
            "text": "നമസ്കാരം",
            "language": "ml",
        }
    )

    post = Mock(return_value=response)
    monkeypatch.setattr(bodhan.requests, "post", post)

    result = bodhan.transcribe_with_bodhan(
        b"fake-audio",
        "sample.wav",
        "ml",
    )

    assert result["transcription"] == "നമസ്കാരം"
    assert result["duration_seconds"] == 5.0

    args, kwargs = post.call_args

    assert args[0].endswith("/v1/audio/transcriptions")
    assert kwargs["data"]["model"] == "indic-transcribe"
    assert kwargs["data"]["language"] == "ml"
    assert kwargs["headers"]["Authorization"] == "Bearer test-transcribe-key"


def test_translation_api(monkeypatch):
    setup_keys(monkeypatch)

    response = mock_response(
        {"choices": [{"message": {"content": "Hello, how are you?"}}]}
    )

    post = Mock(return_value=response)
    monkeypatch.setattr(bodhan.requests, "post", post)

    result = bodhan.translate_with_bodhan(
        "നമസ്കാരം",
        "ml",
        "en",
    )

    assert result == "Hello, how are you?"

    args, kwargs = post.call_args

    assert args[0].endswith("/v1/chat/completions")

    payload = kwargs["json"]

    assert payload["model"] == "indic-translate"
    assert payload["source_language_code"] == "ml"
    assert payload["target_language_code"] == "en"


def test_tts_api(monkeypatch, tmp_path):
    setup_keys(monkeypatch)

    monkeypatch.setattr(
        bodhan.tempfile,
        "NamedTemporaryFile",
        lambda **kwargs: open(tmp_path / "test.wav", "wb"),
    )

    response = mock_response(content=b"fake-audio-data")

    post = Mock(return_value=response)
    monkeypatch.setattr(bodhan.requests, "post", post)

    audio_path = bodhan.generate_speech_with_bodhan(
        "നമസ്കാരം",
        "ml",
        "Lakshmi",
    )

    assert Path(audio_path).exists()
    assert Path(audio_path).read_bytes() == b"fake-audio-data"

    args, kwargs = post.call_args

    assert args[0].endswith("/v1/audio/speech")

    payload = kwargs["json"]

    assert payload["model"] == "indic-speak"
    assert payload["input"] == "നമസ്കാരം"
    assert payload["voice"] == "Lakshmi"
    assert '"lang": "ml"' in payload["instructions"]


def test_complete_pipeline(monkeypatch):
    setup_keys(monkeypatch)

    transcription_mock = Mock(
        return_value={
            "transcription": "നമസ്കാരം",
            "duration_seconds": 5.0,
        }
    )

    translation_mock = Mock(
        side_effect=[
            "Hello",
            "ഹലോ",
        ]
    )

    tts_mock = Mock(return_value="generated.wav")

    monkeypatch.setattr(
        bodhan,
        "transcribe_with_bodhan",
        transcription_mock,
    )
    monkeypatch.setattr(
        bodhan,
        "translate_with_bodhan",
        translation_mock,
    )
    monkeypatch.setattr(
        bodhan,
        "generate_speech_with_bodhan",
        tts_mock,
    )

    result = bodhan.process_bodhan_direct(
        audio_data=b"fake-audio",
        filename="sample.wav",
        spoken_language="ml",
        tts_language="ml",
        voice="Lakshmi",
        generate_speech=True,
    )

    assert result["success"] is True
    assert result["transcription"] == "നമസ്കാരം"
    assert result["translation"] == "Hello"
    assert result["speech_text"] == "ഹലോ"
    assert result["audio_path"] == "generated.wav"
    assert result["tts_generated"] is True

    assert transcription_mock.call_count == 1
    assert translation_mock.call_count == 2
    assert tts_mock.call_count == 1


def test_pipeline_without_tts(monkeypatch):
    setup_keys(monkeypatch)

    monkeypatch.setattr(
        bodhan,
        "transcribe_with_bodhan",
        Mock(
            return_value={
                "transcription": "നമസ്കാരം",
                "duration_seconds": 5.0,
            }
        ),
    )

    translation_mock = Mock(return_value="Hello")

    monkeypatch.setattr(
        bodhan,
        "translate_with_bodhan",
        translation_mock,
    )

    tts_mock = Mock()
    monkeypatch.setattr(
        bodhan,
        "generate_speech_with_bodhan",
        tts_mock,
    )

    result = bodhan.process_bodhan_direct(
        b"fake-audio",
        "sample.wav",
        "ml",
        generate_speech=False,
    )

    assert result["success"] is True
    assert result["translation"] == "Hello"
    assert result["tts_generated"] is False
    assert result["audio_path"] is None

    translation_mock.assert_called_once()
    tts_mock.assert_not_called()


def test_tts_failure_does_not_destroy_text_results(monkeypatch):
    setup_keys(monkeypatch)

    monkeypatch.setattr(
        bodhan,
        "transcribe_with_bodhan",
        Mock(
            return_value={
                "transcription": "നമസ്കാരം",
                "duration_seconds": 5.0,
            }
        ),
    )

    monkeypatch.setattr(
        bodhan,
        "translate_with_bodhan",
        Mock(side_effect=["Hello", "ഹലോ"]),
    )

    monkeypatch.setattr(
        bodhan,
        "generate_speech_with_bodhan",
        Mock(side_effect=RuntimeError("Simulated TTS failure")),
    )

    result = bodhan.process_bodhan_direct(
        b"fake-audio",
        "sample.wav",
        "ml",
        generate_speech=True,
    )

    assert result["success"] is True
    assert result["transcription"] == "നമസ്കാരം"
    assert result["translation"] == "Hello"
    assert result["tts_generated"] is False
    assert "Simulated TTS failure" in result["tts_error"]
