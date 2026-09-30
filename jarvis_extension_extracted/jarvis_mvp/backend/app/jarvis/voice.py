import os
class VoiceService:
    def __init__(self):
        self.client=None
        if os.getenv('OPENAI_API_KEY'):
            try:
                from openai import OpenAI; self.client=OpenAI()
            except Exception:pass
    def transcribe(self,path):
        if not self.client:raise RuntimeError('OPENAI_API_KEY is required for STT')
        with open(path,'rb') as f:return self.client.audio.transcriptions.create(model=os.getenv('JARVIS_STT_MODEL','whisper-1'),file=f).text
    def synthesize(self,text,path):
        if not self.client:raise RuntimeError('OPENAI_API_KEY is required for TTS')
        with self.client.audio.speech.with_streaming_response.create(model=os.getenv('JARVIS_TTS_MODEL','tts-1'),voice=os.getenv('JARVIS_TTS_VOICE','alloy'),input=text) as r:r.stream_to_file(path)
