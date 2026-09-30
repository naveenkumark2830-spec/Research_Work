from .schemas import *
from .llm import LLMParser
from .rag import LocalRAG
class JarvisOrchestrator:
    def __init__(self,hdfs): self.hdfs=hdfs; self.parser=LLMParser(); self.rag=LocalRAG()
    def handle(self,r):
        p=self.parser.parse(r.message); intent=Intent(p.get('intent','UNKNOWN')); c=p.get('command'); cmd=SimulationCommand(**c) if c else None
        if intent in (Intent.STOP,Intent.PAUSE):
            self.hdfs.pause(r.session_id,r.user_id); return JarvisResponse(session_id=r.session_id,intent=intent,text='Pausing the simulation. The current state is preserved.',should_pause=True)
        if intent==Intent.RESUME:
            self.hdfs.resume(r.session_id,r.user_id); return JarvisResponse(session_id=r.session_id,intent=intent,text='Continuing from the current simulation state.',should_resume=True)
        if intent==Intent.RESTART:
            self.hdfs.restart(r.session_id,r.user_id); return JarvisResponse(session_id=r.session_id,intent=intent,text='Restarting the simulation.')
        if intent==Intent.START_SIMULATION and cmd:
            result=self.hdfs.write_file(r.session_id,r.user_id,cmd.file_size_mb or 500,cmd.block_size_mb or 128,cmd.replication_factor or 3)
            return JarvisResponse(session_id=r.session_id,intent=intent,command=cmd,simulation_result=result,text=f'Starting HDFS with a {cmd.file_size_mb} MB file, {cmd.block_size_mb} MB blocks and replication factor {cmd.replication_factor}. The simulator created {result["block_count"]} blocks.',visual_actions=[VisualAction(type='SHOW_HDFS_WRITE'),VisualAction(type='SHOW_FILE',text=f'{cmd.file_size_mb} MB')])
        if intent in (Intent.ASK_QUESTION,Intent.EXPLAIN,Intent.UNKNOWN):
            state=self.hdfs.get_state(r.session_id,r.user_id); hits=self.rag.retrieve(r.message); sim=state.get('simulation',{}) if isinstance(state,dict) else {}; cfg=sim.get('configuration',{}) if isinstance(sim,dict) else {}
            q=r.message.lower()
            if 'block' in q and ('why' in q or 'how many' in q):
                size=cfg.get('file_size',cfg.get('file_size_mb')); block=cfg.get('block_size',cfg.get('block_size_mb'))
                if size and block:
                    sm=size/(1024*1024) if size>1024*1024 else size; bm=block/(1024*1024) if block>1024*1024 else block; n=int((sm+bm-1)//bm)
                    return JarvisResponse(session_id=r.session_id,intent=intent,text=f'Your current simulation uses a {int(bm)} MB block size for a {int(sm)} MB file, so it divides the file into {n} blocks. The final block contains the remaining data.',visual_actions=[VisualAction(type='HIGHLIGHT_BLOCKS',target='hdfs-blocks')],sources=['current_simulation_state'])
            text=('Based on your Hadoop notes: '+' '.join(hits[0].split()[:100])) if hits else 'I need more information from the current simulation or Hadoop knowledge to answer that precisely.'
            return JarvisResponse(session_id=r.session_id,intent=intent,text=text,visual_actions=[VisualAction(type='FOCUS_COMPONENT',target='NameNode')] if 'namenode' in q else [])
        return JarvisResponse(session_id=r.session_id,intent=intent,text=f'I understood the request as {intent.value}.')
