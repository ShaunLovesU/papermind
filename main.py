from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api import qa_api

app = FastAPI(
    title="PaperMind API",
    description="A knowledge-driven QA system based on graph RAG.",
    version="1.0.0"
)

# Enable CORS (especially for local frontend dev)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # in production, specify frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(qa_api.router)

# Optional root route
@app.get("/")
def read_root():
    return {"message": "PaperMind backend is running."}
