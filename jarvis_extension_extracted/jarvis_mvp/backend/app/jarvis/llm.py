import json, os, re

SYSTEM='''You are the command parser for an interactive Hadoop learning simulator. Return JSON only with intent, command, confidence. Intents: EXPLAIN, START_SIMULATION, MODIFY_SIMULATION, ASK_QUESTION, PAUSE, STOP, RESUME, RESTART, COMPARE, FAILURE_INJECTION, SCALE, SHOW_COMPONENT, QUIZ, UNKNOWN. Never invent simulation results. Normalize GB to MB using 1024. For executable commands, command.operation must describe the requested operation.'''

class LLMParser:
    def __init__(self):
        self.client=None
        if os.getenv('OPENAI_API_KEY'):
            try:
                from openai import OpenAI
                self.client=OpenAI()
            except Exception: pass
    def parse(self,message):
        if self.client:
            try:
                r=self.client.chat.completions.create(model=os.getenv('JARVIS_LLM_MODEL','gpt-4o-mini'),temperature=0,response_format={'type':'json_object'},messages=[{'role':'system','content':SYSTEM},{'role':'user','content':message}])
                return json.loads(r.choices[0].message.content)
            except Exception: pass
        return deterministic_parse(message)

def deterministic_parse(message):
    m=message.lower().strip()
    if re.search(r'\b(stop|halt)\b',m): return {'intent':'STOP','command':None,'confidence':1}
    if re.search(r'\b(pause|wait|hold on)\b',m): return {'intent':'PAUSE','command':None,'confidence':1}
    if re.search(r'\b(continue|resume)\b',m): return {'intent':'RESUME','command':None,'confidence':1}
    if re.search(r'\b(restart|start over|reset)\b',m): return {'intent':'RESTART','command':None,'confidence':1}
    if 'quiz' in m: return {'intent':'QUIZ','command':None,'confidence':.95}
    if 'compare' in m and ('hadoop 1' in m or 'hadoop 2' in m or 'yarn' in m): return {'intent':'COMPARE','command':None,'confidence':.9}
    node=re.search(r'datanode[\s_-]*(\d+)',m)
    if node and re.search(r'\b(kill|fail|shutdown)\b',m): return {'intent':'FAILURE_INJECTION','command':{'operation':'FAIL_DATANODE','node_id':f'datanode-{node.group(1)}'},'confidence':.95}
    if node and re.search(r'\b(recover|restore)\b',m): return {'intent':'FAILURE_INJECTION','command':{'operation':'RECOVER_DATANODE','node_id':f'datanode-{node.group(1)}'},'confidence':.95}
    g=re.search(r'(\d+(?:\.\d+)?)\s*(gb|gib)',m); mb=re.search(r'(\d+(?:\.\d+)?)\s*mb',m)
    file_mb=int(float(g.group(1))*1024) if g else None
    block_mb=int(float(mb.group(1))) if mb else None
    rf=re.search(r'(?:replication(?:\s+factor)?|rf)\s*(?:of|=|:)?\s*(\d+)',m)
    rf=int(rf.group(1)) if rf else None
    if any(x in m for x in ('run','simulate','create','write','upload','start')) and (file_mb is not None or 'hdfs' in m):
        return {'intent':'START_SIMULATION','command':{'system':'HDFS','operation':'WRITE_FILE','file_size_mb':file_mb or 500,'block_size_mb':block_mb or 128,'replication_factor':rf or 3},'confidence':.8}
    if 'why' in m or 'how' in m or 'explain' in m or 'what is' in m: return {'intent':'ASK_QUESTION','command':None,'confidence':.85}
    return {'intent':'UNKNOWN','command':None,'confidence':.2}
