# Crime Intelligence & Investigation Platform
## 3. AI, Data, and Graph Intelligence

### 7. Database Design & 8. ER Diagram (Conceptual)
The core relational data in PostgreSQL captures immutable records.
- **FIR_Table**: `id`, `fir_number`, `station_id`, `date`, `ipc_sections`, `narrative`, `status`.
- **Police_Station_Table**: `id`, `name`, `district`, `zone`, `lat`, `lng`.
- **Officer_Table**: `id`, `badge_no`, `name`, `rank`, `station_id`.
- **Audit_Log_Table**: `id`, `user_id`, `action`, `timestamp`, `details`.

### 9. Knowledge Graph Schema (Neo4j)
**Nodes (Labels)**:
- `Person` (id, name, age, gender, criminal_record)
- `Incident` (id, type, date, location, severity)
- `Location` (id, address, lat, lng, type)
- `Vehicle` (license_plate, make, color)
- `Phone` (number, imei)
- `Weapon` (type, serial_number)
- `ModusOperandi` (tag)

**Edges (Relationships)**:
- `(Person)-[:COMMITTED]->(Incident)`
- `(Person)-[:VICTIM_OF]->(Incident)`
- `(Person)-[:WITNESSED]->(Incident)`
- `(Person)-[:OWNS]->(Vehicle | Phone | Weapon)`
- `(Person)-[:CALLED {count, duration}]->(Person)`
- `(Incident)-[:OCCURRED_AT]->(Location)`
- `(Incident)-[:USES_MO]->(ModusOperandi)`
- `(Person)-[:ASSOCIATED_WITH {weight}]->(Person)`

### 11. ML Pipeline & 12. Data Pipeline
The intelligence pipelines act on the raw data to extract features.
1. **Data Ingestion**: Scheduled pulls or push APIs ingest FIRs.
2. **Text Processing**: Spacy/NLTK cleans the Kannada/English FIR narratives.
3. **Entity Extraction (NER)**: A lightweight LLM or trained Spacy model extracts names, locations, and entities, transforming unstructured text into structured graph nodes.
4. **Vectorization**: `SentenceTransformers (all-MiniLM-L6-v2)` generates 384-dimensional embeddings of the FIR text.
5. **Storage**: Nodes to Neo4j. Vectors to Qdrant.

### 13. ETL Flow
- **Extract**: Raw JSON from police systems (mocked via CSV/JSON).
- **Transform**: Clean text, normalize addresses, geocode locations, resolve entities (entity disambiguation to prevent duplicate `Person` nodes for the same suspect).
- **Load**: Transactional insert into Postgres, Neo4j, and Qdrant.

### 14. Graph Construction Pipeline
Entity Resolution is critical. When a new FIR mentions "Raju, Phone: 98765...", the pipeline queries Neo4j. If Phone 98765 exists, the new `Person` node is merged or linked, instantly surfacing a connection to past crimes.

### 15. Feature Engineering
- **Temporal Features**: Day of week, hour of day, proximity to festivals.
- **Spatial Features**: Distance to nearest police station, ward-level density.
- **Graph Features**: Degree centrality (number of connections), PageRank score (influence in the criminal network).

### 16. Algorithms Used & 17. AI Models
- **Clustering (Hotspots)**: DBSCAN (Density-Based Spatial Clustering of Applications with Noise) identifies geographic clusters of crimes.
- **Association Rule Mining**: Apriori algorithm finds MO patterns (e.g., "If [Biking] and [Chain Snatching], then [Time > 18:00]").
- **Predictive Scoring**: XGBoost classifier trained on spatio-temporal and graph features to predict the probability of crime occurrence in a grid.
- **Case Retrieval**: Cosine Similarity via Qdrant on vector embeddings.
- **LLM Engine**: Gemini / GPT-4 for natural language interface and semantic reasoning.

### 18. Statistical Models & 19. Explainability Framework
- **Sociological Correlation**: Pearson correlation to map crime density against ward-level demographic data.
- **Explainability (XAI)**:
  - Predictions from XGBoost utilize SHAP (SHapley Additive exPlanations) values to output: *"Area X is high risk. Key factors: Recent cluster of thefts (40%), Low police patrol density (35%), Weekend (25%)."*
  - The LLM responses utilize **Citation Markers** mapped directly to Cypher query outputs or FIR IDs.

### 20. Graph Analytics Design
Utilizing Neo4j Graph Data Science (GDS):
- **Shortest Path**: Connect two seemingly unrelated suspects via shared vehicles/phones.
- **Centrality**: Identify the "Kingpin" using Betweenness Centrality (the node that bridges different criminal groups).
- **Community Detection**: Louvain algorithm automatically segments the graph into distinct Organized Crime Syndicates based on interaction density.

### 39. Sample Data Schema
```json
{
  "fir_id": "FIR-2023-BGL-001",
  "date": "2023-10-14T22:30:00Z",
  "location": {"lat": 12.9716, "lng": 77.5946},
  "ipc_sections": ["392", "397"],
  "mo": ["Bike-borne", "Machete", "Chain Snatching"],
  "suspects": [{"name": "Unknown", "vehicle": "KA-01-XX-1234"}],
  "narrative": "Victim was returning from work when..."
}
```
