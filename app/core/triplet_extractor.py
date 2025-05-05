import os
from typing import List, Tuple
from openai import OpenAI
from dotenv import load_dotenv
import json
# Load environment variables from .env
load_dotenv()

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
model = os.getenv("OPENAI_MODEL", "gpt-3.5-turbo")



def extract_triplets_openai(chunks: List[str], batch_size: int = 10) -> List[Tuple[str, str, str]]:
    '''
    Extract triplets (subject, relation, object) from a list of text chunks using OpenAI GPT.
    :param chunks: A list of text chunks.
    :return:A list of extracted triplets.
    '''
    triplets = []

    # System prompt defines extraction rule
    system_prompt = (
        "You are a knowledge extractor.\n"
        "Given the following numbered paragraphs, extract all possible factual (subject, relation, object) triplets from each paragraph.\n"
        "\n"
        "A valid triplet follows:\n"
        "- Subject: The entity that performs or holds something\n"
        "- Relation: The action, relation or property\n"
        "- Object: The entity that receives or is associated with the subject\n"
        "\n"
        "Your response MUST ONLY be a valid JSON object, in this format:\n"
        "{\n"
        "  \"Paragraph 1\": [[subject, relation, object], [subject, relation, object]],\n"
        "  \"Paragraph 2\": []\n"
        "}\n"
        "\n"
        "Rules:\n"
        "- Do NOT add explanations.\n"
        "- Do NOT output anything except the JSON object.\n"
        "- Extract all possible relations, even simple or obvious ones."
    )

# Process in batches
    for i in range(0, len(chunks), batch_size):
        batch = chunks[i:i + batch_size]

        # Build numbered paragraphs
        paragraphs = ""
        for idx, text in enumerate(batch, start=1):
            paragraphs += f"Paragraph {idx}: {text.strip()}\n"

        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": paragraphs}
        ]

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                temperature=0,
            )
            content = response.choices[0].message.content.strip()

            # Parse JSON result
            extracted = json.loads(content)

            for key, triplet_list in extracted.items():
                for t in triplet_list:
                    if isinstance(t, list) and len(t) == 3:
                        triplets.append(tuple(t))

        except Exception as e:
            print(f"[OpenAI Error] Failed to process batch. Skipping. Error: {e}")

    return triplets