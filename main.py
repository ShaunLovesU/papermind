# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "PaperMind is running"}


from app.core.pdf_parser import parse_pdf
from app.core.triplet_extractor import extract_triplets_openai
from io import BytesIO

from app.core.rag_answerer import generate_answer

triplets = [
    ("Transformer", "IS_BASED_ON", "Self-attention mechanism"),
    ("Transformer", "USES", "Positional encoding"),
]

question = "transformer?"
answer = generate_answer(question, triplets)
print(answer)

