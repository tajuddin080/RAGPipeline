"""
Data ingestion and preprocessing for RAG.
"""

import re
from functools import partial

from langchain_core.documents import Document

from langchain_community.document_loaders import (
    TextLoader,
    DirectoryLoader,
)
from langchain_text_splitters import RecursiveCharacterTextSplitter

# ----------------------------------------------------
# Load documents
# ----------------------------------------------------

def load_directory(
    path="./app/knowledge_base",
    glob="**/*.txt",
    loader_cls=partial(TextLoader, encoding="UTF-8"),
):

    directory_loader = DirectoryLoader(
        path=path,
        glob=glob,
        loader_cls=loader_cls,
    )

    documents = directory_loader.load()

    return document_clean(documents)


# ----------------------------------------------------
# Generic metadata extractor
# ----------------------------------------------------

def extract_section_metadata(section_text: str):
    """
    Separates actual section content from metadata blocks.

    Returns:
        cleaned_content
        metadata dictionary
    """

    metadata = {}
    cleaned_content = []

    block_mapping = {
        "Keywords:": "keywords",
        "Synonyms:": "synonyms",
        "Related Topics:": "related_topics",
    }

    current_block = None

    for line in section_text.splitlines():

        line = line.strip()

        if not line:
            continue

        # New metadata block starts
        if line in block_mapping:
            current_block = block_mapping[line]
            metadata[current_block] = []
            continue

        # Collect metadata
        if current_block:
            metadata[current_block].append(line)

        # Otherwise normal content
        else:
            cleaned_content.append(line)

    return "\n".join(cleaned_content), metadata


# ----------------------------------------------------
# Document cleaning
# ----------------------------------------------------

def document_clean(documents):

    for doc in documents:

        text = doc.page_content

        text = re.sub(
            r"^\s*=+\s*$",
            "",
            text,
            flags=re.MULTILINE,
        )

        text = re.sub(
            r"^\s*-+\s*$",
            "",
            text,
            flags=re.MULTILINE,
        )

        text = re.sub(
            r"\n{3,}",
            "\n\n",
            text,
        )

        title = re.search(r"^(.*?)\n", text)
        version = re.search(r"Document Version:\s*(.*)", text)
        department = re.search(r"Department:\s*(.*)", text)
        effective_date = re.search(r"Effective Date:\s*(.*)", text)

        doc.metadata.update(
            {
                "title": title.group(1).strip() if title else None,
                "version": version.group(1).strip() if version else None,
                "department": department.group(1).strip()
                if department
                else None,
                "eff_date": effective_date.group(1).strip()
                if effective_date
                else None,
            }
        )

        match = re.search(
            r"(?i)Section\s+1:",
            text,
        )

        if match:
            doc.page_content = text[match.start():]

    return split_data_and_metadata(documents)


# ----------------------------------------------------
# Split into sections
# ----------------------------------------------------

def split_data_and_metadata(final_document):

    section_documents = []

    for doc in final_document:

        sections = re.split(
            r"(?=Section\s+\d+:)",
            doc.page_content
        )

        for section in sections:

            section = section.strip()

            if not section:
                continue

            lines = section.splitlines()

            section_title = lines[0].strip()

            section_body = "\n".join(lines[1:])

            # ----------------------------
            # Extract section metadata
            # ----------------------------

            section_body, section_metadata = extract_section_metadata(
                section_body
            )

            section_doc = Document(
                page_content=section_body.strip(),
                metadata={
                    **doc.metadata,
                    "section_title":section_title,
                    **section_metadata
                    }
            )

            section_documents.append(section_doc)

    return split_the_chunks(section_documents)

# ----------------------------------------------------
# Chunking
# ----------------------------------------------------

def split_the_chunks(docs):

    splitter = RecursiveCharacterTextSplitter(
        separators=[
            r"(?i)section\s+\d+:",
            "\n\n",
            "\n",
            " ",
            "",
        ],
        chunk_size=300,
        chunk_overlap=45,
    )

    return splitter.split_documents(docs)


# ----------------------------------------------------
# Public function
# ----------------------------------------------------

def get_chunks():
    return load_directory()
