import json
import os
import sys
import logging

# Ensure we can import the services
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from src.services.graph.neo4j_client import neo4j_client
from src.services.ai.qdrant_client import vector_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_json(filepath):
    with open(filepath, 'r') as f:
        return json.load(f)

def run_etl():
    logger.info("--- Starting Intelligence ETL Pipeline ---")
    
    # Paths to the mock data generated in Sprint 1
    data_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../../data'))
    suspects_file = os.path.join(data_dir, 'suspects.json')
    firs_file = os.path.join(data_dir, 'firs.json')
    
    if not os.path.exists(suspects_file) or not os.path.exists(firs_file):
        logger.error("Mock data not found. Please run data_generator.py first.")
        return

    suspects = load_json(suspects_file)
    firs = load_json(firs_file)
    
    logger.info(f"Loaded {len(suspects)} Suspects and {len(firs)} FIRs.")
    
    # 1. Setup DB schemas
    try:
        neo4j_client.setup_constraints()
        vector_client.setup_collection()
    except Exception as e:
        logger.error(f"Failed to connect to databases. Are Docker containers running? Error: {e}")
        return

    # 2. Ingest into Neo4j
    logger.info("Ingesting Suspects to Neo4j...")
    for s in suspects:
        neo4j_client.ingest_suspect(s)
        
    logger.info("Ingesting FIRs to Neo4j...")
    for f in firs:
        neo4j_client.ingest_fir(f)
        
    # 3. Ingest into Qdrant
    logger.info("Generating Embeddings and Ingesting FIRs to Qdrant...")
    vector_client.ingest_firs(firs)
    
    neo4j_client.close()
    logger.info("--- ETL Pipeline Completed Successfully ---")

if __name__ == "__main__":
    run_etl()
