import os
import sys
import logging
from sqlalchemy.orm import joinedload

# Ensure we can import the services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.services.db.database import SessionLocal
from src.services.db.models import Act, Section, CaseMaster, ComplainantDetails, Victim, Accused, ActSectionAssociation
from src.services.graph.neo4j_client import neo4j_client
from src.services.ai.qdrant_client import vector_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def run_etl():
    logger.info("--- Starting Intelligence ETL Pipeline (Postgres to Graph/Vector) ---")
    
    db = SessionLocal()
    
    try:
        neo4j_client.setup_constraints()
        neo4j_client.clear_database()
        vector_client.setup_collection()
    except Exception as e:
        logger.error(f"Failed to connect to databases. Error: {e}")
        return

    logger.info("Ingesting Acts and Sections to Neo4j...")
    acts = db.query(Act).all()
    sections = db.query(Section).all()
    
    # Pre-cache acts for fast lookup
    act_map = {a.ActCode: {"ActCode": a.ActCode, "ActDescription": a.ActDescription} for a in acts}
    for sec in sections:
        if sec.ActCode in act_map:
            neo4j_client.ingest_act_section(
                act_data=act_map[sec.ActCode],
                section_data={"id": sec.id, "SectionCode": sec.SectionCode, "SectionDescription": sec.SectionDescription}
            )

    logger.info("Ingesting Case Data to Neo4j and Qdrant...")
    cases = db.query(CaseMaster).all()
    
    neo4j_batch_payload = []
    qdrant_payloads = []
    
    for case in cases:
        # Fetch related entities
        complainants = db.query(ComplainantDetails).filter(ComplainantDetails.CaseMasterID == case.CaseMasterID).all()
        victims = db.query(Victim).filter(Victim.CaseMasterID == case.CaseMasterID).all()
        accused = db.query(Accused).filter(Accused.CaseMasterID == case.CaseMasterID).all()
        assocs = db.query(ActSectionAssociation).filter(ActSectionAssociation.CaseMasterID == case.CaseMasterID).all()
        
        # Serialize for Neo4j
        c_comps = [{"id": c.ComplainantID, "name": c.ComplainantName, "age": c.AgeYear} for c in complainants]
        c_vics = [{"id": v.VictimMasterID, "name": v.VictimName, "age": v.AgeYear} for v in victims]
        c_acc = [{"id": a.AccusedMasterID, "name": a.AccusedName, "age": a.AgeYear} for a in accused]
        c_secs = [assoc.SectionID for assoc in assocs]
        
        neo4j_batch_payload.append({
            "CrimeNo": case.CrimeNo,
            "CaseNo": case.CaseNo,
            "CrimeRegisteredDate": case.CrimeRegisteredDate.isoformat() if case.CrimeRegisteredDate else None,
            "BriefFacts": case.BriefFacts,
            "CaseStatusID": case.CaseStatusID,
            "latitude": case.latitude,
            "longitude": case.longitude,
            "complainants": c_comps,
            "victims": c_vics,
            "accused": c_acc,
            "sections": c_secs
        })
        
        # Prepare for Qdrant (Text Search)
        accused_names = ", ".join([a.AccusedName for a in accused])
        victim_names = ", ".join([v.VictimName for v in victims])
        
        narrative = f"{case.BriefFacts} | Accused: {accused_names} | Victims: {victim_names}"
        
        # Format required by ingest_firs (requires fir_id, date, location.name/lat/lng, narrative)
        qdrant_payloads.append({
            "fir_id": case.CrimeNo,
            "date": case.CrimeRegisteredDate.isoformat() if case.CrimeRegisteredDate else "",
            "location": {"name": "Mapped Location", "lat": case.latitude or 0, "lng": case.longitude or 0},
            "type": "Incident",
            "ipc_sections": [],
            "mo_tags": [],
            "suspects_involved": [a.AccusedMasterID for a in accused],
            "narrative": narrative
        })

    logger.info(f"Ingesting {len(neo4j_batch_payload)} Cases to Neo4j in a single batch...")
    if neo4j_batch_payload:
        neo4j_client.ingest_cases_batch(neo4j_batch_payload)

    logger.info(f"Generating Embeddings and Ingesting {len(qdrant_payloads)} FIRs to Qdrant...")
    if qdrant_payloads:
        vector_client.ingest_firs(qdrant_payloads)
    
    neo4j_client.close()
    db.close()
    logger.info("--- ETL Pipeline Completed Successfully ---")

if __name__ == "__main__":
    run_etl()
