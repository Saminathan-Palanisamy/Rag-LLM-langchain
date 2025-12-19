import pinecone
from app.core.config import settings

def get_pinecone_index():
    pc = pinecone.Pinecone(api_key=settings.PINECONE_API_KEY)

    index_name = settings.PINECONE_INDEX_NAME

    
    if index_name not in pc.list_indexes().names():
        pc.create_index(
            name=index_name,
            dimension=1536,  
            metric="cosine",
            spec=pinecone.ServerlessSpec(
                cloud="aws",
                region=settings.PINECONE_ENV
            )
        )

    return pc.Index(index_name)
