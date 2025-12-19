from fastapi import APIRouter, HTTPException, Query, status
from app.services.vector_service import search_similar_chunks
from fastapi.responses import JSONResponse
from app.services.rag_service import answer_from_documents

router = APIRouter()


# @router.get("/Search")
# def search(q: str = Query(..., description="Search query"), top_k: int = 5):
#     try:
#         results = search_similar_chunks(q, top_k)

#         return JSONResponse(
#             status_code=status.HTTP_200_OK,
#             content={
#             "query": q,
#             "top_k": top_k,
#             "results": results
#         })

#     except Exception as e:
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Search failed: {str(e)}")
    
@router.get("/search")
def search(q: str, k: int = 5):
    if not q:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Query is required"
        )

    result = answer_from_documents(q, k)

    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=result)
    #     content={
    #     "query": q,
    #     "answer": result["answer"]
    # }

