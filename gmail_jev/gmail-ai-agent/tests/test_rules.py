import pytest
from app.classifier.rules import determine_action

def test_determine_action_keep():
    # If important_probability is high, keep it
    probs = {"important_probability": 0.8}
    assert determine_action(probs) == "KEEP"
    
    # If action_required_probability is high, keep it
    probs = {"action_required_probability": 0.75}
    assert determine_action(probs) == "KEEP"

def test_determine_action_trash():
    # High ad, low important
    probs = {
        "advertisement_probability": 0.99,
        "important_probability": 0.05,
        "action_required_probability": 0.05,
        "financial_probability": 0.05
    }
    assert determine_action(probs) == "TRASH"
    
    # High spam, low important
    probs = {
        "spam_probability": 0.99,
        "important_probability": 0.01
    }
    assert determine_action(probs) == "TRASH"

def test_determine_action_review():
    # Uncertainty
    probs = {
        "important_probability": 0.5,
        "spam_probability": 0.5
    }
    assert determine_action(probs) == "REVIEW"
