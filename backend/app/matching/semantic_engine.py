import logging
from typing import List

logger = logging.getLogger(__name__)

class SemanticEngine:
    _instance = None
    _model = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(SemanticEngine, cls).__new__(cls)
            cls._instance._init_model()
        return cls._instance

    def _init_model(self):
        try:
            from sentence_transformers import SentenceTransformer
            # Using a lightweight local model suitable for semantic textual similarity
            logger.info("Loading sentence-transformers/all-MiniLM-L6-v2 ...")
            self._model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Model loaded successfully.")
        except Exception as e:
            logger.error(f"Failed to load sentence-transformers model: {e}")
            self._model = None

    def compute_similarity(self, text1: str, text2: str) -> float:
        """
        Computes cosine similarity between two strings.
        Returns a float between 0 and 1.
        """
        if not self._model or not text1 or not text2:
            return 0.0

        from sklearn.metrics.pairwise import cosine_similarity
        
        try:
            embeddings = self._model.encode([text1, text2])
            sim = cosine_similarity([embeddings[0]], [embeddings[1]])[0][0]
            # Convert numpy float to native Python float
            return float(max(0.0, min(1.0, sim)))
        except Exception as e:
            logger.error(f"Similarity computation error: {e}")
            return 0.0

    def compute_similarity_batch(self, query: str, texts: List[str]) -> List[float]:
        """
        Computes cosine similarity between a single query and multiple texts.
        """
        if not self._model or not query or not texts:
            return [0.0] * len(texts)

        from sklearn.metrics.pairwise import cosine_similarity
        
        try:
            all_texts = [query] + texts
            embeddings = self._model.encode(all_texts)
            query_emb = embeddings[0:1]
            texts_emb = embeddings[1:]
            
            sims = cosine_similarity(query_emb, texts_emb)[0]
            return [float(max(0.0, min(1.0, s))) for s in sims]
        except Exception as e:
            logger.error(f"Batch similarity computation error: {e}")
            return [0.0] * len(texts)

# Singleton access
semantic_engine = SemanticEngine()
