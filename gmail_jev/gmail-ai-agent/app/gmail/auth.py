import os
from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from app.config import GMAIL_CREDENTIALS_FILE, GMAIL_TOKEN_FILE, ENABLE_CLEANUP
from app.utils.logging import logger

def get_scopes():
    if ENABLE_CLEANUP:
        return ["https://www.googleapis.com/auth/gmail.modify"]
    return ["https://www.googleapis.com/auth/gmail.readonly"]

def authenticate_gmail():
    creds = None
    if os.path.exists(GMAIL_TOKEN_FILE):
        creds = Credentials.from_authorized_user_file(GMAIL_TOKEN_FILE, get_scopes())
    
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except Exception as e:
                logger.error(f"Error refreshing token: {e}. Please remove {GMAIL_TOKEN_FILE} and re-authenticate.")
                raise e
        else:
            if not os.path.exists(GMAIL_CREDENTIALS_FILE):
                raise FileNotFoundError(f"Credentials file {GMAIL_CREDENTIALS_FILE} not found. Please follow setup instructions.")
            flow = InstalledAppFlow.from_client_secrets_file(GMAIL_CREDENTIALS_FILE, get_scopes())
            creds = flow.run_local_server(port=0)
        
        with open(GMAIL_TOKEN_FILE, "w") as token:
            token.write(creds.to_json())
            
    return creds

def get_gmail_service():
    creds = authenticate_gmail()
    service = build("gmail", "v1", credentials=creds)
    return service
