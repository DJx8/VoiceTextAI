import pytest
from fastapi.testclient import TestClient

from backend.main import app
import backend.main as main_module


@pytest.fixture
def client():
    return TestClient(app)


def test_health_endpoint(client):
    response = client.get("/health")

    assert response.status_code == 200
    assert response.json()["status"] == "running"
    assert response.json()["application"] == "VoiceText AI"


def test_successful_indic_transcription(client, monkeypatch):
    def mock_transcribe(**kwargs):
        assert kwargs["language"] == "kn"
        assert kwargs["model"] == "indic"

        return {
            "success": True,
            "transcription": "ನಮಸ್ಕಾರ",
            "translation": "Hello",
            "detected_language": "Kannada",
        }

    monkeypatch.setattr(
        main_module, "transcribe_audio_bytes", mock_transcribe
    )

    response = client.post(
        "/transcribe",
        files={"file": ("kannada.wav", b"fake-audio", "audio/wav")},
        data={"model": "indic", "language": "kn"},
    )

    assert response.status_code == 200
    assert response.json()["transcription"] == "ನಮಸ್ಕಾರ"
    assert response.json()["translation"] == "Hello"


def test_whisper_forces_english(client, monkeypatch):
    def mock_transcribe(**kwargs):
        assert kwargs["model"] == "whisper"
        assert kwargs["language"] == "en"

        return {
            "success": True,
            "transcription": "Hello world",
            "language": "en",
        }

    monkeypatch.setattr(
        main_module, "transcribe_audio_bytes", mock_transcribe
    )

    response = client.post(
        "/transcribe",
        files={"file": ("english.wav", b"fake-audio", "audio/wav")},
        data={"model": "whisper", "language": "ml"},
    )

    assert response.status_code == 200
    assert response.json()["transcription"] == "Hello world"


def test_unsupported_file_format(client):
    response = client.post(
        "/transcribe",
        files={"file": ("document.txt", b"not-audio", "text/plain")},
        data={"model": "indic", "language": "auto"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported audio format."


def test_invalid_model(client):
    response = client.post(
        "/transcribe",
        files={"file": ("test.wav", b"fake-audio", "audio/wav")},
        data={"model": "invalid", "language": "auto"},
    )

    assert response.status_code == 400
    assert "Invalid model" in response.json()["detail"]


def test_unsupported_language(client):
    response = client.post(
        "/transcribe",
        files={"file": ("test.wav", b"fake-audio", "audio/wav")},
        data={"model": "indic", "language": "xyz"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Unsupported language selection."


def test_empty_audio_upload(client):
    response = client.post(
        "/transcribe",
        files={"file": ("empty.wav", b"", "audio/wav")},
        data={"model": "indic", "language": "auto"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Uploaded file is empty."


def test_transcription_value_error_returns_400(client, monkeypatch):
    def mock_transcribe(**kwargs):
        raise ValueError("Invalid audio data.")

    monkeypatch.setattr(
        main_module, "transcribe_audio_bytes", mock_transcribe
    )

    response = client.post(
        "/transcribe",
        files={"file": ("test.wav", b"fake-audio", "audio/wav")},
        data={"model": "indic", "language": "auto"},
    )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid audio data."


def test_transcription_service_error_returns_502(client, monkeypatch):
    def mock_transcribe(**kwargs):
        raise RuntimeError("Simulated service failure.")

    monkeypatch.setattr(
        main_module, "transcribe_audio_bytes", mock_transcribe
    )

    response = client.post(
        "/transcribe",
        files={"file": ("test.wav", b"fake-audio", "audio/wav")},
        data={"model": "indic", "language": "auto"},
    )

    assert response.status_code == 502
    assert response.json()["detail"] == "Simulated service failure."
