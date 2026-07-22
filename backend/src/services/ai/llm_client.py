import os
import google.generativeai as genai
import logging
from src.services.graph.neo4j_client import neo4j_client
from src.services.ai.qdrant_client import vector_client

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure API Key (Mock for datathon unless set in .env)
api_key = os.getenv("GEMINI_API_KEY", "MOCK_KEY_FOR_DATATHON")
if api_key != "MOCK_KEY_FOR_DATATHON":
    genai.configure(api_key=api_key)

class LLMClient:
    def __init__(self):
        try:
            self.model = genai.GenerativeModel('gemini-1.5-pro')
        except Exception as e:
            logger.warning("Gemini API not configured properly, using fallback mode.")
            self.model = None

    def ask(self, query: str) -> dict:
        """Hybrid RAG implementation"""
        logger.info(f"Processing AI Query: {query}")
        
        # 1. Retrieve Semantic Context from Qdrant
        embedding = vector_client.encoder.encode(query).tolist()
        try:
            search_result = vector_client.client.search(
                collection_name=vector_client.collection_name,
                query_vector=embedding,
                limit=3
            )
            fir_context = "\n".join([
                f"FIR {hit.payload.get('fir_id')} at {hit.payload.get('location')}: {hit.payload.get('narrative')}" 
                for hit in search_result
            ])
        except Exception:
            fir_context = "Could not reach Qdrant for semantic search."

        # 2. Retrieve Graph Context from Neo4j (Simple global stats for demo)
        graph_context = ""
        try:
            with neo4j_client.driver.session() as session:
                res = session.run("MATCH (i:Incident) RETURN count(i) as total_firs")
                total = res.single()["total_firs"]
                graph_context = f"The knowledge graph currently holds {total} recorded incidents."
        except Exception:
            graph_context = "Could not reach Neo4j for graph search."

        # 3. Construct the Augmented Prompt
        prompt = f"""
        You are an elite Crime Intelligence AI for the Karnataka State Police.
        Answer the user's query using ONLY the provided evidence. Cite the FIR IDs in your answer.
        
        User Query: "{query}"
        
        Evidence (Vector DB):
        {fir_context}
        
        Evidence (Graph DB):
        {graph_context}
        """

        # 4. Generate Response
        if self.model:
            response = self.model.generate_content(prompt)
            answer = response.text
        else:
            answer = f"Mocked AI Response based on context:\n\n{fir_context}\n\n{graph_context}"

        return {
            "answer": answer,
            "confidence": 0.85, # In a real implementation, calculate based on distance scores
            "citations": [hit.payload.get("fir_id") for hit in search_result] if 'search_result' in locals() else []
        }

llm_client = LLMClient()
