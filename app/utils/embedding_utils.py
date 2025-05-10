import numpy as np
from typing import List, Dict
from openai import OpenAI, APIError
from app.core.config import settings
from multiprocessing import Pool, cpu_count
import time

client = OpenAI(api_key=settings.OPENAI_API_KEY)


def get_text_embedding(text: str, model: str = "text-embedding-3-small") -> List[float]:
    """
    Generate embedding vector for a given input text using OpenAI's embedding API.

    Args:
        text (str): The text to embed.
        model (str): The embedding model to use.

    Returns:
        List[float]: The embedding vector (or empty list if failed).
    """
    try:
        response = client.embeddings.create(
            model=model,
            input=[text]
        )
        return response.data[0].embedding
    except APIError as e:
        print(f"OpenAI API Error while embedding text: {e}")
    except Exception as e:
        print(f"Unexpected error during embedding: {e}")

    return []  # Return empty list on failure


def cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
    """
    Compute cosine similarity between two vectors.

    Args:
        vec1 (List[float]): First vector.
        vec2 (List[float]): Second vector.

    Returns:
        float: Cosine similarity in the range [-1, 1], or 0.0 if inputs are invalid.
    """
    try:
        a = np.array(vec1)
        b = np.array(vec2)
        if a.shape != b.shape or a.size == 0:
            return 0.0
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))
    except Exception as e:
        print(f"Error computing cosine similarity: {e}")
        return 0.0

def _embed_text_safe(text: str) -> tuple[str, List[float]]:
    """
    Safe wrapper for multiprocessing.
    """
    embedding = get_text_embedding(text)
    return (text, embedding)


def batch_get_embeddings(texts: List[str], processes: int = 4) -> Dict[str, List[float]]:
    """
    Compute OpenAI embeddings for a list of texts using multiprocessing.

    Args:
        texts (List[str]): List of text inputs to embed.
        processes (int): Number of processes to use.

    Returns:
        Dict[str, List[float]]: Mapping from text → embedding.
    """
    start = time.time()

    with Pool(processes=processes) as pool:
        results = pool.map(_embed_text_safe, texts)

    embedding_map = {text: emb for text, emb in results if emb}

    print(f"Embedded {len(embedding_map)}/{len(texts)} texts in {round(time.time() - start, 2)}s.")
    return embedding_map
