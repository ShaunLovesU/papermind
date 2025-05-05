import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

class Settings:
    # OpenAI configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")

    # Neo4j configuration
    NEO4J_URI = os.getenv("NEO4J_URI")
    NEO4J_USER = os.getenv("NEO4J_USER")
    NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

    def __init__(self):
        # Check required configs
        if not self.OPENAI_API_KEY:
            raise ValueError("OPENAI_API_KEY is not set in .env")
        if not self.NEO4J_URI or not self.NEO4J_USER or not self.NEO4J_PASSWORD:
            raise ValueError("Neo4j connection information is incomplete in .env")


# Instantiate the config
settings = Settings()
