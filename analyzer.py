"""Fetch, score, and analyze one pull request."""

from github_client import fetch_pr
from model import analyze_with_model
from rules import check_rules


VERDICT_LABELS = {
    "LOOKS_GENUINE": "Not spam (looks genuine)",
    "LIKELY_LOW_VALUE": "Likely spam",
    "NEEDS_REVIEW": "Uncertain — needs human review",
}
AI_SLOP_LABELS = {
    "LIKELY": "Likely AI slop",
    "NO_CLEAR_SIGNS": "No clear AI slop signs",
    "UNCERTAIN": "Uncertain",
}


def analyze_pr(url, progress=None):
    report = progress or (lambda message: None)
    report("Fetching PR...")
    pr = fetch_pr(url)
    report("Running rule checks...")
    signals = check_rules(pr)
    report("Asking local model...")
    judgment = analyze_with_model(pr, signals)
    return {"pr": pr, "signals": signals, **judgment}
