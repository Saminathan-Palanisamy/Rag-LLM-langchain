import os, uuid
import pdfplumber
import docx
from fastapi import UploadFile, HTTPException, status


UPLOAD_DIR = "uploads/documents"


def save_and_extract_text(file: UploadFile) -> str:
    """
    Save uploaded file and extract text from txt / pdf / docx
    """
    os.makedirs(UPLOAD_DIR, exist_ok=True)

    filename = f"{uuid.uuid4().hex}_{file.filename}"
    path = os.path.join(UPLOAD_DIR, filename)

    # Save file
    with open(path, "wb") as f:
        f.write(file.file.read())

    name = file.filename.lower()
    content = ""

    if name.endswith(".txt"):
        with open(path, "r", encoding="utf-8", errors="ignore") as fh:
            content = fh.read()

    elif name.endswith(".pdf"):
        with pdfplumber.open(path) as pdf:
            pages = [p.extract_text() or "" for p in pdf.pages]
            content = "\n".join(pages)

    elif name.endswith(".docx"):
        doc = docx.Document(path)
        content = "\n".join([p.text for p in doc.paragraphs])

    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Unsupported file type"
        )

    if not content.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No text could be extracted from document"
        )

    return content
