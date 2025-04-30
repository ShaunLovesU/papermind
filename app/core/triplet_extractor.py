import re
from typing import List, Tuple


def extract_triplets(chunks: List[str]) -> List[Tuple[str, str, str]]:
    '''
    Extract (head, relation, tail) triplets from a list of text chunks using simple regex rules.
    :param chunks:Cleaned and chunked text segments.
    :return:Extracted knowledge triplets.
    '''
    triplets = []

    for chunk in chunks:
        lines = chunk.split(".")  # crude sentence splitter
        for line in lines:
            sentence = line.strip()
            if not sentence:
                continue

            # Rule: X proposed Y
            match = re.search(r"([\w\s\-]+?)\s+(proposed|introduced|presented)\s+(the\s+)?([\w\s\-]+)", sentence, re.IGNORECASE)
            if match:
                head = match.group(1).strip()
                relation = match.group(2).strip().lower()
                tail = match.group(4).strip()
                triplets.append((head, relation, tail))
                continue

            # Rule: X is based on Y
            match = re.search(r"([\w\s\-]+?)\s+is\s+based\s+on\s+([\w\s\-]+)", sentence, re.IGNORECASE)
            if match:
                triplets.append((match.group(1).strip(), "based_on", match.group(2).strip()))
                continue

            # Rule: X uses Y
            match = re.search(r"([\w\s\-]+?)\s+uses\s+([\w\s\-]+)", sentence, re.IGNORECASE)
            if match:
                triplets.append((match.group(1).strip(), "uses", match.group(2).strip()))
                continue

            # Rule: X evaluates Y
            match = re.search(r"([\w\s\-]+?)\s+evaluates\s+([\w\s\-]+)", sentence, re.IGNORECASE)
            if match:
                triplets.append((match.group(1).strip(), "evaluates", match.group(2).strip()))
                continue

    return triplets
