"""
Data ingestion and preprocessing for RAG.

Detects file format automatically (PDF / TXT / Markdown / HTML)
and applies the most appropriate LangChain loader + splitter.

Required packages (already in pyproject.toml):
  langchain-community, langchain-text-splitters

Optional – install to unlock the format:
  pypdf  →  PDF support   (uv add pypdf)
"""

import os
import re
import hashlib
from datetime import datetime, timezone
from pathlib import Path
from functools import partial

from langchain_core.documents import Document
from langchain_community.document_loaders import (
    TextLoader,
    BSHTMLLoader,
    DirectoryLoader,
)
from langchain_text_splitters import (
    RecursiveCharacterTextSplitter,
    MarkdownHeaderTextSplitter,
)

# ----------------------------------------------------------------
# Constants
# ----------------------------------------------------------------

KNOWLEDGE_BASE_PATH = "./app/knowledge_base"
CHUNK_SIZE    = 300
CHUNK_OVERLAP = 45

_PDF_TABLE_HEADERS = {
    "document issued by deadline",
    "item responsible team lead time required",
    "time activity owner",
    "milestone description success indicator",
    "function track duration key focus areas",
    "checkpoint manager action timeline",
    "benefit coverage employee action required",
    "benefit eligibility details",
    "outcome criteria hr action",
    "item provided by return required?",
    "metric target reviewed",
    "term definition",
    "grade role level notice period (employer) notice period (employee)",
    "scenario approver impact",
    "area details required deadline",
    "step action owner timeline",
    "department what they clear cleared by",
    "incomplete item consequence",
    "component payable / recoverable details",
    "activity timeline",
    "item return to consequence if not returned",
    "entitlement details",
}

# Supported extensions → (glob, loader_factory, format_label)
_FORMAT_CONFIG: dict[str, tuple[str, object, str]] = {
    ".txt":  ("**/*.txt",  partial(TextLoader, encoding="utf-8"), "txt"),
    ".md":   ("**/*.md",   partial(TextLoader, encoding="utf-8"), "md"),
    ".html": ("**/*.html", BSHTMLLoader,                          "html"),
    ".htm":  ("**/*.htm",  BSHTMLLoader,                          "html"),
}

# Lazily add PDF support when pypdf is available
try:
    from langchain_community.document_loaders import PyPDFLoader
    _FORMAT_CONFIG[".pdf"] = ("**/*.pdf", PyPDFLoader, "pdf")
except ImportError:
    PyPDFLoader = None  # type: ignore[assignment]

# ----------------------------------------------------------------
# Internal helpers
# ----------------------------------------------------------------

def _file_hash(path: Path) -> str | None:
    """Short SHA-256 hex digest of file bytes (first 16 chars)."""
    if not path.exists():
        return None
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(8192), b""):
            h.update(chunk)
    return h.hexdigest()[:16]


def _enrich_metadata(doc: Document, fmt: str) -> None:
    """
    Attach file-level metadata to *doc*.  Fields set:

    file_name     – bare filename with extension
    file_format   – detected format  (pdf / txt / md / html)
    file_size_kb  – size on disk in kilobytes
    file_hash     – short SHA-256 for deduplication
    source_path   – normalised absolute path
    ingested_at   – ISO-8601 UTC timestamp of this run
    page          – page index (PDF only; kept from PyPDFLoader)
    """
    src = doc.metadata.get("source", "")
    path = Path(src)
    stat = path.stat() if path.exists() else None

    doc.metadata.update({
        "file_name"   : path.name,
        "file_format" : fmt,
        "file_size_kb": round(stat.st_size / 1024, 2) if stat else None,
        "file_hash"   : _file_hash(path),
        "source_path" : str(path.resolve()) if path.exists() else src,
        "ingested_at" : datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    })


def _clean_text(text: str) -> str:
    """Remove decorative separator lines and collapse excess blank lines."""
    text = re.sub(r"^\s*[=\-]{2,}\s*$", "", text, flags=re.MULTILINE)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()


# ----------------------------------------------------------------
# Public – load_directory
# ----------------------------------------------------------------

def load_directory(path: str = KNOWLEDGE_BASE_PATH) -> list[Document]:
    """
    Walk *path* and load every supported document type.

    A separate DirectoryLoader is spun up for each format so the
    correct loader class is applied per file.  All documents are
    merged, metadata-enriched, and returned.

    Supported: TXT, Markdown, HTML/HTM, PDF (when pypdf installed).
    """
    all_docs: list[Document] = []

    for ext, (glob, loader_cls, fmt_label) in _FORMAT_CONFIG.items():
        loader = DirectoryLoader(
            path=path,
            glob=glob,
            loader_cls=loader_cls,
            silent_errors=True,
            show_progress=False,
        )
        try:
            docs = loader.load()
        except Exception as exc:
            print(f"[pre_processing] Warning – could not load {ext} files: {exc}")
            docs = []

        for doc in docs:
            doc.page_content = _clean_text(doc.page_content)
            _enrich_metadata(doc, fmt_label)

        all_docs.extend(docs)

    if not all_docs:
        print(f"[pre_processing] Warning – no documents found in: {path}")

    return all_docs


