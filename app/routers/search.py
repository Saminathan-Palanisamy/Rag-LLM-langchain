from fastapi import APIRouter, HTTPException, status
from fastapi.responses import StreamingResponse
from app.services.rag_service import answer_from_documents_stream

router = APIRouter()

@router.get("/search")
def search(q: str, k: int = 5):
    try:
        if not q:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Query is required"
            )

        return StreamingResponse(
            answer_from_documents_stream(q, k),
            media_type="text/event-stream"
        )
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="unable to search")
