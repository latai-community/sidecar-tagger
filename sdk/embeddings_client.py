import numpy as np
from typing import List, Optional
from fastembed import TextEmbedding

class LocalEmbeddings:
    """Service to generate local text embeddings using FastEmbed (ONNX)."""
    
    def __init__(self, model_name: str = "BAAI/bge-small-en-v1.5"):
        # bge-small-en-v1.5 is lightweight (~100MB) and very fast on CPU
        self.model = TextEmbedding(model_name=model_name)
    
    def generate_vector(self, text: str) -> List[float]:
        """Generates a high-dimensional vector for the given text."""
        # FastEmbed expects a list of documents
        embeddings = list(self.model.embed([text]))
        # Return the first (and only) embedding as a list of floats
        return embeddings[0].tolist()

    def calculate_similarity(self, vector1: List[float], vector2: List[float]) -> float:
        """Calculates cosine similarity between two vectors."""
        v1 = np.array(vector1)
        v2 = np.array(vector2)
        return float(np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2)))
