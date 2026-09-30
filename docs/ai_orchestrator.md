# LEVEL 7 — AI ORCHESTRATOR / NATURAL-LANGUAGE CONTROL LAYER

## 1. ARCHITECTURAL OVERVIEW

The Level 7 AI Orchestrator bridges natural-language user messages with the existing deterministic backend HDFS simulation engine.

```
[User Message / UI Chat Panel]
              │
              ▼ (POST /api/v1/ai/sessions/{session_id}/message)
[AIOrchestrator Application Layer]
              │
              ▼ (Construct Session-Scoped Context)
[AIContext Builder]
              │
              ▼ (Structured Response Generation)
[AIProvider (MockAIProvider / Gemini AI)]
              │
              ▼ (Strict Parameter & Security Checks)
[ActionValidator]
              │
              ▼ (Dispatch to Level 0-6 Services)
[HDFSService / StateService]
              │
              ▼
[Pure Python HDFSSimulationEngine & EventEngine]
              │
              ▼
[SQLite Persistent DB & Monotonic Events Stream]
              │
              ▼
[Frontend React App & Dynamic Canvas Visualization]
```

The AI is strictly an **ORCHESTRATOR** and never invents Hadoop simulation state. The Python `HDFSSimulationEngine` remains the single source of truth.

---

## 2. INTENT TAXONOMY

Defined in `app.ai.intent.IntentType`:
*   `EXPLAIN`: Requests for Hadoop architecture, concepts, or current live simulation events.
*   `START_SIMULATION`: Command to initiate simulation execution.
*   `MODIFY_SIMULATION`: Requests to alter parameters (block size, file size, replication factor, datanode count, speed).
*   `ASK_QUESTION`: General questions about Hadoop.
*   `PAUSE`: Interrupt or pause running simulation.
*   `STOP`: Interrupt or pause running simulation (maps to STOP intent).
*   `RESUME`: Resume paused simulation execution.
*   `RESTART`: Reset simulation lifecycle to clean initialization.
*   `COMPARE`: Comparative questions between configurations.
*   `FAILURE_INJECTION`: DataNode crash/kill operations.
*   `SCALE`: Scale out/in DataNode count.
*   `ZOOM`: Canvas zoom requests.
*   `SHOW_COMPONENT`: Component highlight requests.
*   `QUIZ`: Quiz requests (reserved for future levels).
*   `UNKNOWN`: Unrecognized inputs.

---

## 3. ACTION TAXONOMY

Defined in `app.ai.action.ActionType`:
*   `UPDATE_CONFIG`: Modify `file_size_mb`, `block_size_mb`, `replication_factor`, `datanode_count`, `reducer_count`, `simulation_speed`.
*   `START_SIMULATION`: Triggers write simulation.
*   `PAUSE_SIMULATION`: Pauses active simulation.
*   `RESUME_SIMULATION`: Resumes paused simulation.
*   `RESTART_SIMULATION`: Clears cluster and re-initializes.
*   `SET_SPEED`: Adjusts simulation clock speed ($0.1\text{x} \dots 10.0\text{x}$).
*   `ADD_DATANODE`: Scale out cluster by adding DataNode(s).
*   `REMOVE_DATANODE`: Scale in cluster by removing target DataNode.
*   `KILL_DATANODE`: Inject node failure on target DataNode.
*   `RECOVER_DATANODE`: Recover failed DataNode and restore replicas.
*   `SHOW_COMPONENT`: Highlight visual component.
*   `EXPLAIN_COMPONENT`: Explain selected component.
*   `ASK_HADOOP_QUESTION`: General concept response.
*   `COMPARE_CONFIGURATIONS`: Comparative output.
*   `NO_OP`: No state mutation required.

---

## 4. CONTEXT MODEL (`AIContext`)

Structured context model passed to AI providers:
```json
{
  "user_message": "Kill DataNode 3",
  "user_context": { "user_id": "usr_123", "display_name": "Naveen" },
  "session_context": { "session_id": "ses_456", "topic": "HDFS Fundamentals" },
  "conversation_context": { "recent_messages": [...] },
  "simulation_state": { "status": "RUNNING", "datanodes": {...} },
  "visualization_state": { "selected_component": "datanode-3" },
  "event_context": { "recent_events": [...], "current_sequence": 42 }
}
```

---

## 5. PROVIDER ABSTRACTION & DETERMINISTIC MOCK PROVIDER

*   `AIProvider` interface enforces `generate_structured_response(context: AIContext) -> IntentResult`.
*   `MockAIProvider`: Rule-based deterministic provider that handles all Level 7 expressions offline without API keys, ensuring 100% test reproducibility.
*   `GoogleAIProvider`: Activated when `AI_API_KEY` is present in environment settings (`AI_PROVIDER="google"`).

---

## 6. VALIDATION & SECURITY PIPELINE

1.  **Code Injection Prevention**: `ActionValidator` rejects parameters containing forbidden terms (`eval`, `exec`, `shell`, `script`, `code`, `sql`, `command`).
2.  **Schema Bounds Check**: Validates numerical ranges for parameters (`file_size_mb`, `block_size_mb`, `replication_factor`, `datanode_count`, `reducer_count`, `simulation_speed`).
3.  **Business Logic Validation**: HDFSService enforces cross-field rules (e.g. `replication_factor <= datanode_count`).
4.  **Backend Truth Rule**: If backend validation fails, `action_executed` is set to `false`, and the response explicitly reports the backend rejection message.

---

## 7. REST API CONTRACT

```http
POST /api/v1/ai/sessions/{session_id}/message
Header: X-User-Id: {user_id}
Content-Type: application/json

{
  "message": "Set the block size to 256 MB.",
  "visualization_context": {
    "selected_component": "datanode-3"
  }
}
```

Response:
```json
{
  "session_id": "ses_456",
  "intent": "MODIFY_SIMULATION",
  "action_executed": true,
  "response": "Updating simulation configuration parameters: block_size_mb=256.",
  "action": {
    "type": "UPDATE_CONFIG",
    "parameters": { "block_size_mb": 256 }
  },
  "simulation_state": {...},
  "visualization_state": {...},
  "event": {...}
}
```

---

## 8. INTEGRATION POINT FOR LEVEL 8 RAG

In Level 8, the `AIOrchestrator` context builder will interface with a Vector Database / Embeddings retriever to inject relevant chunks from user notes into `ai_context.rag_context` before invoking the LLM provider.
