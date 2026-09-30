from __future__ import annotations

import json
import re
from typing import Any

from app.ai.provider import LLMRequest
from app.ai.router import LLMRouter

from .rag import TeddyRAG
from .schemas import (
    SimulationAction,
    TeddyPlan,
    TeddyRequest,
    TeddyResponse,
    VisualizationStep,
)


SYSTEM_PROMPT = """
You are Teddy, an intelligent Hadoop learning assistant.

Your job is to answer the user's question using the supplied RAG knowledge
and, when appropriate, control the Hadoop simulator.

IMPORTANT RULES:

1. The RAG context is REFERENCE MATERIAL.
2. NEVER copy the RAG context directly into "answer".
3. NEVER include "[Source: ...]" blocks in "answer".
4. Synthesize a clear, concise educational explanation.
5. Preserve important technical details from the supplied context.
6. Do not invent facts that are not supported by the supplied context.
7. If the user asks for a simulation, create a simulation action.
8. If the user only asks a conceptual question, simulation_required=false.
9. visualization contains instructions for the frontend.
10. voice_text must sound natural when spoken by Teddy.
11. Return ONLY valid JSON.

SUPPORTED SIMULATION ACTIONS:

create_cluster
write_file
kill_datanode
recover_datanode
recover_under_replicated_blocks
none

SUPPORTED VISUALIZATION TYPES:

show_cluster
show_file
create_blocks
replicate_blocks
show_namenode
show_datanodes
highlight_block
show_pipeline
show_failure
show_recovery
explain

OUTPUT FORMAT:

{
  "intent": "short description",
  "answer": "clean synthesized answer for the user",
  "voice_text": "natural spoken explanation",
  "simulation_required": false,
  "simulation_action": {
      "action": "none",
      "parameters": {}
  },
  "visualization": [],
  "sources": []
}

For sources, return only the document names that actually contributed
to the answer.

For example, if the user asks:

"What does the NameNode do?"

Do NOT return the retrieved document text.

Instead produce a concise answer such as:

"The NameNode is the master component of HDFS. It manages metadata
such as file names, block IDs, block locations, permissions and
replication information. The actual file blocks are stored on
DataNodes."

Then create an appropriate visualization plan.
"""


