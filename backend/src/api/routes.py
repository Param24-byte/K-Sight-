from fastapi import APIRouter, Depends, Query
import sys
import os

# Ensure services can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.services.graph.neo4j_client import neo4j_client
from src.api.auth import get_current_user, require_role
from src.services.db.models import User

router = APIRouter()

@router.get("/intelligence/firs")
def get_firs(limit: int = Query(100, le=1000), current_user: User = Depends(get_current_user)):
    """Fetch FIRs with coordinates for the map"""
    query = """
    MATCH (i:Incident)-[:OCCURRED_AT]->(l:Location)
    RETURN i.fir_id AS fir_id, "Incident" AS type, i.date AS date, 
           "Mapped Location" AS location_name, l.lat AS lat, l.lng AS lng
    LIMIT $limit
    """
    try:
        with neo4j_client.driver.session() as session:
            result = session.run(query, limit=limit)
            return [record.data() for record in result]
    except Exception as e:
        return {"error": str(e), "message": "Ensure Neo4j is running"}

@router.get("/graph/suspects")
def get_suspect_graph(limit: int = Query(50, le=500), current_user: User = Depends(require_role(["Investigator", "Supervisor", "Policymaker"]))):
    """Fetch a subgraph of suspects, phones, and vehicles"""
    query = """
    MATCH (i:Incident)
    OPTIONAL MATCH (a:Accused)-[r1:IS_ACCUSED_IN]->(i)
    OPTIONAL MATCH (c:Complainant)-[r2:FILED]->(i)
    OPTIONAL MATCH (v:Victim)-[r3:VICTIM_IN]->(i)
    RETURN i.fir_id AS case_id, 
           a.id AS accused_id, a.name AS accused_name,
           c.id AS comp_id, c.name AS comp_name,
           v.id AS vic_id, v.name AS vic_name
    LIMIT $limit
    """
    try:
        nodes = []
        edges = []
        with neo4j_client.driver.session() as session:
            result = session.run(query, limit=limit)
            for record in result:
                cid = record["case_id"]
                if not any(n["id"] == cid for n in nodes):
                    nodes.append({"id": cid, "label": cid, "type": "incident"})
                
                if record["accused_id"]:
                    aid = f"acc_{record['accused_id']}"
                    if not any(n["id"] == aid for n in nodes):
                        nodes.append({"id": aid, "label": record["accused_name"], "type": "accused"})
                    edges.append({"source": aid, "target": cid, "label": "ACCUSED_IN"})
                    
                if record["comp_id"]:
                    com_id = f"comp_{record['comp_id']}"
                    if not any(n["id"] == com_id for n in nodes):
                        nodes.append({"id": com_id, "label": record["comp_name"], "type": "complainant"})
                    edges.append({"source": com_id, "target": cid, "label": "FILED"})
                    
                if record["vic_id"]:
                    vid = f"vic_{record['vic_id']}"
                    if not any(n["id"] == vid for n in nodes):
                        nodes.append({"id": vid, "label": record["vic_name"], "type": "victim"})
                    edges.append({"source": vid, "target": cid, "label": "VICTIM_IN"})
            
            # Deduplicate edges
            edges = [dict(t) for t in {tuple(d.items()) for d in edges}]
            
            return {"nodes": nodes, "edges": edges}
    except Exception as e:
        return {"error": str(e), "message": "Ensure Neo4j is running"}
