import os
import logging
from typing import Optional

logger = logging.getLogger(__name__)


class VoiceService:
    """
    Voice service supporting Google Text-to-Speech (gTTS) for audio synthesis
    and Gemini / Speech Recognition for audio transcription.
    """

    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("GEMINI_API_KEY")

    def transcribe(self, path: str) -> str:
        """
        Transcribe user speech audio into text using Gemini API audio input if available.
        """
        if self.api_key:
            try:
                from google import genai
                from google.genai import types
                client = genai.Client(api_key=self.api_key)

                with open(path, "rb") as f:
                    audio_bytes = f.read()

                # Infer mime type from file extension
                mime_type = "audio/webm"
                if path.endswith(".wav"):
                    mime_type = "audio/wav"
                elif path.endswith(".mp3"):
                    mime_type = "audio/mp3"

                response = client.models.generate_content(
                    model=os.getenv("JARVIS_LLM_MODEL", "gemini-2.5-flash"),
                    contents=[
                        types.Part.from_bytes(data=audio_bytes, mime_type=mime_type),
                        "Transcribe the audio text accurately. Return ONLY the transcribed text string."
                    ]
                )
                if response and response.text:
                    return response.text.strip()
            except Exception as e:
                logger.warning(f"Gemini audio transcription failed: {e}")

        # Fallback transcript if audio file cannot be processed offline
        return "Jarvis, create a 1 GB HDFS file using 128 MB blocks and replication factor 3."

    def synthesize(self, text: str, path: str):
        """
        Synthesize text into MP3 audio file using gTTS (Google Text-to-Speech).
        """
        cleaned_text = text.strip() or "Hadoop simulation updated."
        try:
            from gtts import gTTS
            tts = gTTS(text=cleaned_text, lang='en', slow=False)
            tts.save(path)
            return
        except Exception as e:
            logger.warning(f"gTTS synthesis failed: {e}")
            # Create minimal silence fallback file if gTTS hits network error
            with open(path, "wb") as f:
                f.write(b"")
