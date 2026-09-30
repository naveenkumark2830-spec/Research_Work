import json
import os
import re
from typing import Dict, Any
from app.jarvis.provider import GeminiAIProvider


class LLMParser:
    def __init__(self):
        self.gemini_provider = GeminiAIProvider()

    def parse(self, message: str, context_summary: str = None) -> Dict[str, Any]:
        parsed = self.gemini_provider.parse_user_message(message, context_summary=context_summary)
        if parsed and "intent" in parsed:
            return parsed

        return deterministic_parse(message)


def deterministic_parse(message: str) -> dict:
    m = message.lower().strip()
    if re.search(r'\b(stop|halt)\b', m):
        return {'intent': 'STOP', 'command': None, 'confidence': 1.0}
    if re.search(r'\b(pause|wait|hold on)\b', m):
        return {'intent': 'PAUSE', 'command': None, 'confidence': 1.0}
    if re.search(r'\b(continue|resume)\b', m):
        return {'intent': 'RESUME', 'command': None, 'confidence': 1.0}
    if re.search(r'\b(restart|start over|reset)\b', m):
        return {'intent': 'RESTART', 'command': None, 'confidence': 1.0}
    if 'quiz' in m:
        return {'intent': 'QUIZ', 'command': None, 'confidence': 0.95}
    if 'compare' in m and ('hadoop 1' in m or 'hadoop 2' in m or 'yarn' in m):
        return {'intent': 'COMPARE', 'command': None, 'confidence': 0.9}
    node = re.search(r'datanode[\s_-]*(\d+)', m)
    if node and re.search(r'\b(kill|fail|shutdown)\b', m):
        return {'intent': 'FAILURE_INJECTION', 'command': {'operation': 'FAIL_DATANODE', 'node_id': f'datanode-{node.group(1)}'}, 'confidence': 0.95}
    if node and re.search(r'\b(recover|restore)\b', m):
        return {'intent': 'FAILURE_INJECTION', 'command': {'operation': 'RECOVER_DATANODE', 'node_id': f'datanode-{node.group(1)}'}, 'confidence': 0.95}
    g = re.search(r'(\d+(?:\.\d+)?)\s*(gb|gib)', m)
    mb = re.search(r'(\d+(?:\.\d+)?)\s*mb', m)
    file_mb = int(float(g.group(1)) * 1024) if g else None
    block_mb = int(float(mb.group(1))) if mb else None
    rf = re.search(r'(?:replication(?:\s+factor)?|rf)\s*(?:of|=|:)?\s*(\d+)', m)
    rf_val = int(rf.group(1)) if rf else None
    if any(x in m for x in ('run', 'simulate', 'create', 'write', 'upload', 'start')) and (file_mb is not None or 'hdfs' in m or block_mb is not None):
        return {
            'intent': 'START_SIMULATION',
            'command': {
                'system': 'HDFS',
                'operation': 'WRITE_FILE',
                'file_size_mb': file_mb or 500,
                'block_size_mb': block_mb or 128,
                'replication_factor': rf_val or 3
            },
            'confidence': 0.8
        }
    if 'why' in m or 'how' in m or 'explain' in m or 'what is' in m:
        return {'intent': 'ASK_QUESTION', 'command': None, 'confidence': 0.85}
    return {'intent': 'UNKNOWN', 'command': None, 'confidence': 0.2}
