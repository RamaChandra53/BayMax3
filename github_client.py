"""GitHub API access for SpamShield."""

import os
import re

import requests
from dotenv import load_dotenv


API_ROOT = "https://api.github.com"
PR_URL = re.compile(r"https://github\.com/([^/]+)/([^/]+)/pull/(\d+)/?")


class GitHubError(Exception):
    """A GitHub request could not be completed."""


def parse_pr_url(url):
    match = PR_URL.fullmatch(url)
    if not match:
        raise GitHubError("Use a PR URL like https://github.com/owner/repo/pull/123")
    owner, repo, number = match.groups()
    return owner, repo, int(number)


def _get(session, path, params=None):
    try:
        response = session.get(f"{API_ROOT}{path}", params=params, timeout=20)
    except requests.RequestException as exc:
        raise GitHubError(f"Could not reach GitHub: {exc}") from exc

    if response.status_code == 404:
        raise GitHubError("PR not found, or this token cannot access its repository.")
    if response.status_code in (403, 429) and response.headers.get("X-RateLimit-Remaining") == "0":
        raise GitHubError("GitHub API rate limit reached. Set GITHUB_TOKEN in .env and retry.")
    if not response.ok:
        raise GitHubError(f"GitHub API returned HTTP {response.status_code}.")
    return response.json()


def fetch_pr(url):
    """Return PR details and every changed file, including available patches."""
    owner, repo, number = parse_pr_url(url)
    load_dotenv()
    session = requests.Session()
    session.headers.update({"Accept": "application/vnd.github+json"})
    token = os.getenv("GITHUB_TOKEN")
    if token:
        session.headers["Authorization"] = f"Bearer {token}"

    base = f"/repos/{owner}/{repo}/pulls/{number}"
    details = _get(session, base)
    files = []
    page = 1
    while True:
        batch = _get(session, f"{base}/files", {"per_page": 100, "page": page})
        files.extend(batch)
        if len(batch) < 100:
            break
        page += 1

    return {
        "title": details["title"],
        "body": details.get("body") or "",
        "author": details["user"]["login"],
        "additions": details["additions"],
        "deletions": details["deletions"],
        "changed_files": details["changed_files"],
        "files": files,
    }
