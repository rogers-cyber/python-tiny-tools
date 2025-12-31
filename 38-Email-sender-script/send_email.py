import os
import pandas as pd
import logging
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from tenacity import retry, stop_after_attempt, wait_fixed

# Setup logging
logging.basicConfig(
    filename='email_sender.log',
    level=logging.INFO,
    format='%(asctime)s:%(levelname)s:%(message)s'
)

SCOPES = ['https://www.googleapis.com/auth/gmail.send']

def authenticate_gmail():
    creds = None
    if os.path.exists('token.json'):
        creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.json', 'w') as token:
            token.write(creds.to_json())
    return build('gmail', 'v1', credentials=creds)

def create_message(sender, to, subject, body, cc=None, bcc=None):
    message = MIMEMultipart()
    message['to'] = to
    message['from'] = sender
    message['subject'] = subject
    if cc:
        message['cc'] = cc
    if bcc:
        message['bcc'] = bcc
    message.attach(MIMEText(body, 'plain'))
    return {'raw': base64.urlsafe_b64encode(message.as_bytes()).decode()}

@retry(stop=stop_after_attempt(3), wait=wait_fixed(5))
def send_email(service, sender, to, subject, body, cc=None, bcc=None):
    try:
        msg = create_message(sender, to, subject, body, cc, bcc)
        service.users().messages().send(userId='me', body=msg).execute()
        logging.info(f"Email sent to {to} with subject '{subject}'")
    except Exception as e:
        logging.error(f"Error sending email to {to}: {str(e)}")
        raise

def send_bulk_emails(csv_file='recipients.csv'):
    service = authenticate_gmail()
    sender = "me"
    df = pd.read_csv(csv_file)
    for index, row in df.iterrows():
        send_email(
            service,
            sender,
            row['email'],
            row['subject'],
            row['body'],
            cc=row.get('cc'),
            bcc=row.get('bcc')
        )
