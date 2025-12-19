from fastapi import FastAPI, status
from app.routers import upload, search

from fastapi.responses import JSONResponse




app = FastAPI(title="Chatbot_Pinecone")

app.include_router(upload.router, prefix="/upload", tags=["Upload"])
app.include_router(search.router, prefix="/search", tags=["Search"])


@app.get("/")
def root():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"message": "Chatbot"
    "pesi parunga, sandhosama ponga!"}
    )
