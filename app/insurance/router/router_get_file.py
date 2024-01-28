from fastapi import Depends, File, UploadFile, HTTPException, applications
from app.utils import AppModel
from ..service import Service, get_service
from starlette.responses import JSONResponse
from google.cloud import storage
from . import router
import os
import uuid
import tempfile



@router.post("/get_file")
def get_file(
    iin: str,
    file: UploadFile = File(...),
    svc: Service = Depends(get_service),
):  
    print("Start get File")
    if file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Only PDF files are allowed")
    
    os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = r"app/insurance/router/google.json"
    BUCKET_NAME = os.getenv("BUCKET_NAME")
    unique_id = str(uuid.uuid4())
    file_name = f"{unique_id}_document.pdf"

    storage_client = storage.Client()
    bucket = storage_client.bucket(BUCKET_NAME)
    blob = bucket.blob(file_name)
    print("Post Google")
    with tempfile.NamedTemporaryFile(delete=False) as temp_pdf:
        temp_pdf.write(file.file.read())
        temp_pdf_name = temp_pdf.name

    try:
        blob.upload_from_filename(temp_pdf_name, content_type="application/pdf")
    finally:
        os.unlink(temp_pdf_name)

    pdf_url = blob.public_url

    response = svc.openai.readBarcodes(pdf_url, iin)

    if response == "True":
        raise HTTPException(status_code=200, detail="OK")

    raise response

