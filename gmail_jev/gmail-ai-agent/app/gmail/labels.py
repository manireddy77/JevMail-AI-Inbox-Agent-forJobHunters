from app.gmail.auth import get_gmail_service
from app.utils.logging import logger

REQUIRED_LABELS = [
    "AI/Important",
    "AI/ActionRequired",
    "AI/Review",
    "AI/Processed"
]

def ensure_labels_exist():
    service = get_gmail_service()
    results = service.users().labels().list(userId="me").execute()
    existing_labels = {label["name"]: label["id"] for label in results.get("labels", [])}
    
    label_map = {}
    for req_label in REQUIRED_LABELS:
        if req_label in existing_labels:
            label_map[req_label] = existing_labels[req_label]
        else:
            logger.info(f"Creating label: {req_label}")
            label = {
                "name": req_label,
                "labelListVisibility": "labelShow",
                "messageListVisibility": "show"
            }
            try:
                created = service.users().labels().create(userId="me", body=label).execute()
                label_map[req_label] = created["id"]
            except Exception as e:
                logger.error(f"Failed to create label {req_label}: {e}")
    return label_map
