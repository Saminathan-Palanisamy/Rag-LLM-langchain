
from openai import OpenAI
from app.core.config import settings
from app.services.vector_service import search_similar_chunks
from collections import defaultdict

client = OpenAI(api_key=settings.OPENAI_API_KEY)
DEFAULT_CHAT_MODEL = "gpt-4o-mini"


def generate_rag_answer(query: str, context: str) -> str:
    prompt = f"""
You are an assistant answering ONLY from the provided context.

Rules:

- Use ONLY the given context.
- If the answer is not found, say: "Information not found in the document".
- DO NOT mention sources, filenames, or file_ids in the answer.

Context:
{context}

Question:
{query}


Answer clearly and concisely.
"""

    resp = client.chat.completions.create(
        model=DEFAULT_CHAT_MODEL,
        messages=[
            {"role": "system", "content": "You are a helpful document assistant"},
            {"role": "user", "content": prompt},
        ],
        temperature=0.2,
    )

    return resp.choices[0].message.content.strip()

 

#------------------------------------------------------------------------------------------------
def answer_from_documents(query: str, top_k: int = 5):
    matches = search_similar_chunks(query=query, top_k=top_k)

    if not matches:
        return {
            "query": query,
            "answer": "No relevant information found",
            "sources": []
        }


    file_groups = defaultdict(list)
    print("length of file groups: " ,len(file_groups))

    for m in matches:
        key = (m["filename"], m["file_id"])
        file_groups[key].append(m)

    best_file = None
    best_count = 0
    best_score = 0.0

    for key, chunks in file_groups.items():
        chunk_count = len(chunks)
        max_score = max(c["score"] for c in chunks)

        if (
            chunk_count > best_count or
            (chunk_count == best_count and max_score > best_score)
        ):
            best_file = key
            best_count = chunk_count
            best_score = max_score
            print("best_file: ",best_file)
            print("best_count: ",best_count)
            print("best_score: ",best_score)

    final_chunks = file_groups[best_file]
    print("length of final chunks", len(final_chunks))
    print("++++++++++++++++++++++++++++++")
    print("finalllllllllllllll chunkkkkkkkkkssssss", final_chunks)

    context = "\n\n".join(
        [
            f"""
        Source:
        - filename: {m['filename']}
        - file_id: {m['file_id']}

        Content:
        {m['text']}
        """
            for m in final_chunks
        ]
    )
    print("+++++++++++++++++++")
    print("contextsssssssssssssssssssssssssssss",context)

    answer = generate_rag_answer(query, context)

    filename, file_id = best_file
    print("+++++++++++++++++++")
    print("Answer:", answer)
    print("---------------------------------")
    print("From the file name:" , filename)

    return {
        "query": query,
        "answer": answer,
        "sources": [
            {
                "filename": filename,
                "file_id": file_id
            }
        ]
    }

#------------------------------------------------------------------------------------------------

