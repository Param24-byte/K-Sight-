# Crime Intelligence & Investigation Platform
## 2. System Architecture & Engineering

### 4. High-Level Architecture (HLA)
The platform follows a modern, decoupled, intelligence-first architecture, separated into four major tiers:
1. **Client Tier**: React/Next.js SPA consumed by Web and Tablet interfaces.
2. **API & Orchestration Tier**: FastAPI application acting as the central gateway. It routes requests to analytical pipelines or basic CRUD operations.
3. **Intelligence Tier**: Dedicated Python services for Machine Learning, Graph Analytics, and LLM orchestration (Hybrid RAG).
4. **Persistence Tier**: Polyglot persistence strategy ensuring the right database for the right job:
   - *PostgreSQL*: ACID-compliant relational data (Users, Audit Logs, raw FIR text).
   - *Neo4j*: Graph data (Suspects, Vehicles, Locations and their relationships).
   - *Qdrant*: Vector data (FIR narrative embeddings for semantic search).
   - *Redis*: Caching layer and Task Queue broker.

### 5. Low-Level Architecture (LLA)
**Data Ingestion to Intelligence Flow**:
1. User uploads FIR / Case data via UI.
2. Data hits FastAPI `POST /api/v1/ingest`.
3. Background Worker (Celery/Redis) picks up the job.
4. **ETL Process**:
   - Stores raw JSON in PostgreSQL.
   - Extracts Entities (NER using Spacy/LLM).
   - Updates Neo4j Graph with Nodes (Person, Location, Phone) and Edges (OWNED_BY, PRESENT_AT, CALLED).
   - Generates Embeddings (SentenceTransformers) of the case summary and upserts to Qdrant.
5. The UI queries the Intelligence tier, which aggregates Neo4j Cypher queries and Qdrant semantic search results to present insights.

### 6. Microservice Architecture (Logical Boundaries)
While starting as a modular monolith for the hackathon, the logical boundaries are strictly defined for microservice extraction:
- **Core Service**: User Auth, RBAC, Configuration.
- **Graph & Analytics Service**: Neo4j interactions, NetworkX algorithms.
- **AI & RAG Service**: LLM interactions, Embeddings, Semantic Search.
- **Geospatial Service**: Heatmap generation, clustering, spatial queries.

### 10. API Design (RESTful & GraphQL-inspired)
The API strictly follows RESTful principles with JSON payloads.
**Key Endpoints**:
- `POST /api/v1/auth/login`: JWT generation.
- `GET /api/v1/intelligence/hotspots?city=Bengaluru&time=weekend`: Returns GeoJSON for heatmaps.
- `GET /api/v1/graph/network/{suspect_id}?depth=2`: Returns nodes and edges connected to a suspect.
- `POST /api/v1/ai/ask`: The core AI interface.
  - *Payload*: `{"query": "Show robbery hotspots"}`
  - *Response*: `{"answer": "...", "confidence": 0.92, "citations": [{"type": "db_query", "data": "..."}]}`

### 24. Backend Folder Structure
```text
backend/
├── src/
│   ├── api/                 # FastAPI routers & controllers
│   ├── core/                # Config, Security, JWT, Error Handling
│   ├── models/              # Pydantic & SQLAlchemy Models
│   ├── services/
│   │   ├── graph/           # Neo4j query builders & analytics
│   │   ├── ai/              # LLM, Vector Search, Hybrid RAG
│   │   ├── spatial/         # Geospatial computations
│   ├── tasks/               # Background Jobs (Redis/Celery)
│   ├── utils/               # Helpers
│   └── main.py              # Application Entrypoint
├── tests/
├── Dockerfile
├── requirements.txt
└── .env
```

### 25. Frontend Folder Structure
```text
frontend/
├── src/
│   ├── assets/
│   ├── components/
│   │   ├── ui/              # shadcn/ui generic components
│   │   ├── maps/            # Leaflet integration
│   │   ├── graphs/          # React Flow network visualizer
│   │   └── analytics/       # Recharts dashboards
│   ├── hooks/               # Custom React hooks (e.g., useGraphData)
│   ├── pages/               # Route pages (Dashboard, Investigation, GraphView)
│   ├── services/            # Axios API clients
│   ├── store/               # Zustand state management
│   ├── types/               # TypeScript interfaces
│   ├── utils/
│   └── App.tsx
├── tailwind.config.js
├── package.json
└── Dockerfile
```

### 26. Deployment Architecture
- **Docker Compose**: Entire stack orchestrated via a `docker-compose.yml` for 1-click execution.
- **Containers**:
  1. Frontend (Nginx/React)
  2. Backend (Uvicorn/FastAPI)
  3. Postgres
  4. Neo4j
  5. Qdrant
  6. Redis
- **Reverse Proxy**: Nginx handles SSL termination and routes traffic to Frontend or Backend.

### 27. Security Architecture
- **Authentication**: Stateless JWT with short expiration and refresh tokens.
- **Authorization**: Strict Role-Based Access Control (RBAC). A Policy Maker cannot view PII; an Investigator cannot delete system logs.
- **Data Protection**: 
  - Passwords hashed via bcrypt.
  - Data-in-transit encrypted via TLS.
- **Audit Logging**: Every query, especially AI assistant queries and graph traversals, is logged with the User ID and timestamp.

### 28. Scalability Plan
- **Horizontal Scaling**: FastAPI backend and React frontend are stateless and can scale horizontally behind a Load Balancer.
- **Database Scaling**: PostgreSQL read-replicas. Neo4j causal clustering for heavy graph reads.
- **Asynchronous Processing**: Heavy ML tasks (graph community detection, embedding generation) are offloaded to background workers, keeping the API highly responsive.

### 29. Performance Optimization
- **Caching**: Frequently accessed aggregate queries (e.g., city-wide crime stats) are cached in Redis.
- **Graph Projections**: Neo4j Graph Data Science (GDS) uses in-memory projected graphs to run intensive algorithms (PageRank) in milliseconds.
- **Frontend Optimization**: React concurrent rendering, lazy loading map and graph visualizer components to ensure fast Initial Load Time.
