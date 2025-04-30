import re
from io import BytesIO
from typing import List
from unstructured.partition.pdf import partition_pdf
from unstructured.documents.elements import Text
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document


def clean_text(text: str) -> str:
    '''
    :param text:
    :return: cleaned text
    Clean and normalize raw text extracted from PDF elements.
    This includes:
    - Merging words broken by hyphen and newline (e.g., "multi- modal" → "multimodal")
    - Removing redundant line breaks
    - Collapsing multiple spaces
    '''
    # Merge hyphenated line breaks
    text = re.sub(r"(\w)-\s+(\w)", r"\1\2", text)
    # Merge broken lines
    text = re.sub(r"\n+", " ", text)
    # Normalize whitespace
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()




def parse_pdf(file: BytesIO) -> list[str]:
    '''
    :param PDF file
    This function parse PDF fille and return structured Text element list
    :return:structured Text element list
    '''

    elements = partition_pdf(
        file = file,
        strategy= "fast",
    )
    text_elements = []
    for element in elements:
        if not isinstance(element, Text):
            continue
        if element.category in ['Title', 'NarrativeText', 'ListItem', 'FigureCaption', 'Table', 'Formula']:
            # handle new line
            element.apply(clean_text)
            text_elements.append(Document(page_content=element.text))

    splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
    chunks = splitter.split_documents(text_elements)
    return [chunk.page_content for chunk in chunks]