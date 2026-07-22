from fastapi import APIRouter
import sys
import os

# Ensure services can be imported
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))
from src.services.graph.neo4j_client import neo4j_client

router = APIRouter()

@router.get("/intelligence/firs")
def get_firs(limit: int = 100):
    """Fetch FIRs with coordinates for the map"""
    query = """
    MATCH (i:Incident)-[:OCCURRED_AT]->(l:Location)
    RETURN i.fir_id AS fir_id, i.type AS type, i.date AS date, 
           l.name AS location_name, l.lat AS lat, l.lng AS lng
    LIMIT $limit
    """
    try:
        with neo4j_client.driver.session() as session:
            result = session.run(query, limit=limit)
            return [record.data() for record in result]
    except Exception as e:
        return {"error": str(e), "message": "Ensure Neo4j is running"}

@router.get("/graph/suspects")
def get_suspect_graph(limit: int = 50):
    """Fetch a subgraph of suspects, phones, and vehicles"""
    query = """
    MATCH (p:Person)
    OPTIONAL MATCH (p)-[r1:OWNS_PHONE]->(ph:Phone)
    OPTIONAL MATCH (p)-[r2:OWNS_VEHICLE]->(v:Vehicle)
    RETURN p.id AS person_id, p.name AS name, 
           ph.number AS phone, v.license_plate AS vehicle
    LIMIT $limit
    """
    try:
        nodes = []
        edges = []
        with neo4j_client.driver.session() as session:
            result = session.run(query, limit=limit)
            for record in result:
                pid = record["person_id"]
                nodes.append({"id": pid, "label": record["name"], "type": "person"})
                if record["phone"]:
                    ph_id = record["phone"]
                    nodes.append({"id": ph_id, "label": ph_id, "type": "phone"})
                    edges.append({"source": pid, "target": ph_id, "label": "OWNS_PHONE"})
                if record["vehicle"]:
                    v_id = record["vehicle"]
                    nodes.append({"id": v_id, "label": v_id, "type": "vehicle"})
                    edges.append({"source": pid, "target": v_id, "label": "OWNS_VEHICLE"})
            return {"nodes": nodes, "edges": edges}
    except Exception as e:
        return {"error": str(e), "message": "Ensure Neo4j is running"}
