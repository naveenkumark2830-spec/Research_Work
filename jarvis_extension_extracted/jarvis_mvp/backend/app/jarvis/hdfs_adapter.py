import os, requests
class ExistingHDFSAdapter:
    def __init__(self): self.base=os.getenv('JARVIS_EXISTING_BACKEND_URL','http://127.0.0.1:8000').rstrip('/')
    def _post(self,p,u,payload=None):
        r=requests.post(self.base+p,headers={'X-User-Id':u},json=payload or {},timeout=30); r.raise_for_status(); return r.json()
    def _get(self,p,u):
        r=requests.get(self.base+p,headers={'X-User-Id':u},timeout=30); r.raise_for_status(); return r.json()
    def write_file(self,s,u,file_size_mb,block_size_mb,replication_factor):
        cfg={'session_id':s,'user_id':u,'config':{'file_size_bytes':file_size_mb*1024*1024,'block_size_bytes':block_size_mb*1024*1024,'replication_factor':replication_factor,'data_node_count':5,'data_node_capacity_bytes':100*1024**3,'rack_count':1,'rack_aware':False,'heartbeat_interval':3}}
        try:self._post('/api/v1/simulation/hdfs/cluster',u,cfg)
        except Exception:pass
        result=self._post(f'/api/v1/simulation/hdfs/sessions/{s}/write',u,{'user_id':u,'path':'input/jarvis_data.bin','size_bytes':file_size_mb*1024*1024})
        if not isinstance(result,dict):result={'raw':result}
        result['block_count']=(file_size_mb+block_size_mb-1)//block_size_mb
        return result
    def get_state(self,s,u):
        for p in (f'/api/v1/simulation/hdfs/sessions/{s}',f'/api/v1/sessions/{s}/state'):
            try:return self._get(p,u)
            except Exception:pass
        return {}
    def pause(self,s,u): return self._post(f'/api/v1/sessions/{s}/pause',u)
    def resume(self,s,u): return self._post(f'/api/v1/sessions/{s}/resume',u)
    def restart(self,s,u): return self._post(f'/api/v1/sessions/{s}/restart',u)
