import os
import requests


class ExistingHDFSAdapter:
    def __init__(self):
        self.base = os.getenv('JARVIS_EXISTING_BACKEND_URL', 'http://127.0.0.1:8000').rstrip('/')

    def _post(self, path: str, user_id: str, payload: dict = None):
        try:
            r = requests.post(
                self.base + path,
                headers={'X-User-Id': user_id},
                json=payload or {},
                timeout=5
            )
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    def _get(self, path: str, user_id: str):
        try:
            r = requests.get(
                self.base + path,
                headers={'X-User-Id': user_id},
                timeout=5
            )
            r.raise_for_status()
            return r.json()
        except Exception:
            return None

    def write_file(self, session_id: str, user_id: str = "test-user", file_size_mb: int = 500, block_size_mb: int = 128, replication_factor: int = 3, path: str = "input/jarvis_data.bin", size_bytes: int = None, **kwargs):
        if size_bytes:
            file_size_mb = size_bytes // (1024 * 1024)
        cfg = {
            'session_id': session_id,
            'user_id': user_id,
            'config': {
                'file_size_bytes': file_size_mb * 1024 * 1024,
                'block_size_bytes': block_size_mb * 1024 * 1024,
                'replication_factor': replication_factor,
                'data_node_count': 5,
                'data_node_capacity_bytes': 100 * 1024**3,
                'rack_count': 1,
                'rack_aware': False,
                'heartbeat_interval': 3
            }
        }
        self._post('/api/v1/simulation/hdfs/cluster', user_id, cfg)
        result = self._post(
            f'/api/v1/simulation/hdfs/sessions/{session_id}/write',
            user_id,
            {'user_id': user_id, 'path': path, 'size_bytes': size_bytes or (file_size_mb * 1024 * 1024)}
        )
        if not isinstance(result, dict):
            result = {'raw': result}
        result['block_count'] = (file_size_mb + block_size_mb - 1) // block_size_mb
        return result

    def get_state(self, session_id: str, user_id: str):
        for path in (f'/api/v1/simulation/hdfs/sessions/{session_id}', f'/api/v1/sessions/{session_id}/state'):
            res = self._get(path, user_id)
            if res:
                return res
        return {}

    def pause(self, session_id: str, user_id: str):
        return self._post(f'/api/v1/sessions/{session_id}/pause', user_id) or {}

    def resume(self, session_id: str, user_id: str):
        return self._post(f'/api/v1/sessions/{session_id}/resume', user_id) or {}

    def restart(self, session_id: str, user_id: str):
        return self._post(f'/api/v1/sessions/{session_id}/restart', user_id) or {}

    def kill_datanode(self, session_id: str, node_id: str, user_id: str = ""):
        return self._post(f'/api/v1/simulation/hdfs/sessions/{session_id}/failure', user_id, {'node_id': node_id}) or {}

    def recover_datanode(self, session_id: str, node_id: str, user_id: str = ""):
        return self._post(f'/api/v1/simulation/hdfs/sessions/{session_id}/recovery', user_id, {'node_id': node_id}) or {}

    def create_cluster(self, session_id: str, user_id: str = "", config: dict = None):
        return self._post('/api/v1/simulation/hdfs/cluster', user_id, {'session_id': session_id, 'user_id': user_id, 'config': config or {}}) or {}
