import asyncio
from app.utillities.utils import get_model,model_gemini
from langchain_core.prompts import PromptTemplate
from app.rag.get_retriever_models import final_retriever


def execute_query(f_retriever,user_query):
    docs = f_retriever.invoke(user_query)
    return docs


def _extract_text_content(content: str | list[str | dict[str, object]]) -> str:
    if isinstance(content, str):
        return content

    text_parts = []
    for block in content:
        if isinstance(block, str):
            text_parts.append(block)
        elif block.get("type") == "text":
            text = block.get("text")
            if isinstance(text, str):
                text_parts.append(text)

    if not text_parts:
        raise ValueError("The model response did not contain any text.")

    return "\n".join(text_parts)


def retireved_context(docs):
    context = ""
    sources = []

    for doc in docs:
        context += f"\n\n{doc.page_content}\n"

        m = doc.metadata

        # ── File-level fields (set by pre_processing) ──────────────────
        file_name    = m.get("file_name",    "unknown")
        file_format  = m.get("file_format",  "unknown")
        source_path  = m.get("source_path",  m.get("source", "unknown"))
        file_size_kb = m.get("file_size_kb")
        ingested_at  = m.get("ingested_at",  "unknown")

        # ── Chunk-level position ────────────────────────────────────────
        chunk_index  = m.get("chunk_index")
        total_chunks = m.get("total_chunks")

        # ── Format-specific fields (may be absent) ──────────────────────
        page         = m.get("page")          # PDF: page number
        h1           = m.get("h1")            # Markdown: H1 heading
        h2           = m.get("h2")            # Markdown: H2 heading
        h3           = m.get("h3")            # Markdown: H3 heading

        # ── Build a human-readable section label ────────────────────────
        heading_parts = [h for h in (h1, h2, h3) if h]
        section_label = " > ".join(heading_parts) if heading_parts else None
        location = (
            f"page {page}" if page is not None
            else (f"section: {section_label}" if section_label else None)
        )

        source_line = (
            f"[file: {file_name}]"
            f" | format: {file_format}"
            f" | chunk: {chunk_index}/{total_chunks}"
            + (f" | {location}" if location else "")
            + (f" | size: {file_size_kb} KB" if file_size_kb is not None else "")
            + f" | ingested: {ingested_at}"
            + f" | path: {source_path}"
        )

        sources.append(source_line)

    return context, sources


async def rag_pipeline(user_query):

    llm = model_gemini

    docs =  execute_query(final_retriever,user_query)

    context,sources = retireved_context(docs)

    rag_template = """
        You are a precise assistant answering questions from company policies.
        Use the retrieved context as your source of truth.

        The context may contain PDF tables flattened into a header line followed
        by data rows. Read the row that matches the question and use its column
        headings to interpret the values. State the matching value or values
        directly in your answer. Do not tell the user to find, inspect, or refer
        to a table, and do not answer with table headings alone. If a matching
        row is present but its column alignment is unclear, quote the row and
        explain the ambiguity instead of guessing.

        If the context fully answers the question, answer directly using only
        the context. If it only partially answers the question, state what is
        present and identify what is missing. Only provide general guidance
        when clearly labeled as outside the policy.

        Retrieved Context:
        {context}

        User Question: {question}

        Answer:"""
    
    final_template = PromptTemplate.from_template(rag_template).format(context = context,question = user_query)
    
    response = await llm.ainvoke(final_template)

    return {
        "answer": _extract_text_content(response.content),
        "context": [paragraph.strip() for paragraph in context.strip("\n\n").split("\n\n") if paragraph.strip()],
        "sources": sources
    }
