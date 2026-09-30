# AI-Assisted Interactive Hadoop Execution & Learning Simulator

## Overview & Purpose
The **AI-Assisted Interactive Hadoop Execution & Learning Simulator** is a stateful, AI-driven, voice-interactive learning and execution platform designed for Hadoop distributed storage and processing environments. It combines deterministic distributed system simulation with natural language AI assistance, real-time voice interaction (including voice interruption/barging-in), dynamic workflow visualization, user note-taking RAG, and hands-on scenario assessments.

## Current Implementation Stage
**Level 1 — Project Foundation**

This repository is being built incrementally. Level 1 establishes the application foundation. Hadoop simulation, AI orchestration, RAG, voice interaction, dynamic visualization, and persistent user state will be implemented in subsequent levels.

## Architectural Vision
The full system architecture will incrementally introduce:
- **Session & User Memory**: Isolated user sessions and persistent storage.
- **Deterministic Simulation Engine**: High-fidelity Hadoop cluster simulation (HDFS NameNode/DataNode, YARN ResourceManager/NodeManager, MapReduce execution).
- **AI & RAG Engine**: Contextual voice and text assistant built with Hadoop knowledge base + user note integration.
- **Voice Barging-In Engine**: Real-time STT/TTS with low-latency interruption ("Jarvis, stop") and simulation pause/resume state management.
- **Event-Driven Visualization Engine**: Dynamic UI rendering of cluster state and job events.
- **Scenario & Assessment Engine**: Interactive scenarios, failure injection (chaos engineering), and guided assessments.

---

## Project Structure
```
hadoop-ai-simulator/
│
├── backend/
│   ├── app/
│   │   ├── init.py
│   │   ├── main.py
│   │   ├── api/
│   │   │   ├── init.py
│   │   │   └── health.py
│   │   ├── core/
│   │   │   ├── init.py
│   │   │   └── config.py
│   │   ├── models/
│   │   │   └── init.py
│   │   ├── schemas/
│   │   │   └── init.py
│   │   └── services/
│   │       └── init.py
│   ├── tests/
│   │   └── test_health.py
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   └── client.ts
│   │   ├── components/
│   │   │   └── StatusIndicator.tsx
│   │   ├── types/
│   │   │   └── health.ts
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── package.json
│   ├── tsconfig.json
│   └── vite.config.ts
│
├── data/
│   ├── knowledge/
│   ├── scenarios/
│   └── assessments/
│
├── docs/
├── docker/
├── .env.example
├── .gitignore
└── README.md
```

---

## Getting Started

### Prerequisites
- **Python 3.12+**
- **Node.js 18+** and **npm**

---

### Backend Setup & Run

1. Navigate to the backend directory:
   ```bash
   cd backend
   ```

2. Create and activate a virtual environment:
   ```bash
   # Windows (PowerShell)
   python -m venv .venv
   .\.venv\Scripts\Activate.ps1

   # Linux/macOS
   python3 -m venv .venv
   source .venv/bin/activate
   ```

3. Install backend dependencies:
   ```bash
   pip install -r requirements.txt
   ```

4. Run the FastAPI development server:
   ```bash
   python -m uvicorn app.main:app --reload --port 8000
   ```
   - API Root: [http://localhost:8000/](http://localhost:8000/)
   - Health Endpoint: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)
   - OpenAPI Docs: [http://localhost:8000/docs](http://localhost:8000/docs)

---

### Running Backend Tests

Run pytest from the `backend` directory:
```bash
cd backend
python -m pytest
```

---

### Frontend Setup & Run

1. Navigate to the frontend directory:
   ```bash
   cd frontend
   ```

2. Install dependencies:
   ```bash
   npm install
   ```

3. Run the Vite development server:
   ```bash
   npm run dev
   ```
   - Frontend Application: [http://localhost:5173](http://localhost:5173)

---

## Current Limitations
- Level 1 provides baseline application connectivity only.
- Database persistence, Hadoop cluster simulation, AI orchestration, voice interface, and dynamic visual canvas are intentionally deferred to subsequent development levels.
