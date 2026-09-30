import os
from pathlib import Path
class LocalRAG:
    def __init__(self,path=None):
        self.path=Path(path or os.getenv('JARVIS_KNOWLEDGE_PATH','../data/Hadoop_Spark_Complete_Notes.pdf')); self.chunks=[]; self.v=None; self.m=None; self.load()
    def load(self):
        if not self.path.exists(): return
        try:
            from pypdf import PdfReader
            text='\n'.join((p.extract_text() or '') for p in PdfReader(str(self.path)).pages); w=text.split(); n=180
            self.chunks=[' '.join(w[i:i+n]) for i in range(0,len(w),n)]
            if self.chunks:
                from sklearn.feature_extraction.text import TfidfVectorizer
                self.v=TfidfVectorizer(stop_words='english'); self.m=self.v.fit_transform(self.chunks)
        except Exception: self.chunks=[]
    def retrieve(self,q,k=3):
        if self.v is None:return []
        from sklearn.metrics.pairwise import cosine_similarity
        s=cosine_similarity(self.v.transform([q]),self.m).ravel(); return [self.chunks[i] for i in s.argsort()[::-1][:k] if s[i]>0]
