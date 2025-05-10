from typing import List, Tuple
from openai import OpenAI
from app.core.config import settings


client = OpenAI(api_key=settings.OPENAI_API_KEY)


def format_triplets_for_prompt(triplets: List[Tuple[str, str, str]]) -> str:
    """
    Format triplets into readable sentences to be used in GPT prompt context.
    """
    lines = [f"{h} {r.replace('_', ' ').lower()} {t}." for h, r, t in triplets]
    return "\n".join(lines)


def generate_answer(question: str, triplets: List[Tuple[str, str, str]], model: str = None) -> str:
    """
    Generate a natural language answer using GPT based on question and triplets.

    Args:
        question (str): User's question.
        triplets (List[Tuple[str, str, str]]): Retrieved knowledge from graph.
        model (str): Optional override model.

    Returns:
        str: GPT-generated answer.
    """
    if not triplets:
        return "No knowledge available to answer the question."

    try:
        model = model or settings.OPENAI_MODEL

        context = format_triplets_for_prompt(triplets)

        system_prompt = (
            "You are a strict assistant. You must answer the user's question "
            "using ONLY the provided knowledge. If the knowledge does not contain "
            "the answer, respond with exactly: 'No.' Do not guess. Do not add anything extra."
        )

        user_prompt = (
            f"Knowledge:\n{context}\n\n"
            f"Question:\n{question}\n\n"
            "Answer:"
        )

        response = client.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature=0.2
        )

        return response.choices[0].message.content.strip()

    except Exception as e:
        print(f"Error while generating answer: {e}")
        return "Answer generation failed due to an internal error."
