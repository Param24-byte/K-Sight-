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
        if api_key == "MOCK_KEY_FOR_DATATHON":
            logger.warning("Gemini API not configured properly, using fallback mode.")
            self.model = None
        else:
            try:
                self.model = genai.GenerativeModel('gemini-1.5-pro')
            except Exception as e:
                logger.warning("Gemini API error, using fallback mode.")
                self.model = None

    def ask(self, query: str, language: str = "English", history: list = None) -> dict:
        """Hybrid RAG implementation"""
        logger.info(f"Processing AI Query: {query}")
        
        # 1. Retrieve Semantic Context from Qdrant
        confidence = 0.0
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
            if search_result:
                scores = [hit.score for hit in search_result]
                confidence = round(sum(scores) / len(scores), 2)
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
        history_text = ""
        if history:
            history_text = "Previous Conversation Context:\n"
            for m in history:
                role = "User" if m["role"] == "user" else "Assistant"
                history_text += f"{role}: {m['content']}\n"

        prompt = f"""
        You are an elite Crime Intelligence AI for the Karnataka State Police.
        Answer the user's query using ONLY the provided evidence. Cite the FIR IDs in your answer.
        You MUST reply exclusively in {language}.
        
        {history_text}
        
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
            if language == "Kannada":
                answer = f"ಮಾಕ್ ಎಐ ಪ್ರತಿಕ್ರಿಯೆ (Mock AI Response in Kannada):\n\n{fir_context}\n\n{graph_context}"
            else:
                answer = f"Mocked AI Response based on context:\n\n{fir_context}\n\n{graph_context}"

        return {
            "answer": answer,
            "confidence": confidence,
            "citations": [hit.payload.get("fir_id") for hit in search_result] if 'search_result' in locals() else []
        }

llm_client = LLMClient()