class TeddyOrchestrator:
    """
    Main intelligence coordinator for Teddy.

    Flow:

        User
          ↓
        RAG
          ↓
        LLM
          ↓
        Structured Teddy Plan
          ↓
        Simulation
          ↓
        Visualization instructions
    """

    def __init__(
        self,
        llm_router: LLMRouter,
        rag: TeddyRAG,
        hdfs_service=None,
    ):
        self.llm = llm_router
        self.rag = rag
        self.hdfs_service = hdfs_service

    async def process(
        self,
        request: TeddyRequest,
    ) -> TeddyResponse:

        # ---------------------------------------------------------
        # 1. Retrieve Hadoop knowledge
        # ---------------------------------------------------------

        rag_context = self.rag.build_context(
            request.message,
            top_k=5,
        )

        # ---------------------------------------------------------
        # 2 & 3. Ask LLM to reason over knowledge (with quota safety net)
        # ---------------------------------------------------------

        prompt = f"""
USER QUESTION:

{request.message}

==================================================
RETRIEVED HADOOP KNOWLEDGE
==================================================

{rag_context}

==================================================
TASK
==================================================

Use the retrieved knowledge as reference material.

Answer the user's question yourself.

DO NOT copy the retrieved text directly.

DO NOT include source markers such as:

[Source: ...]

inside the answer.

Instead:

1. Understand the user's question.
2. Extract the relevant Hadoop facts.
3. Synthesize a clean explanation.
4. Determine whether simulation is required.
5. If simulation is required, select the correct supported action.
6. Create visualization instructions.
7. Create natural voice text.
8. Return ONLY valid JSON matching the required schema.
"""

        llm_request = LLMRequest(
            prompt=prompt,
            system_prompt=SYSTEM_PROMPT,
            temperature=0.2,
            max_tokens=2500,
        )

        try:
            response = await self.llm.generate(llm_request)
            plan_data = self._extract_json(response.text)
            plan = TeddyPlan.model_validate(plan_data)
        except Exception:
            plan = self._generate_fallback_plan(request.message, rag_context)

        # ---------------------------------------------------------
        # 4. Execute simulation if requested
        # ---------------------------------------------------------

        simulation_state = None

        if (
            plan.simulation_required
            and plan.simulation_action.action != "none"
            and self.hdfs_service is not None
        ):
            simulation_state = await self._execute_simulation(
                request,
                plan.simulation_action,
            )

        # ---------------------------------------------------------
        # 5. Build dynamic visualization scene (Stage 9.2)
        # ---------------------------------------------------------

        visualization_scene = None
        if self.hdfs_service is not None and hasattr(self.hdfs_service, "session_repo"):
            try:
                hdfs_state = self.hdfs_service.session_repo.get_state(request.session_id)
                if hdfs_state:
                    from .visualization_scene import build_visualization_scene
                    visualization_scene = build_visualization_scene(
                        hdfs_state,
                        question=request.message,
                        teddy_response=plan.answer,
                    )
            except Exception:
                pass
        elif simulation_state:
            try:
                from .visualization_scene import build_visualization_scene
                visualization_scene = build_visualization_scene(
                    simulation_state,
                    question=request.message,
                    teddy_response=plan.answer,
                )
            except Exception:
                pass

        # ---------------------------------------------------------
        # 6. Return complete Teddy response
        # ---------------------------------------------------------

        return TeddyResponse(
            session_id=request.session_id,
            user_message=request.message,
            plan=plan,
            simulation_state=simulation_state,
            visualization_scene=visualization_scene,
        )

    # =============================================================
    # JSON extraction
    # =============================================================

    @staticmethod
    def _extract_json(text: str) -> dict[str, Any]:

        text = text.strip()

        # Direct JSON
        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        # Markdown JSON block
        match = re.search(
            r"```json\s*(.*?)\s*```",
            text,
            re.DOTALL | re.IGNORECASE,
        )

        if match:
            return json.loads(match.group(1))

        # Find first JSON object
        start = text.find("{")
        end = text.rfind("}")

        if start != -1 and end != -1:
            return json.loads(text[start : end + 1])

        raise ValueError(
            "Teddy LLM returned an invalid structured response"
        )

    # =============================================================
    # Fallback plan generation for rate limits / offline mode
    # =============================================================

    @staticmethod
    def _generate_fallback_plan(message: str, rag_context: str) -> TeddyPlan:
        msg_lower = message.lower()
        sim_req = any(
            word in msg_lower
            for word in ["create", "write", "kill", "fail", "recover", "simulate", "start"]
        )

        sim_action = SimulationAction(action="none")
        if "kill" in msg_lower or "fail" in msg_lower:
            sim_action = SimulationAction(action="kill_datanode", parameters={"node_id": "datanode-3"})
        elif "recover" in msg_lower:
            sim_action = SimulationAction(action="recover_datanode", parameters={"node_id": "datanode-3"})
        elif "create" in msg_lower or "write" in msg_lower:
            sim_action = SimulationAction(action="write_file", parameters={"path": "/teddy/demo-file", "size_bytes": 1024 * 1024})

        answer_summary = ""
        voice_summary = ""

        # 1. Attempt to extract directly from RAG Context
        if rag_context and rag_context.strip():
            # Clean source tags from RAG context
            lines = []
            for line in rag_context.split("\n"):
                line_str = line.strip()
                if line_str and not line_str.startswith("[Source:") and not line_str == "---":
                    lines.append(line_str)
            if lines:
                extracted = " ".join(lines)
                if len(extracted) > 400:
                    extracted = extracted[:400] + "..."
                answer_summary = extracted
                voice_summary = extracted[:200]

        # 2. Topic-based fallback synthesis if RAG context did not yield text
        if not answer_summary:
            if "heartbeat" in msg_lower:
                answer_summary = "A Heartbeat in HDFS is a periodic signal sent by each DataNode to the NameNode (approximately every 3 seconds) to report node health, disk capacity, and operational status. If the NameNode does not receive a heartbeat from a DataNode within 10 minutes, it marks the DataNode as dead and automatically initiates block re-replication onto healthy nodes."
                voice_summary = "Heartbeats are periodic signals sent by DataNodes to the NameNode every 3 seconds to report health and disk status."
            elif "block" in msg_lower:
                answer_summary = "HDFS divides large files into fixed-size blocks (default 128 MB in HDFS 2.x/3.x). Storing data in large blocks minimizes NameNode metadata memory footprint and optimizes sequential disk I/O performance."
                voice_summary = "HDFS splits files into 128 MB blocks to optimize storage efficiency and sequential read-write throughput."
            elif "write" in msg_lower or "pipeline" in msg_lower:
                answer_summary = "In the HDFS write pipeline, the client requests block allocation from the NameNode. The NameNode returns a list of target DataNodes, and the client streams data blocks to the primary DataNode, which automatically replicates them downstream to secondary DataNodes."
                voice_summary = "The client streams 128 MB blocks to the primary DataNode, which replicates them downstream to secondary DataNodes in sequence."
            elif "namenode" in msg_lower or "master" in msg_lower:
                answer_summary = "The NameNode is the master daemon in HDFS. It manages the file system namespace tree, directory structure, and block-to-DataNode mappings, but does not store raw file bytes."
                voice_summary = "The NameNode is the master node managing metadata, file namespace, and block locations across the HDFS cluster."
            elif "datanode" in msg_lower or "worker" in msg_lower or "storage" in msg_lower:
                answer_summary = "DataNodes are worker daemons in HDFS that store file block data on local disks and periodically send heartbeats and block reports to the NameNode."
                voice_summary = "DataNodes store block data on disk and periodically send heartbeats and block reports to the NameNode."
            elif "secondary" in msg_lower or "checkpoint" in msg_lower:
                answer_summary = "The Secondary NameNode periodically merges the EditLog (transaction log) with the FsImage metadata snapshot to create updated checkpoints, preventing EditLog from growing excessively."
                voice_summary = "The Secondary NameNode merges the EditLog with FsImage to create periodic metadata checkpoints."
            elif "replication" in msg_lower or "replica" in msg_lower:
                answer_summary = "HDFS automatically replicates each data block across multiple DataNodes (default replication factor = 3) to guarantee high availability and fault tolerance."
                voice_summary = "HDFS maintains a default replication factor of 3 to ensure data durability even during node failures."
            else:
                answer_summary = "Apache HDFS is a distributed, fault-tolerant file system that splits large files into blocks (128 MB by default) and replicates them across multiple DataNodes managed by a central NameNode."
                voice_summary = "HDFS is a fault-tolerant distributed file system designed for scalable, high-throughput data processing."

        return TeddyPlan(
            intent="Hadoop Storage & Simulation Query",
            answer=answer_summary,
            voice_text=voice_summary,
            simulation_required=sim_req,
            simulation_action=sim_action,
            visualization=[
                VisualizationStep(
                    type="show_namenode",
                    title="NameNode Metadata",
                    description="NameNode tracks cluster health and block distribution.",
                    duration_ms=1200,
                )
            ],
            sources=["Hadoop_Spark_Complete_Notes.pdf"],
        )



    # =============================================================
    # HDFS simulation execution
    # =============================================================

    async def _execute_simulation(
        self,
        request: TeddyRequest,
        action: SimulationAction,
    ) -> dict[str, Any]:

        if self.hdfs_service is None:
            return {}

        from .executor import TeddyActionExecutor

        executor = TeddyActionExecutor(self.hdfs_service)
        state = executor.execute(
            session_id=request.session_id,
            action=action,
            user_id=request.user_id,
        )

        return self._serialize_state(state)

    # =============================================================
    # Convert simulation state into API-safe dictionary
    # =============================================================

    @staticmethod
    def _serialize_state(state: Any) -> dict[str, Any]:

        if state is None:
            return {}

        if hasattr(state, "model_dump"):
            return state.model_dump()

        if hasattr(state, "dict"):
            return state.dict()

        if hasattr(state, "__dict__"):
            return state.__dict__

        return {"state": str(state)}


