from fileinput import filename
from app.core.pinecone_client import get_pinecone_index
from app.services.embedding_service import create_embedding
import uuid

index = get_pinecone_index()

def store_chunks(
    chunks: list[str],
    
    file_id: str,
    filename: str,
    category: str = "text"
):


    vectors = []

    for i, chunk in enumerate(chunks):
        vectors.append({
            "id": str(uuid.uuid4()),
            "values": create_embedding(chunk),
            
            "metadata": {
                
                "file_id": file_id,
                "file_name": filename,
                "category": category,
                "chunk_index": i,
                "text":chunk,
            }
        })

    index.upsert(vectors=vectors)

    return {
        "message": "Stored successfully",
        "total_chunks": len(vectors)
    }
#-----------------------------------------------------------------------------
def search_similar_chunks(query: str, top_k: int = 5):
    """
    Search similar text from Pinecone
    """
    query_vector = create_embedding(query)

    result = index.query(
        vector=query_vector,
        top_k=top_k,
        include_metadata=True
    )
    print("+++++++++++++++++++++++++++++++++++++++++")
    print("result working")
    

    matches = result.get("matches", [])
    if not matches:
        return []

    chunks = []

    for match in matches:
        metadata = match.get("metadata", {})

        chunk_data = {
            "text": metadata.get("text", ""),
            "filename": metadata.get("file_name", ""),  
            "file_id": metadata.get("file_id", match.get("id", "")), 
            "chunk_index": metadata.get("chunk_index", 0),
            "score": match.get("score", 0.0),
        }

        chunks.append(chunk_data)
        print("========================================")
        print("chunkssssssssss fetched", chunks)

    return chunks

#------------------------------------------------------------------------------

# def search_similar_chunks(query: str, top_k: int = 5):
#     """
#     Search similar text from Pinecone
#     """
#     query_vector = create_embedding(query)
#     print("++++++++++++++++++++++++++++")
#     result = index.query(
#         vector=query_vector,
#         top_k=top_k,
#         include_metadata= True
#                 )
#     print(result)
#     matches = result.get('matches', [])
    
#     if not matches:
#         return []
    
#     # Process each match
#     chunks = []

#     for match in matches:
#         metadata = match.get("metadata", {})

#         chunk_data = {
#             "text": metadata.get("text", ""),
#             "file_name": metadata.get("file_name", ""),
#             "chunk_index": metadata.get("chunk_index", 0),
#             "score": match.get("score", 0.0),
#             "id": match.get("id", "")
#         }

#         chunks.append(chunk_data)
#     print("++++++++++++++++++++++++++++++++++++")
#     print("chunkssssssssss", chunks)
#     return chunks


#------------------------------------------------------------------------------
#suma test panuradhuku run panuren
# if __name__ == "__main__":
#     upsert_text("Pinecone is a vector database")
#     upsert_text("FastAPI is a Python web framework")
#     upsert_text("Pinecone sajith kodutha task..haha!")
#     upsert_text("Unaku dhilu irundha divakar kita modhi paru")
#     upsert_text("enga periappa peru vignesh")
#     upsert_text("pinecone is Pinecone!!!")

#     results = search_text("What is Pinecone?")
#     print(results)
#python -m app.services.vector_service

#------------------------------------------------------------------------------
# index = get_pinecone_index()
# def upsert_text(text: str, namespace: str = "default"):
#     """
#     Create embedding and store in Pinecone
#     """
#     vector = create_embedding(text)

#     vector_id = str(uuid.uuid4())

#     index.upsert(
#         vectors=[
#             {
#                 "id": vector_id,
#                 "values": vector,
#                 "metadata": {
#                     "text": text
#                 }
#             }
#         ],
#         namespace=namespace
#     )

#     return {
#         "id": vector_id,
#         "message": "Text stored successfully"
#     }
#------------------------------------------------------------------------------