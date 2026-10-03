"""SpamShield command line interface."""

import argparse
import sys

from analyzer import AI_SLOP_LABELS, VERDICT_LABELS, analyze_pr
from github_client import GitHubError


def main():
    parser = argparse.ArgumentParser(description="Review a GitHub pull request")
    subcommands = parser.add_subparsers(dest="command", required=True)
    check = subcommands.add_parser("check", help="Analyze a pull request")
    check.add_argument("pr_url", help="GitHub pull request URL")
    args = parser.parse_args()

    try:
        result = analyze_pr(args.pr_url, progress=print)
    except GitHubError as exc:
        print(f"Error: {exc}", file=sys.stderr)
        return 1

    print(f"Title: {result['pr']['title']}")
    print(f"Verdict: {VERDICT_LABELS[result['verdict']]} ({result['confidence']:.0%} confidence)")
    print(f"Reason: {result['reason']}")
    print(f"AI slop: {AI_SLOP_LABELS[result['ai_slop']]}")
    print(f"AI slop reason: {result['ai_slop_reason']}")
    print(f"Signals: {', '.join(name for name, active in result['signals'].items() if active) or 'none'}")
    print(f"Model time: {result['model_seconds']:.1f}s")
    return 0


if __name__ == "__main__":
    sys.exit(main())
