"""
Title: Embeddings Client
Abstract: Service to generate local text embeddings using FastEmbed (ONNX).
Why: Enables semantic similarity search and caching without external API calls.
Dependencies: numpy, fastembed, logging, typing, sdk.exceptions
"""

import logging
from typing import List
import numpy as np
from fastembed import TextEmbedding
from sdk.exceptions import CacheError

logger = logging.getLogger(__name__)

class LocalEmbeddings:
    """
    Service to generate local text embeddings.
    Follows Pillar 1 (Strict Typing) and Pillar 4 (Traceability).
    """
    
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5") -> None:
        """Initializes the FastEmbed model."""
        try:
            self.model = TextEmbedding(model_name=model_name)
            logger.info(f"Initialized LocalEmbeddings with model: {model_name}")
        except Exception as e:
            logger.error(f"Failed to initialize embeddings model: {e}")
            raise CacheError(f"Embeddings initialization failed: {e}") from e
    
    def generate_vector(self, text: str) -> List[float]:
        """Generates a high-dimensional vector for the given text."""
        try:
            embeddings = list(self.model.embed([text]))
            return embeddings[0].tolist()
        except Exception as e:
            logger.error(f"Failed to generate vector: {e}")
            raise CacheError(f"Vector generation failed: {e}") from e

    def calculate_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculates cosine similarity between two vectors."""
        try:
            v1 = np.array(vector1)
            v2 = np.array(vector2)
            norm = (np.linalg.norm(v1) * np.linalg.norm(v2))
            if norm == 0:
                return 0.0
            return float(np.dot(v1, v2) / norm)
        except Exception as e:
            logger.error(f"Similarity calculation failed: {e}")
            raise CacheError(f"Similarity calculation failed: {e}") from e

if __name__ == "__main__":
    # Example usage
    logging.basicConfig(level=logging.INFO)
    client = LocalEmbeddings()
    v1 = client.generate_vector("Hello world")
    v2 = client.generate_vector("Hello universe")
    sim = client.calculate_similarity(v1, v2)
    print(f"Similarity: {sim:.4f}")
