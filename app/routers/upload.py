from fastapi import APIRouter, UploadFile, File, HTTPException, status
from app.services.document_service import save_and_extract_text
from app.services.chunking_service import chunk_text
from app.services.vector_service import store_chunks
from fastapi.responses import JSONResponse
import uuid

router = APIRouter()

@router.post("/upload_file")
async def upload_file(file: UploadFile = File(...)):
    try:
        file_id = str(uuid.uuid4())        
        file_name = file.filename            
        category = "text" 

        text = save_and_extract_text(file)

        
        chunks = chunk_text(text)

        
        result = store_chunks(
            chunks,
            file_id=file_id,
            filename=file.filename,
            category="text"
        )
        return JSONResponse(
            status_code=status.HTTP_200_OK,
            content={
                "message": "File uploaded and indexed successfully",
                "file_id": file_id,
                "file_name": file_name,
                "category": category,
                "total_chunks": len(chunks),
                "pinecone": result
            }
        )

    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,detail=f"Upload failed: {str(e)}")