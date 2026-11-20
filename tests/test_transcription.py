from types import SimpleNamespace

import pytest

from backend import transcription


def test_empty_audio_is_rejected():
    with pytest.raises(ValueError, match="Audio file is empty"):
        transcription.transcribe_audio_bytes(b"", "test.wav")


def test_invalid_model_is_rejected():
    with pytest.raises(ValueError, match="Invalid model selection"):
        transcription.transcribe_audio_bytes(
            b"audio", "test.wav", model="invalid"
        )


def test_unsupported_indic_language_is_rejected(monkeypatch):
    monkeypatch.setattr(
        transcription, "convert_audio", lambda *args: (b"wav", 2.0)
    )

    with pytest.raises(ValueError, match="Unsupported language"):
        transcription.transcribe_audio_bytes(
            b"audio", "test.wav", language="xyz", model="indic"
        )


def test_whisper_transcription(monkeypatch):
    monkeypatch.setattr(
        transcription, "convert_audio", lambda *args: (b"wav-data", 3.5)
    )

    mock_create = lambda **kwargs: SimpleNamespace(text="  Hello world.  ")

    mock_client = SimpleNamespace(
        audio=SimpleNamespace(
            transcriptions=SimpleNamespace(create=mock_create)
        )
    )

    monkeypatch.setattr(
        transcription, "get_whisper_client", lambda: mock_client
    )

    result = transcription.transcribe_audio_bytes(
        b"audio", "english.wav", model="whisper"
    )

    assert result["success"] is True
    assert result["selected_model"] == "whisper"
    assert result["transcription"] == "Hello world."
    assert result["language"] == "en"
    assert result["duration_seconds"] == 3.5


def test_indic_transcription_and_translation(monkeypatch):
    monkeypatch.setattr(
        transcription, "convert_audio", lambda *args: (b"wav-data", 4.0)
    )

    mock_client = SimpleNamespace(
        predict=lambda *args, **kwargs: (
            "  ನಮಸ್ಕಾರ  ",
            "  Hello  ",
            "Kannada",
        )
    )

    monkeypatch.setattr(
        transcription, "get_indic_client", lambda: mock_client
    )
    monkeypatch.setattr(
        transcription, "handle_file", lambda path: path
    )

    result = transcription.transcribe_audio_bytes(
        b"audio",
        "kannada.wav",
        language="kn",
        model="indic",
    )

    assert result["success"] is True
    assert result["selected_model"] == "indic"
    assert result["transcription"] == "ನಮಸ್ಕಾರ"
    assert result["translation"] == "Hello"
    assert result["detected_language"] == "Kannada"
    assert result["language"] == "kn"


def test_indic_empty_translation_uses_fallback(monkeypatch):
    monkeypatch.setattr(
        transcription, "convert_audio", lambda *args: (b"wav-data", 2.0)
    )

    mock_client = SimpleNamespace(
        predict=lambda *args, **kwargs: (
            "ನಮಸ್ಕಾರ",
            "",
            "Kannada",
        )
    )

    monkeypatch.setattr(
        transcription, "get_indic_client", lambda: mock_client
    )
    monkeypatch.setattr(
        transcription, "handle_file", lambda path: path
    )

    result = transcription.transcribe_audio_bytes(
        b"audio", "kannada.wav", language="kn", model="indic"
    )

    assert result["transcription"] == "ನಮಸ್ಕಾರ"
    assert result["translation"] == "English translation is unavailable."


def test_indic_service_error_is_handled(monkeypatch):
    monkeypatch.setattr(
        transcription, "convert_audio", lambda *args: (b"wav-data", 2.0)
    )

    mock_client = SimpleNamespace(
        predict=lambda *args, **kwargs: (_ for _ in ()).throw(
            Exception("Simulated service failure")
        )
    )

    monkeypatch.setattr(
        transcription, "get_indic_client", lambda: mock_client
    )
    monkeypatch.setattr(
        transcription, "handle_file", lambda path: path
    )

    with pytest.raises(
        RuntimeError,
        match="Indic transcription and translation failed",
    ):
        transcription.transcribe_audio_bytes(
            b"audio", "kannada.wav", language="kn", model="indic"
        )


def test_all_expected_languages_are_configured():
    expected = {
        "auto", "en", "as", "bn", "brx", "doi", "gu", "hi",
        "kn", "ks", "kok", "mai", "ml", "mni", "mr", "ne",
        "or", "pa", "sa", "sat", "sd", "ta", "te", "ur",
        "bho", "bhb",
    }

    assert set(transcription.HF_LANGUAGES) == expected
