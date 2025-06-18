from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Tuple
from app.core.graph_query import GraphQueryWithEmbedding
from app.core.rag_answerer import generate_answer
from app.core.config import settings

router = APIRouter()


class QARequest(BaseModel):
    question: str


class QAResponse(BaseModel):
    answer: str
    triplets: List[Tuple[str, str, str]]


@router.post("/api/answer", response_model=QAResponse)
def answer_question(request: QARequest):
    try:
        query_client = GraphQueryWithEmbedding(
            settings.NEO4J_URI,
            settings.NEO4J_USER,
            settings.NEO4J_PASSWORD
        )

        question = request.question
        embedding = query_client.get_text_embedding(question)

        if not embedding:
            raise HTTPException(status_code=500, detail="Failed to generate embedding.")

        entities = query_client.find_top_k_entities(embedding, top_k=3, processes=4)
        triplets = query_client.get_triplets_by_entities(entities)

        answer = generate_answer(question, triplets)

        query_client.close()

        return QAResponse(answer=answer, triplets=triplets)

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
