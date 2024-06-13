from ui.utils import initialise_azure_openai_speech


def transcribe_audio(filepath: str, language: str = "nl") -> str:
    client = initialise_azure_openai_speech()
    audio_file = open(filepath, "rb")
    transcript = client.audio.transcriptions.create(
        model="whisper-1", file=audio_file, language=language
    )

    return transcript.text
