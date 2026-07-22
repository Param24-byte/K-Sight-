# Crime Intelligence & Investigation Platform
## 4. UX/UI and User Journeys

### 12. Role-Based Dashboard Strategy
The UI dynamically adapts to the user's role to prevent cognitive overload.
- **Investigator**: Focuses on active cases, suspect graphs, and local (station-level) heatmaps.
- **Senior Officer / SP**: Focuses on district-wide metrics, predictive risk models, and resource allocation.
- **SCRB Analyst**: Accesses raw data querying, data pipeline health, and macro sociological correlations.
- **Administrator**: Audit logs, system health, user access controls.

### 21. Dashboard Wireframes & 22. UI Screens
The interface utilizes a sleek, dark-mode-first design (Tailwind CSS, shadcn/ui) suitable for extended viewing in command centers.

**Screen 1: The Command Center (Home)**
- **Top Bar**: Global search (NLP powered), Role indicator, Alert bell.
- **Main View (Center)**: Interactive Leaflet Map of Karnataka/District showing live hotspots (red zones).
- **Left Sidebar**: Filters (Date range, Crime Type, Status, MO).
- **Right Panel**: "Emerging Intelligence" feed (e.g., "3 Chain Snatchings detected in Jayanagar with similar MO").
- **Bottom Shelf**: KPI Cards (Total FIRs, Arrest Rate, Predicted Incidents).

**Screen 2: The Graph Investigator (Neo4j View)**
- **Canvas**: React Flow visualizer showing nodes (Suspects, Phones) and edges.
- **Interactions**: Click a node to expand its connections. Physics-based layout.
- **Inspector Panel**: Clicking a node reveals its properties (e.g., Suspect timeline, probability of reoffending).

**Screen 3: AI Investigation Assistant (Chat View)**
- **Layout**: Split screen. Left side: Chatbot interface. Right side: Dynamic rendering panel.
- **Flow**: User types "Show me recent robbery hotspots". The right panel instantly updates with a map heatmap. The chatbot replies, "Here are the hotspots, citing 45 recent FIRs. High confidence due to weekend patterns."

**Screen 4: Case Similarity & Timeline**
- A vertical timeline of a specific investigation.
- "Similar Cases" sidebar showing % match based on Vector similarity (e.g., "FIR-102 (89% match) - Similar weapon and escape route").

### 23. User Journey (Investigator Flow)
1. **Trigger**: Investigator logs in and sees an alert: "New organized crime cluster detected in Zone South."
2. **Investigation**: Clicks the alert. The UI transitions to the **Graph Investigator**.
3. **Exploration**: The graph shows a central node (a phone number) connecting three separate burglary FIRs.
4. **Action**: The investigator asks the AI Chatbot: "Who owns this phone number and what is their risk score?"
5. **Intelligence**: The AI queries the graph and DB, returning the suspect's identity, a 92% flight risk score, and cites past FIRs.
6. **Resolution**: Investigator exports the subgraph and intelligence report as a PDF to attach to the case diary.
