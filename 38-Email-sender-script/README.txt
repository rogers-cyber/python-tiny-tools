# Bulk Email Sender with Gmail OAuth

## Features
- Send bulk emails from a CSV file
- Supports CC and BCC
- Gmail OAuth 2.0 (no passwords)
- FastAPI API endpoint
- Logging with retries

## Setup
1. Create a project in Google Cloud Console
2. Enable Gmail API and download `credentials.json`
3. Install dependencies:
    pip install -r requirements.txt
4. Prepare `recipients.csv` with columns:
    email, cc, bcc, subject, body
5. Run the FastAPI app:
    uvicorn app:app --reload

## API Endpoint
- POST /send_bulk
- Body:
    {
        "csv_file": "recipients.csv"
    }

## Logging
- Check `email_sender.log` for success/failure logs
- Automatic retries on failure (3 attempts, 5s apart)

## Notes
- First run will open browser for Gmail OAuth authentication.
