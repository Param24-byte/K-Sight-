from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from sentence_transformers import SentenceTransformer
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class VectorDBClient:
    def __init__(self, host="localhost", port=6333):
        # We load the embedding model in memory
        self.encoder = SentenceTransformer('all-MiniLM-L6-v2')
        self.client = QdrantClient(host=host, port=port)
        self.collection_name = "firs"
        
    def setup_collection(self):
        """Creates the Qdrant collection if it does not exist"""
        if not self.client.collection_exists(collection_name=self.collection_name):
            self.client.create_collection(
                collection_name=self.collection_name,
                vectors_config=VectorParams(size=384, distance=Distance.COSINE),
            )
            logger.info(f"Created Qdrant collection: {self.collection_name}")
        else:
            logger.info(f"Qdrant collection '{self.collection_name}' already exists.")

    def ingest_firs(self, firs_data: list):
        """Generates embeddings for FIR narratives and upserts to Qdrant"""
        points = []
        for idx, fir in enumerate(firs_data):
            # We want the vector to represent the narrative, MO, and crime type
            text_to_embed = f"Crime: {fir.get('type')}. MO: {', '.join(fir.get('mo_tags', []))}. Narrative: {fir.get('narrative')}"
            
            embedding = self.encoder.encode(text_to_embed).tolist()
            
            # Use a numeric ID for Qdrant, we'll map it using the fir_id in payload
            points.append(
                PointStruct(
                    id=idx + 1,
                    vector=embedding,
                    payload={
                        "fir_id": fir.get("fir_id"),
                        "type": fir.get("type"),
                        "location": fir.get("location", {}).get("name"),
                        "date": fir.get("date"),
                        "narrative": fir.get("narrative")
                    }
                )
            )
        
        # Upsert in batches of 100 for performance
        batch_size = 100
        for i in range(0, len(points), batch_size):
            batch = points[i:i + batch_size]
            self.client.upsert(
                collection_name=self.collection_name,
                points=batch
            )
        logger.info(f"Upserted {len(points)} FIR vectors to Qdrant.")

# Singleton instance
vector_client = VectorDBClient()