# ----------------------------------------------------------------
# Internal – chunking
# ----------------------------------------------------------------

def _md_chunks(doc: Document) -> list[Document]:
    """
    Split a Markdown document first by headings, then by size.

    Heading levels (H1–H3) are recorded as metadata so each chunk
    knows which section it belongs to.
    """
    headers = [
        ("#",   "h1"),
        ("##",  "h2"),
        ("###", "h3"),
    ]
    md_splitter = MarkdownHeaderTextSplitter(
        headers_to_split_on=headers,
        strip_headers=False,
    )
    char_splitter = RecursiveCharacterTextSplitter(
        separators=["\n\n", "\n", ". ", " ", ""],
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )

    # Split by headings first
    header_sections = md_splitter.split_text(doc.page_content)

    chunks: list[Document] = []
    for section in header_sections:
        sub = char_splitter.split_text(section.page_content)
        for piece in sub:
            chunks.append(Document(
                page_content=piece,
                metadata={**doc.metadata, **section.metadata},
            ))
    return chunks


def _generic_chunks(doc: Document, separators: list[str]) -> list[Document]:
    """Split *doc* with RecursiveCharacterTextSplitter."""
    splitter = RecursiveCharacterTextSplitter(
        separators=separators,
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
    )
    return splitter.split_documents([doc])


def _pdf_table_chunks(doc: Document) -> list[Document]:
    lines = doc.page_content.splitlines()
    table_chunks: list[Document] = []

    for header_index, line in enumerate(lines):
        header = " ".join(line.lower().split())
        if header not in _PDF_TABLE_HEADERS:
            continue

        section = next(
            (
                previous.strip()
                for previous in reversed(lines[:header_index])
                if re.match(r"^\d+(?:\.\d+)*\s+", previous.strip())
            ),
            doc.metadata.get("file_name", "PDF table"),
        )

        for row in lines[header_index + 1:]:
            row = row.strip()
            if (
                not row
                or row.lower() in _PDF_TABLE_HEADERS
                or row.startswith("INTERNAL - CONFIDENTIAL")
                or re.match(r"^\d+(?:\.\d+)*\s+", row)
                or row.lower().startswith(("note", "important", "sla"))
            ):
                break

            table_chunks.append(Document(
                page_content=f"{section}\nTable columns: {line.strip()}\nTable row: {row}",
                metadata={**doc.metadata, "table_row": True},
            ))

    return table_chunks


def _split_documents(docs: list[Document]) -> list[Document]:
    """
    Chunk each document with the splitter appropriate for its format.

    After chunking, chunk_index and total_chunks are added to
    each chunk's metadata so the vector store can reconstruct
    reading order.
    """
    # Format → separator hierarchy
    _separators: dict[str, list[str]] = {
        "pdf" : ["\n\n", "\n", ". ", " ", ""],
        "txt" : ["\n\n", "\n", " ", ""],
        "html": ["\n\n", "\n", ". ", " ", ""],
    }

    all_chunks: list[Document] = []

    for doc in docs:
        fmt = doc.metadata.get("file_format", "txt")

        if fmt == "pdf":
            # Keep each page intact and index table rows separately for retrieval.
            chunks = [doc, *_pdf_table_chunks(doc)]
        elif fmt == "md":
            chunks = _md_chunks(doc)
        else:
            chunks = _generic_chunks(doc, _separators.get(fmt, ["\n\n", "\n", " ", ""]))

        all_chunks.extend(chunks)

    # ---- Tag each chunk with its position inside its parent file ----
    counters: dict[str, int] = {}
    for chunk in all_chunks:
        key = chunk.metadata.get("source_path", chunk.metadata.get("source", ""))
        idx = counters.get(key, 0)
        chunk.metadata["chunk_index"] = idx
        counters[key] = idx + 1

    for chunk in all_chunks:
        key = chunk.metadata.get("source_path", chunk.metadata.get("source", ""))
        chunk.metadata["total_chunks"] = counters.get(key, 1)

    return all_chunks


# ----------------------------------------------------------------
# Public – get_chunks
# ----------------------------------------------------------------

def get_chunks(path: str = KNOWLEDGE_BASE_PATH) -> list[Document]:
    """
    Load, clean, and chunk every supported document found in *path*.

    Returns a flat list of LangChain Documents ready for embedding.

    Metadata on each chunk:
        source_path   – absolute path of the source file
        file_name     – filename with extension
        file_format   – pdf | txt | md | html
        file_size_kb  – file size in KB
        file_hash     – short SHA-256 for deduplication
        ingested_at   – ISO-8601 UTC ingestion timestamp
        chunk_index   – 0-based position within the source file
        total_chunks  – total chunks produced from the source file
        h1 / h2 / h3  – heading context (Markdown only)
        page          – page number (PDF only)
    """
    docs   = load_directory(path)
    return _split_documents(docs)