# Legacy wrapper for backward compatibility with app/api/jarvis.py
class JarvisOrchestrator(TeddyOrchestrator):
    def __init__(self, hdfs_service=None, llm_router=None, rag=None):
        if llm_router is None or rag is None:
            from .provider import create_teddy_orchestrator
            orch = create_teddy_orchestrator(hdfs_service=hdfs_service)
            super().__init__(llm_router=orch.llm, rag=orch.rag, hdfs_service=hdfs_service)
        else:
            super().__init__(llm_router=llm_router, rag=rag, hdfs_service=hdfs_service)

    def handle(self, r: Any) -> Any:
        import asyncio
        from .schemas import TeddyRequest, Intent, VisualAction, SimulationCommand, JarvisResponse

        teddy_req = TeddyRequest(session_id=r.session_id, user_id=r.user_id, message=r.message)

        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                import nest_asyncio
                nest_asyncio.apply()
                teddy_res = loop.run_until_complete(self.process(teddy_req))
            else:
                teddy_res = loop.run_until_complete(self.process(teddy_req))
        except Exception:
            teddy_res = asyncio.run(self.process(teddy_req))

        plan = teddy_res.plan

        intent_map = {
            "explain": Intent.EXPLAIN,
            "create_cluster": Intent.START_SIMULATION,
            "write_file": Intent.START_SIMULATION,
            "kill_datanode": Intent.FAILURE_INJECTION,
            "recover_datanode": Intent.FAILURE_INJECTION,
            "recover_under_replicated_blocks": Intent.FAILURE_INJECTION,
        }

        intent_val = Intent.EXPLAIN
        if plan.simulation_action and plan.simulation_action.action in intent_map:
            intent_val = intent_map[plan.simulation_action.action]
        elif "quiz" in r.message.lower():
            intent_val = Intent.QUIZ
        elif "stop" in r.message.lower():
            intent_val = Intent.STOP
        elif "continue" in r.message.lower() or "resume" in r.message.lower():
            intent_val = Intent.RESUME

        visual_actions = [
            VisualAction(type=step.type, text=step.description, payload=step.data)
            for step in plan.visualization
        ]

        command = None
        if plan.simulation_action and plan.simulation_action.action != "none":
            command = SimulationCommand(
                operation=plan.simulation_action.action,
                file_size_mb=plan.simulation_action.parameters.get("size_bytes", 0) // (1024 * 1024) if plan.simulation_action.parameters.get("size_bytes") else None,
                block_size_mb=plan.simulation_action.parameters.get("block_size_mb"),
                replication_factor=plan.simulation_action.parameters.get("replication_factor"),
            )

        return JarvisResponse(
            session_id=teddy_res.session_id,
            intent=intent_val,
            text=plan.answer,
            command=command,
            visual_actions=visual_actions,
            should_speak=True,
            should_pause=intent_val in [Intent.STOP, Intent.PAUSE] or "stop" in r.message.lower(),
            should_resume=intent_val == Intent.RESUME or "continue" in r.message.lower() or "resume" in r.message.lower(),
            simulation_result=teddy_res.simulation_state,
            sources=plan.sources,
        )

