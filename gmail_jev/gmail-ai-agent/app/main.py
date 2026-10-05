import os
import time
from datetime import datetime
from app.config import DRY_RUN, ENABLE_CLEANUP, MAX_EMAILS_PER_RUN, JEV_PROVIDER
from app.utils.logging import logger
from app.database.db import init_db, is_processed, save_email_processing, get_stats
from app.gmail.client import list_messages, get_message, trash_message, modify_labels
from app.gmail.labels import ensure_labels_exist
from app.classifier.questions import get_questions_schema, format_state
from app.classifier.rules import determine_category, TRASH_CATEGORIES, CATEGORY_LABEL_MAP
from app.summary.ollama import generate_insight, is_ollama_running


def get_provider():
    if JEV_PROVIDER == "typesafe":
        from app.jev.typesafe import TypeSafeJevProvider
        return TypeSafeJevProvider()
    elif JEV_PROVIDER == "openrouter":
        from app.jev.openrouter import OpenRouterJevProvider
        return OpenRouterJevProvider()
    else:
        raise ValueError(f"Unknown JEV_PROVIDER: {JEV_PROVIDER}")


def process_emails(limit=MAX_EMAILS_PER_RUN, reprocess=False, skip_insights=False):
    logger.info(f"Starting run. DRY_RUN={DRY_RUN}, ENABLE_CLEANUP={ENABLE_CLEANUP}")

    init_db()

    # Check Ollama availability up front
    ollama_ok = False
    if not skip_insights:
        ollama_ok = is_ollama_running()
        if ollama_ok:
            logger.info("Ollama is running — local AI insights enabled.")
        else:
            logger.warning("Ollama not running — insights will be skipped. Start Ollama to enable them.")
    else:
        logger.info("Insights skipped via --skip-insights flag.")

    # Labels only needed with modify scope
    labels = {}
    if not DRY_RUN and ENABLE_CLEANUP:
        try:
            labels = ensure_labels_exist()
        except Exception as e:
            logger.error(f"Failed to create labels: {e}")
    else:
        logger.info("DRY_RUN mode — skipping label creation (requires gmail.modify scope)")

    provider = get_provider()
    questions = get_questions_schema()

    logger.info(
        f"Provider: {provider.provider_name}  Model: {provider.model_name}  "
        f"Ollama: {'ON' if ollama_ok else 'OFF'}"
    )

    messages = list_messages(limit=limit)
    logger.info(f"Fetched {len(messages)} messages from inbox.")

    counts = {
        "NEEDS_RESPONSE": 0, "SHORTLISTED": 0, "REJECTION": 0,
        "FINANCIAL": 0, "HAS_INFO": 0, "REVIEW": 0,
        "SKIP_ACK": 0, "SKIP_PLATFORM": 0, "SKIP_PROMO": 0,
    }

    for msg_meta in messages:
        total_msg_start = time.time()
        msg_id = msg_meta["id"]

        if not reprocess and is_processed(msg_id):
            logger.debug(f"Already processed {msg_id}, skipping.")
            continue

        try:
            email_data = get_message(msg_id)
        except Exception as e:
            logger.error(f"Could not fetch message {msg_id}: {e}")
            continue

        subject = email_data.get("subject", "(no subject)")
        sender  = email_data.get("sender", "")

        safe_subject = subject.encode("ascii", "replace").decode("ascii")
        logger.info(f"Classifying: {safe_subject[:60]}  |  {sender[:40]}")

        # ── Jev classification ──
        t0 = time.time()
        state_str = format_state(email_data)
        try:
            probabilities = provider.classify(state_str, questions)
        except Exception as e:
            logger.error(f"Classification error for {msg_id}: {e}")
            probabilities = {}
        jev_time = time.time() - t0

        category = determine_category(probabilities)
        counts[category] = counts.get(category, 0) + 1

        # ── Local LLM insight ──
        t1 = time.time()
        insight = ""
        if ollama_ok and category not in {"SKIP_ACK", "SKIP_PLATFORM", "SKIP_PROMO"}:
            insight = generate_insight(
                subject=subject,
                sender=sender,
                body=email_data.get("body_text", email_data.get("snippet", ""))
            )
        ollama_time = time.time() - t1

        total_time = time.time() - total_msg_start
        logger.info(f"→ {category} [{total_time:.1f}s total | Jev: {jev_time:.1f}s | Ollama: {ollama_time:.1f}s]  |  {insight[:60] if insight else 'no insight'}")

        if DRY_RUN:
            _print_dry_run(email_data, probabilities, category, insight)
            action_taken = "DRY_RUN"
        else:
            action_taken = _apply_action(msg_id, category, labels)

        save_email_processing(
            message_id=msg_id,
            thread_id=email_data.get("thread_id", ""),
            sender=sender,
            subject=subject,
            received_at=email_data.get("date", ""),
            body_snippet=email_data.get("snippet", ""),
            probabilities=probabilities,
            category=category,
            action_taken=action_taken,
            insight=insight,
            model=provider.model_name,
            provider=provider.provider_name,
        )

    _print_run_summary(counts, DRY_RUN)


def _apply_action(msg_id: str, category: str, labels: dict) -> str:
    try:
        if category in TRASH_CATEGORIES and ENABLE_CLEANUP:
            trash_message(msg_id)
            return "TRASHED"
        label_name = CATEGORY_LABEL_MAP.get(category)
        if label_name and label_name in labels:
            modify_labels(msg_id, [labels[label_name]], [])
            return f"LABELED:{label_name}"
    except Exception as e:
        logger.error(f"Action failed for {msg_id}: {e}")
        return "ERROR"
    return "NONE"


def _print_dry_run(email_data, probabilities, category, insight):
    sep = "─" * 60
    print(f"\n[DRY RUN] {sep}")
    print(f"  From   : {email_data.get('sender', '')}")
    print(f"  Subject: {email_data.get('subject', '')}")
    print(f"\n  Scores:")
    for k, v in sorted(probabilities.items()):
        bar_len = int(float(v) * 20)
        bar = "█" * bar_len + "░" * (20 - bar_len)
        print(f"    {k:<35} {bar}  {float(v):.2f}")
    print(f"\n  Category: {category}")
    if insight:
        print(f"  Insight : {insight}")
    print()


def _print_run_summary(counts, dry_run):
    total = sum(counts.values())
    mode = "DRY RUN" if dry_run else "LIVE"
    print(f"\n{'='*60}")
    print(f"  {mode} COMPLETE   Processed: {total}")
    print(f"{'='*60}")
    print(f"  📬 Needs Response : {counts.get('NEEDS_RESPONSE', 0)}")
    print(f"  🎉 Shortlisted    : {counts.get('SHORTLISTED', 0)}")
    print(f"  ❌ Rejection      : {counts.get('REJECTION', 0)}")
    print(f"  💰 Financial      : {counts.get('FINANCIAL', 0)}")
    print(f"  ℹ️  Has Info       : {counts.get('HAS_INFO', 0)}")
    print(f"  👁  Review         : {counts.get('REVIEW', 0)}")
    print(f"  ⏭  Skipped (Ack)  : {counts.get('SKIP_ACK', 0)}")
    print(f"  ⏭  Skipped (Plat) : {counts.get('SKIP_PLATFORM', 0)}")
    print(f"  ⏭  Skipped (Promo): {counts.get('SKIP_PROMO', 0)}")
    print(f"{'='*60}")
    if dry_run:
        print("  NO GMAIL CHANGES WERE MADE.")
    print()
