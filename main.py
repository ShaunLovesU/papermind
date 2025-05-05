# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"message": "PaperMind is running"}


from app.core.pdf_parser import parse_pdf
from app.core.triplet_extractor import extract_triplets_openai
from io import BytesIO

if __name__ == "__main__":
    # Load test PDF
    with open("examples/CSC475_575_Final_Report.pdf", "rb") as f:
        file_stream = BytesIO(f.read())

    # Step 1: Extract cleaned text chunks
    chunks = parse_pdf(file_stream)

    # Step 2: Extract triplets using OpenAI
    triplets = extract_triplets_openai(chunks)

    # Show results
    for h, r, t in triplets:
        print(f"({h}) --[{r}]--> ({t})")
