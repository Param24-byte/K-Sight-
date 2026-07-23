from fastapi import APIRouter, Depends, Query
import sys
import os

# Ensure services can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.services.graph.neo4j_client import neo4j_client
from src.services.ai.qdrant_client import vector_client
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
    WITH i LIMIT $limit
    OPTIONAL MATCH (a:Accused)-[r1:IS_ACCUSED_IN]->(i)
    OPTIONAL MATCH (c:Complainant)-[r2:FILED]->(i)
    OPTIONAL MATCH (v:Victim)-[r3:VICTIM_IN]->(i)
    OPTIONAL MATCH (a)-[:IS_ACCUSED_IN]->(all_i:Incident)
    WITH i, a, c, v, count(DISTINCT all_i) AS incident_count
    RETURN i.fir_id AS case_id, i.date AS date, i.brief_facts AS brief_facts, i.status AS status,
           a.id AS accused_id, a.name AS accused_name, a.age AS accused_age, incident_count,
           c.id AS comp_id, c.name AS comp_name, c.age AS comp_age,
           v.id AS vic_id, v.name AS vic_name, v.age AS vic_age
    """
    try:
        nodes_by_id = {}
        edges = []
        with neo4j_client.driver.session() as session:
            result = session.run(query, limit=limit)
            for record in result:
                cid = record["case_id"]
                if cid and cid not in nodes_by_id:
                    nodes_by_id[cid] = {"id": cid, "label": cid, "type": "incident", "details": {"Date": str(record["date"]), "Facts": record["brief_facts"], "Status": record["status"]}}
                
                if record["accused_id"]:
                    aid = f"acc_{record['accused_id']}"
                    if aid not in nodes_by_id:
                        risk = min(100, record["incident_count"] * 15) if record["incident_count"] else 0
                        nodes_by_id[aid] = {"id": aid, "label": record["accused_name"], "type": "accused", "risk_score": risk, "details": {"Age": record["accused_age"], "Risk Score": risk}}
                    edges.append({"source": aid, "target": cid, "label": "ACCUSED_IN"})
                    
                if record["comp_id"]:
                    com_id = f"comp_{record['comp_id']}"
                    if com_id not in nodes_by_id:
                        nodes_by_id[com_id] = {"id": com_id, "label": record["comp_name"], "type": "complainant", "details": {"Age": record["comp_age"]}}
                    edges.append({"source": com_id, "target": cid, "label": "FILED"})
                    
                if record["vic_id"]:
                    vid = f"vic_{record['vic_id']}"
                    if vid not in nodes_by_id:
                        nodes_by_id[vid] = {"id": vid, "label": record["vic_name"], "type": "victim", "details": {"Age": record["vic_age"]}}
                    edges.append({"source": vid, "target": cid, "label": "VICTIM_IN"})
            
            # Deduplicate edges
            edges = [dict(t) for t in {tuple(d.items()) for d in edges}]
            
            return {"nodes": list(nodes_by_id.values()), "edges": edges}
    except Exception as e:
        return {"error": str(e), "message": "Ensure Neo4j is running"}

@router.get("/graph/case/{fir_id}")
def get_case_graph(fir_id: str, current_user: User = Depends(require_role(["Investigator", "Supervisor", "Policymaker"]))):
    """Fetch a subgraph centered on a specific case/FIR"""
    query = """
    MATCH (i:Incident {fir_id: $fir_id})
    OPTIONAL MATCH (a:Accused)-[r1:IS_ACCUSED_IN]->(i)
    OPTIONAL MATCH (c:Complainant)-[r2:FILED]->(i)
    OPTIONAL MATCH (v:Victim)-[r3:VICTIM_IN]->(i)
    OPTIONAL MATCH (a)-[:IS_ACCUSED_IN]->(all_i:Incident)
    WITH i, a, c, v, count(DISTINCT all_i) AS incident_count
    RETURN i.fir_id AS case_id, i.date AS date, i.brief_facts AS brief_facts, i.status AS status,
           a.id AS accused_id, a.name AS accused_name, a.age AS accused_age, incident_count,
           c.id AS comp_id, c.name AS comp_name, c.age AS comp_age,
           v.id AS vic_id, v.name AS vic_name, v.age AS vic_age
    """
    try:
        nodes_by_id = {}
        edges = []
        with neo4j_client.driver.session() as session:
            result = session.run(query, fir_id=fir_id)
            for record in result:
                cid = record["case_id"]
                if cid and cid not in nodes_by_id:
                    nodes_by_id[cid] = {"id": cid, "label": cid, "type": "incident", "details": {"Date": str(record["date"]), "Facts": record["brief_facts"], "Status": record["status"]}}
                
                if record["accused_id"]:
                    aid = f"acc_{record['accused_id']}"
                    if aid not in nodes_by_id:
                        risk = min(100, record["incident_count"] * 15) if record["incident_count"] else 0
                        nodes_by_id[aid] = {"id": aid, "label": record["accused_name"], "type": "accused", "risk_score": risk, "details": {"Age": record["accused_age"], "Risk Score": risk}}
                    edges.append({"source": aid, "target": cid, "label": "ACCUSED_IN"})
                    
                if record["comp_id"]:
                    com_id = f"comp_{record['comp_id']}"
                    if com_id not in nodes_by_id:
                        nodes_by_id[com_id] = {"id": com_id, "label": record["comp_name"], "type": "complainant", "details": {"Age": record["comp_age"]}}
                    edges.append({"source": com_id, "target": cid, "label": "FILED"})
                    
                if record["vic_id"]:
                    vid = f"vic_{record['vic_id']}"
                    if vid not in nodes_by_id:
                        nodes_by_id[vid] = {"id": vid, "label": record["vic_name"], "type": "victim", "details": {"Age": record["vic_age"]}}
                    edges.append({"source": vid, "target": cid, "label": "VICTIM_IN"})
            
            # Deduplicate edges
            edges = [dict(t) for t in {tuple(d.items()) for d in edges}]
            
            return {"nodes": list(nodes_by_id.values()), "edges": edges}
    except Exception as e:
        return {"error": str(e), "message": "Ensure Neo4j is running"}

@router.get("/intelligence/similar/{fir_id}")
def get_similar_firs(fir_id: str, current_user: User = Depends(get_current_user)):
    """Fetch Top 3 similar FIRs based on narrative semantic search"""
    query = "MATCH (i:Incident {fir_id: $fir_id}) RETURN i.brief_facts AS facts"
    try:
        with neo4j_client.driver.session() as session:
            result = session.run(query, fir_id=fir_id).single()
            if not result or not result["facts"]:
                return []
            narrative = result["facts"]
            
            embedding = vector_client.encoder.encode(narrative).tolist()
            search_result = vector_client.client.search(
                collection_name=vector_client.collection_name,
                query_vector=embedding,
                limit=4 
            )
            
            matches = []
            for hit in search_result:
                if hit.payload.get("fir_id") != fir_id:
                    matches.append({
                        "fir_id": hit.payload.get("fir_id"),
                        "type": hit.payload.get("type", "Incident"),
                        "location": hit.payload.get("location", "Unknown Location"),
                        "date": hit.payload.get("date", "Unknown Date"),
                        "score": round(hit.score * 100, 1)
                    })
                    
            return matches[:3]
    except Exception as e:
        return {"error": str(e), "message": "Failed to fetch similar cases"}
