from fastapi import FastAPI
from pydantic import BaseModel, EmailStr
from email_sender import send_bulk_emails
import threading

app = FastAPI(title="Bulk Email Sender API")

class BulkEmailRequest(BaseModel):
    csv_file: str

@app.post("/send_bulk")
def send_bulk(request: BulkEmailRequest):
    # Run in background to avoid blocking
    threading.Thread(target=send_bulk_emails, args=(request.csv_file,)).start()
    return {"status": "Emails are being sent in background"}
