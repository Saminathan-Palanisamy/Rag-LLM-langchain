import json
from collections import defaultdict
from openai import OpenAI
from app.core.config import settings
from app.services.vector_service import search_similar_chunks

client = OpenAI(api_key=settings.OPENAI_API_KEY)
DEFAULT_CHAT_MODEL = "gpt-4o-mini"

MIN_SCORE_THRESHOLD = 0.35  


STRICT_PROMPT = """
You are a retrieval-based assistant.

RULES (MANDATORY):
- Answer ONLY using the provided context.
- If the answer is NOT explicitly present in the context,
  respond with EXACTLY this sentence:
  "Information not found in the document"
- Do NOT mention context, sources, filenames, or file_ids.

Context:
{context}

Question:
{query}

Answer:
"""


def generate_rag_answer_stream(query: str, context: str):
    response = client.chat.completions.create(
        model=DEFAULT_CHAT_MODEL,
        messages=[
            {"role": "system", "content": "You are a strict retrieval assistant"},
            {
                "role": "user",
                "content": STRICT_PROMPT.format(
                    context=context,
                    query=query
                ),
            },
        ],
        temperature=0.0,
        stream=True,
    )

    buffer = ""

    for chunk in response:
        if not chunk.choices:
            continue

        delta = chunk.choices[0].delta
        if not delta or not delta.content:
            continue

        buffer += delta.content

        # sentence-wise streaming
        if buffer.strip().endswith((".", "?", "!", "\n")):
            yield f"data: {buffer.strip()}\n\n"
            buffer = ""

    if buffer.strip():
        yield f"data: {buffer.strip()}\n\n"


def answer_from_documents_stream(query: str, top_k: int = 5):
    matches = search_similar_chunks(query=query, top_k=top_k)

    if not matches:
        yield "data: Information not found in the document\n\n"
        yield "data: [DONE]\n\n"
        return

    #  Retrieval-level guard (NO hallucination)
    best_match_score = max(m["score"] for m in matches)
    if best_match_score < MIN_SCORE_THRESHOLD:
        yield "data: Information not found in the document\n\n"
        yield "data: [DONE]\n\n"
        return

    # group by file
    file_groups = defaultdict(list)
    for m in matches:
        key = (m["filename"], m["file_id"])
        file_groups[key].append(m)

    # pick best document
    best_file = None
    best_count = 0
    best_score = 0.0

    for key, chunks in file_groups.items():
        count = len(chunks)
        max_score = max(c["score"] for c in chunks)

        if count > best_count or (count == best_count and max_score > best_score):
            best_file = key
            best_count = count
            best_score = max_score

    final_chunks = file_groups[best_file]

    context = "\n\n".join(m["text"] for m in final_chunks)

    #  stream answer
    yield from generate_rag_answer_stream(query, context)

    # sources ONLY at the end
    filename, file_id = best_file
    sources_data = [
        {
            "filename": filename,
            "file_id": file_id
        }
    ]

    yield f"data: {json.dumps({'sources': sources_data})}\n\n"
    yield "data: [DONE]\n\n"
    
