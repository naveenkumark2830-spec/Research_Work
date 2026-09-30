import os
import tempfile
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import FileResponse
from pydantic import BaseModel
from app.jarvis.schemas import JarvisRequest, JarvisResponse
from app.jarvis.orchestrator import JarvisOrchestrator
from app.jarvis.hdfs_adapter import ExistingHDFSAdapter
from app.jarvis.voice import VoiceService
from app.jarvis.rag import LocalRAG

router = APIRouter(prefix='/api/v1/jarvis', tags=['JARVIS'])
jarvis = JarvisOrchestrator(ExistingHDFSAdapter())
voice = VoiceService()
rag = LocalRAG()


class RAGQueryRequest(BaseModel):
    query: str
    top_k: int = 3


@router.post('/chat', response_model=JarvisResponse)
def chat(r: JarvisRequest):
    return jarvis.handle(r)


@router.post('/voice/transcribe')
async def transcribe(file: UploadFile = File(...)):
    p = tempfile.NamedTemporaryFile(delete=False, suffix='.webm').name
    try:
        with open(p, 'wb') as f:
            f.write(await file.read())
        return {'text': voice.transcribe(p)}
    except Exception as e:
        raise HTTPException(503, str(e))
    finally:
        try:
            os.remove(p)
        except OSError:
            pass


@router.post('/voice/speak')
def speak(payload: dict):
    text = payload.get('text', '').strip()
    if not text:
        raise HTTPException(422, 'text is required')
    p = tempfile.NamedTemporaryFile(delete=False, suffix='.mp3').name
    try:
        voice.synthesize(text, p)
        return FileResponse(p, media_type='audio/mpeg')
    except Exception as e:
        raise HTTPException(503, str(e))


@router.post('/rag/query')
def query_rag(req: RAGQueryRequest):
    hits = rag.retrieve(req.query, top_k=req.top_k)
    return {"query": req.query, "results": hits}
