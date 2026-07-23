# 👁️ K-Sight - Crime Intelligence & Investigation Platform

> **Built for the Karnataka State Police x Zoho Datathon**

K-Sight is an elite, polyglot-persistence intelligence platform designed to transform raw police records into actionable investigative intelligence. It connects the dots between isolated incidents to uncover hidden organized crime networks.

## 🚀 Key Features

- **Hybrid RAG AI Chatbot**: Powered by Google Gemini, Qdrant, and Neo4j. Ask complex questions like *"What is the MO for recent robberies?"* and the AI will scan semantic FIR narratives and graph relationships to give you cited intelligence.
- **Graph Investigator**: A ReactFlow-powered visualizer that exposes hidden syndicates by linking Suspects 🔴, Phones 🔵, Vehicles 🟢, and Incidents 🟡. Features dynamic Suspect Risk Scoring and Similar Past Cases retrieval.
- **Live Operations Map**: A geospatial heatmap plotting crime incidents to identify high-risk zones.
- **Automated Intelligence ETL**: A pipeline that automatically embeds and graphs raw FIR data from PostgreSQL into Neo4j and Qdrant.

---

## 🏗️ System Architecture

K-Sight utilizes a highly scalable, polyglot architecture to handle structured records, relationships, and semantic search simultaneously.

```mermaid
graph TD
    User([🕵️ Investigator]) -->|Interacts| UI[💻 Next.js Frontend]
    UI <-->|REST API| API[⚡ FastAPI Backend]
    
    subgraph Data Layer
        API <-->|SQL| PG[(🐘 PostgreSQL)]
        API <-->|Cypher| N4J[(🕸️ Neo4j Graph)]
        API <-->|Vectors| QD[(🌌 Qdrant DB)]
    end
    
    subgraph Intelligence Engine
        API <-->|Prompt + Context| GEMINI[🧠 Google Gemini AI]
    end
    
    subgraph ETL Pipeline
        ETL[⚙️ Python ETL Cron/Task]
        PG -->|Read Batch| ETL
        ETL -->|Write Nodes/Edges| N4J
        ETL -->|Embed Narratives| QD
    end

    classDef db fill:#f9f2f4,stroke:#333,stroke-width:1px;
    class PG,N4J,QD db;
```

---

## 🗄️ Database Schemas

### Relational Schema (PostgreSQL)
The structured source of truth for FIR records, lookup tables, and personnel.

```mermaid
erDiagram
    CaseMaster ||--o{ Accused : contains
    CaseMaster ||--o{ Victim : contains
    CaseMaster ||--o{ ComplainantDetails : contains
    CaseMaster {
        string CrimeNo PK
        date CrimeRegisteredDate
        string BriefFacts
        float latitude
        float longitude
    }
    Accused {
        int AccusedMasterID PK
        string AccusedName
        int AgeYear
    }
    Victim {
        int VictimMasterID PK
        string VictimName
    }
    ComplainantDetails {
        int ComplainantID PK
        string ComplainantName
    }
```

### Knowledge Graph Schema (Neo4j)
Designed for multi-hop relationship traversals to uncover organized syndicates.

```mermaid
graph TD
    A([Accused]) -- IS_ACCUSED_IN --> I([Incident])
    C([Complainant]) -- FILED --> I
    V([Victim]) -- VICTIM_IN --> I
    I -- OCCURRED_AT --> L([Location])
    
    A -- OWNS_PHONE --> P([Phone])
    A -- OWNS_VEHICLE --> Veh([Vehicle])
    
    style A fill:#ef4444,color:#fff
    style I fill:#b91c1c,color:#fff
    style C fill:#10b981,color:#fff
    style V fill:#f59e0b,color:#fff
```

---

## 🔄 Core Workflows

### 1. Hybrid RAG (AI Chatbot) Query Flow
How the Intelligence Assistant answers questions using multi-modal data.

```mermaid
sequenceDiagram
    actor User
    participant Frontend
    participant Backend
    participant Qdrant
    participant Neo4j
    participant Gemini
    
    User->>Frontend: "Who is involved in recent robberies?"
    Frontend->>Backend: POST /api/v1/ai/ask {query, history}
    Backend->>Qdrant: Search Vector (Top K FIRs)
    Qdrant-->>Backend: Return Semantic Hits & Scores
    Backend->>Neo4j: Query Global Graph Stats
    Neo4j-->>Backend: Return Incident Counts
    Backend->>Gemini: Prompt + DB Context + Chat History
    Gemini-->>Backend: Augmented Answer + Citations
    Backend-->>Frontend: {answer, confidence, citations}
    Frontend-->>User: Display AI Response
```

### 2. Automated ETL Ingestion Pipeline
How structured data is transformed into intelligence assets.

```mermaid
sequenceDiagram
    participant Postgres
    participant ETL
    participant SentenceTransformers
    participant Neo4j
    participant Qdrant
    
    loop Every Batch (e.g., 1000 records)
        ETL->>Postgres: SELECT * FROM CaseMaster
        Postgres-->>ETL: Return FIR rows
        
        par Graph Processing
            ETL->>Neo4j: UNWIND Batch MERGE (Incident, Accused, Victim)
        and Vector Processing
            ETL->>SentenceTransformers: model.encode(BriefFacts)
            SentenceTransformers-->>ETL: Return 384d Vectors
            ETL->>Qdrant: Upsert Points (Vectors + Metadata)
        end
    end
```

---

## ⚙️ Setup & Installation

Follow these instructions to run the entire intelligence platform locally.

### 1. Start the Infrastructure (Docker)
Ensure Docker Desktop is running on your machine, then spin up the databases:
```bash
docker-compose up -d
```
*(This will start Neo4j, Qdrant, Postgres, and Redis).*

### 2. Configure Environment Variables
Create a `.env` file from the example template and add your Google Gemini API key:
```bash
cp .env.example .env
```
Open the `.env` file and set `GEMINI_API_KEY=your_actual_api_key_here`. 
*(Note: If no key is set, the system will fall back to a hardcoded mock mode, but the AI won't generate real responses).*

### 3. Setup the Python Backend
Open a terminal in the root directory and create a virtual environment:
```bash
python -m venv venv
.\venv\Scripts\activate
pip install -r backend/requirements.txt
```

### 4. Generate Mock Data & Run the ETL Pipeline
We have included a mock data generator that creates 1,000 synthetic FIRs with hidden crime syndicates for testing.
```bash
# 1. Generate the data
cd backend
python -m src.tasks.data_generator

# 2. Run the ETL Pipeline to populate Neo4j and Qdrant
python -m src.tasks.etl_pipeline
cd ..
```

### 5. Start the Application Servers
You will need two terminal windows for this.

**Terminal 1 (Backend):**
```bash
cd backend
.\venv\Scripts\activate
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

**Terminal 2 (Frontend):**
```bash
cd frontend
npm run dev
```

### 6. Access the Platform
Open your browser and navigate to:
👉 **[http://localhost:3000](http://localhost:3000)**

---

## 🛡️ Built With Purpose
*Developed to empower the Karnataka State Police with next-generation investigative capabilities.*
