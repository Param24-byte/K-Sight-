from neo4j import GraphDatabase
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self, uri="bolt://localhost:7687", user="neo4j", password="password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, password))
        
    def close(self):
        self.driver.close()

    def setup_constraints(self):
        """Creates unique constraints to prevent duplicate nodes during ingestion"""
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Person) REQUIRE p.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (p:Phone) REQUIRE p.number IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (v:Vehicle) REQUIRE v.license_plate IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Incident) REQUIRE i.fir_id IS UNIQUE"
        ]
        with self.driver.session() as session:
            for query in queries:
                session.run(query)
        logger.info("Neo4j constraints verified.")

    def ingest_suspect(self, suspect_data):
        """Ingests a suspect and their phone/vehicle into the graph"""
        query = """
        MERGE (p:Person {id: $id})
        SET p.name = $name, p.age = $age
        
        WITH p
        WHERE $phone IS NOT NULL
        MERGE (phone:Phone {number: $phone})
        MERGE (p)-[:OWNS_PHONE]->(phone)
        
        WITH p
        WHERE $vehicle IS NOT NULL
        MERGE (v:Vehicle {license_plate: $vehicle})
        MERGE (p)-[:OWNS_VEHICLE]->(v)
        """
        with self.driver.session() as session:
            session.run(query, 
                        id=suspect_data.get("id"),
                        name=suspect_data.get("name"),
                        age=suspect_data.get("age"),
                        phone=suspect_data.get("phone"),
                        vehicle=suspect_data.get("vehicle"))

    def ingest_fir(self, fir_data):
        """Ingests an FIR, Location, and connects involved Suspects"""
        query = """
        // 1. Merge Incident
        MERGE (i:Incident {fir_id: $fir_id})
        SET i.type = $type, 
            i.date = $date, 
            i.narrative = $narrative,
            i.ipc_sections = $ipc_sections,
            i.mo_tags = $mo_tags
            
        // 2. Merge Location
        MERGE (l:Location {name: $loc_name})
        ON CREATE SET l.lat = $lat, l.lng = $lng
        MERGE (i)-[:OCCURRED_AT]->(l)
        
        // 3. Connect Suspects
        WITH i
        UNWIND $suspects_involved AS suspect_id
        MERGE (p:Person {id: suspect_id}) // Create if not exists
        MERGE (p)-[:COMMITTED]->(i)
        """
        loc = fir_data.get("location", {})
        with self.driver.session() as session:
            session.run(query,
                        fir_id=fir_data.get("fir_id"),
                        type=fir_data.get("type"),
                        date=fir_data.get("date"),
                        narrative=fir_data.get("narrative"),
                        ipc_sections=fir_data.get("ipc_sections", []),
                        mo_tags=fir_data.get("mo_tags", []),
                        loc_name=loc.get("name"),
                        lat=loc.get("lat"),
                        lng=loc.get("lng"),
                        suspects_involved=fir_data.get("suspects_involved", []))

# Singleton instance
neo4j_client = Neo4jClient()
