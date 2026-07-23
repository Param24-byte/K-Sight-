from neo4j import GraphDatabase
import logging
import os

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Neo4jClient:
    def __init__(self, uri=None, user=None, password=None):
        _uri = uri or os.getenv("NEO4J_URI", "bolt://localhost:7687")
        _user = user or os.getenv("NEO4J_USER", "neo4j")
        _password = password or os.getenv("NEO4J_PASSWORD", "password")
        self.driver = GraphDatabase.driver(_uri, auth=(_user, _password))
        
    def close(self):
        self.driver.close()

    def setup_constraints(self):
        """Creates unique constraints to prevent duplicate nodes during ingestion"""
        queries = [
            "CREATE CONSTRAINT IF NOT EXISTS FOR (c:Complainant) REQUIRE c.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (v:Victim) REQUIRE v.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (a:Accused) REQUIRE a.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (i:Incident) REQUIRE i.fir_id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (act:Act) REQUIRE act.id IS UNIQUE",
            "CREATE CONSTRAINT IF NOT EXISTS FOR (sec:Section) REQUIRE sec.id IS UNIQUE",
        ]
        with self.driver.session() as session:
            for query in queries:
                session.run(query)
        logger.info("Neo4j constraints verified.")

    def clear_database(self):
        with self.driver.session() as session:
            session.run("MATCH (n) DETACH DELETE n")

    def ingest_act_section(self, act_data, section_data):
        query = """
        MERGE (act:Act {id: $act_code})
        SET act.name = $act_name
        
        MERGE (sec:Section {id: $sec_id})
        SET sec.code = $sec_code, sec.description = $sec_desc
        
        MERGE (sec)-[:BELONGS_TO]->(act)
        """
        with self.driver.session() as session:
            session.run(query,
                        act_code=act_data["ActCode"],
                        act_name=act_data["ActDescription"],
                        sec_id=section_data["id"],
                        sec_code=section_data["SectionCode"],
                        sec_desc=section_data["SectionDescription"])

    def ingest_cases_batch(self, cases_payload):
        """Ingests a batch of fully relational case graphs"""
        query = """
        UNWIND $payload AS row
        
        // 1. Incident & Location
        MERGE (i:Incident {fir_id: row.CrimeNo})
        SET i.case_no = row.CaseNo,
            i.date = row.CrimeRegisteredDate,
            i.brief_facts = row.BriefFacts,
            i.status = row.CaseStatusID
            
        MERGE (l:Location {lat: row.latitude, lng: row.longitude})
        MERGE (i)-[:OCCURRED_AT]->(l)
        
        // 2. Sections invoked
        WITH i, row
        UNWIND row.sections AS sec_id
        MERGE (sec:Section {id: sec_id})
        MERGE (i)-[:INVOKES]->(sec)
        
        // 3. Complainants
        WITH i, row
        UNWIND row.complainants AS comp
        MERGE (c:Complainant {id: comp.id})
        SET c.name = comp.name, c.age = comp.age
        MERGE (c)-[:FILED]->(i)
        
        // 4. Victims
        WITH i, row
        UNWIND row.victims AS vic
        MERGE (v:Victim {id: vic.id})
        SET v.name = vic.name, v.age = vic.age
        MERGE (v)-[:VICTIM_IN]->(i)
        
        // 5. Accused
        WITH i, row
        UNWIND row.accused AS acc
        MERGE (a:Accused {id: acc.id})
        SET a.name = acc.name, a.age = acc.age
        MERGE (a)-[:IS_ACCUSED_IN]->(i)
        """
        with self.driver.session() as session:
            session.run(query, payload=cases_payload)

neo4j_client = Neo4jClient()
