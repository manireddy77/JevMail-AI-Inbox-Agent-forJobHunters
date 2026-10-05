import base64
from email.utils import parsedate_to_datetime

def extract_headers(payload):
    headers = {}
    for header in payload.get("headers", []):
        name = header["name"].lower()
        if name in ["from", "to", "subject", "date"]:
            headers[name] = header["value"]
    return headers

def parse_body(payload):
    body_text = ""
    if "parts" in payload:
        for part in payload["parts"]:
            mime_type = part.get("mimeType")
            if mime_type == "text/plain":
                data = part.get("body", {}).get("data", "")
                if data:
                    body_text += base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            elif mime_type == "multipart/alternative":
                body_text += parse_body(part)
    elif payload.get("mimeType") == "text/plain":
        data = payload.get("body", {}).get("data", "")
        if data:
            body_text = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
    elif payload.get("mimeType") == "text/html":
        # Fallback to HTML if no plain text
        data = payload.get("body", {}).get("data", "")
        if data:
            import re
            html = base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")
            # Minimal HTML strip
            body_text = re.sub(r'<[^>]+>', ' ', html)
            body_text = re.sub(r'\s+', ' ', body_text).strip()
    return body_text

def parse_message(msg):
    payload = msg.get("payload", {})
    headers = extract_headers(payload)
    
    body = parse_body(payload)
    if not body.strip():
        body = msg.get("snippet", "")
        
    # Limit body size to avoid huge tokens
    if len(body) > 10000:
        body = body[:10000] + "\n...[TRUNCATED]"

    return {
        "id": msg.get("id"),
        "thread_id": msg.get("threadId"),
        "sender": headers.get("from", ""),
        "recipients": headers.get("to", ""),
        "subject": headers.get("subject", ""),
        "date": headers.get("date", ""),
        "labels": msg.get("labelIds", []),
        "body_text": body,
        "snippet": msg.get("snippet", "")
    }
