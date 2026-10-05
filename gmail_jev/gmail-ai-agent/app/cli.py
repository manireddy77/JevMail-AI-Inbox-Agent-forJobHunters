import argparse
import sys
import os
from app.gmail.auth import authenticate_gmail
from app.utils.logging import logger
from app.main import process_emails, get_provider
from app.config import DRY_RUN, ENABLE_CLEANUP

def test_gmail():
    try:
        authenticate_gmail()
        from app.gmail.client import list_messages
        messages = list_messages(limit=1)
        print("✓ Gmail authentication successful")
        print("✓ Gmail API accessible")
        print(f"✓ Found {len(messages)} recent messages")
    except Exception as e:
        print(f"✗ Gmail test failed: {e}")

def test_jev():
    import logging
    # Enable DEBUG for this test so we see the raw API response
    logging.getLogger("gmail-ai").setLevel(logging.DEBUG)
    try:
        provider = get_provider()
        from app.classifier.questions import get_questions_schema
        questions = get_questions_schema()
        
        # Tiny test classification
        state = "Sender: example@example.com\nSubject: Buy viagra now\n\nBody: Discount pills."
        
        print(f"Testing {provider.provider_name} model {provider.model_name}...")
        res = provider.classify(state, questions)
        
        print("✓ Provider configuration loaded")
        print("✓ API connection successful")
        print(f"✓ Classification probabilities: {res}")
    except Exception as e:
        print(f"✗ Jev test failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="Gmail AI Agent (Jev)")
    subparsers = parser.add_subparsers(dest="command")

    # auth
    parser_auth = subparsers.add_parser("auth", help="Authenticate with Gmail")
    
    # test-gmail
    parser_test_gmail = subparsers.add_parser("test-gmail", help="Test Gmail connection")
    
    # test-jev
    parser_test_jev = subparsers.add_parser("test-jev", help="Test Jev API connection")
    
    # run
    parser_run = subparsers.add_parser("run", help="Run the agent")
    parser_run.add_argument("--dry-run", action="store_true", help="Force dry-run mode")
    parser_run.add_argument("--limit", type=int, default=50, help="Max emails to process")
    parser_run.add_argument("--reprocess", action="store_true", help="Process already processed emails")
    parser_run.add_argument("--skip-insights", action="store_true", help="Skip local Ollama insights for faster processing")
    
    # ui
    parser_ui = subparsers.add_parser("ui", help="Start the web dashboard")
    parser_ui.add_argument("--port", type=int, default=5050, help="Port to run the UI on (default: 5050)")
    
    args = parser.parse_args()

    if args.command == "auth":
        try:
            authenticate_gmail()
            print("Authentication successful.")
        except Exception as e:
            print(f"Authentication failed: {e}")
            
    elif args.command == "test-gmail":
        test_gmail()
        
    elif args.command == "test-jev":
        test_jev()
        
    elif args.command == "run":
        if args.dry_run:
            os.environ["DRY_RUN"] = "true"
            logger.info("Forced DRY_RUN via CLI")
            
        process_emails(limit=args.limit, reprocess=args.reprocess, skip_insights=args.skip_insights)
        
    elif args.command == "ui":
        from app.ui.server import run_ui
        run_ui(port=args.port)
        
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
