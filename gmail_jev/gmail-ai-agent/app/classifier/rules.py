"""
Deterministic rules that convert Jev probabilities into a final category.
"""

def determine_category(probs: dict) -> str:
    p = {k: probs.get(k, 0.0) for k in [
        "needs_response_probability",
        "is_shortlisted_probability",
        "is_acknowledgement_probability",
        "is_platform_notification_probability",
        "is_rejection_probability",
        "has_important_info_probability",
        "is_financial_probability",
        "is_spam_or_promo_probability",
        "is_verification_code_probability"
    ]}

    needs_reply    = p["needs_response_probability"]
    shortlisted    = p["is_shortlisted_probability"]
    ack            = p["is_acknowledgement_probability"]
    platform_notif = p["is_platform_notification_probability"]
    rejection      = p["is_rejection_probability"]
    has_info       = p["has_important_info_probability"]
    financial      = p["is_financial_probability"]
    promo          = p["is_spam_or_promo_probability"]
    verification   = p["is_verification_code_probability"]

    # ── SILENT SKIPS (Highest priority so they don't leak into info/needs reply) ──

    # 1. Verification codes / OTPs
    if verification >= 0.80:
        return "SKIP_ACK"

    # 2. Marketing / promotions / bootcamps
    if promo >= 0.70 and shortlisted < 0.40:
        return "SKIP_PROMO"

    # 3. LinkedIn/Indeed/Naukri automated notifications (even if they ask to "connect" or "respond")
    if platform_notif >= 0.75 and shortlisted < 0.40:
        return "SKIP_PLATFORM"

    # 4. Auto-acknowledgement: "We received your application" or "Confirm subscription"
    if ack >= 0.75 and shortlisted < 0.40:
        return "SKIP_ACK"

    # ── PRIORITY CATEGORIES ────────────────────────

    # Genuine financial transactions (not promos)
    if financial >= 0.80 and promo < 0.50:
        return "FINANCIAL"

    # Needs a reply from the user
    if needs_reply >= 0.65:
        return "NEEDS_RESPONSE"

    # Shortlisted / interview invite
    if shortlisted >= 0.60:
        return "SHORTLISTED"

    # Rejection
    if rejection >= 0.75 and needs_reply < 0.40:
        return "REJECTION"

    # Contains useful info
    if has_info >= 0.70 and needs_reply < 0.40 and shortlisted < 0.40:
        return "HAS_INFO"

    # ── DEFAULT: uncertain, keep for review ────────
    return "REVIEW"


CATEGORY_LABEL_MAP = {
    "NEEDS_RESPONSE": "AI/ActionRequired",
    "SHORTLISTED":    "AI/Important",
    "FINANCIAL":      "AI/Important",
    "HAS_INFO":       "AI/Important",
    "REJECTION":      "AI/Processed",
    "REVIEW":         "AI/Review",
    "SKIP_ACK":       "AI/Processed",
    "SKIP_PLATFORM":  "AI/Processed",
    "SKIP_PROMO":     "AI/Processed",
}

TRASH_CATEGORIES = {"SKIP_PROMO", "SKIP_ACK", "SKIP_PLATFORM"}
