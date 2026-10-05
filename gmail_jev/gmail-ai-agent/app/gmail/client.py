from app.gmail.auth import get_gmail_service
from app.gmail.parser import parse_message
from app.utils.logging import logger

def list_messages(limit=50, query="in:inbox"):
    service = get_gmail_service()
    results = service.users().messages().list(userId="me", q=query, maxResults=limit).execute()
    messages = results.get("messages", [])
    return messages

def get_message(message_id):
    service = get_gmail_service()
    msg = service.users().messages().get(userId="me", id=message_id, format="full").execute()
    return parse_message(msg)

def trash_message(message_id):
    service = get_gmail_service()
    service.users().messages().trash(userId="me", id=message_id).execute()

def modify_labels(message_id, add_labels, remove_labels):
    service = get_gmail_service()
    body = {
        "addLabelIds": add_labels,
        "removeLabelIds": remove_labels
    }
    service.users().messages().modify(userId="me", id=message_id, body=body).execute()
