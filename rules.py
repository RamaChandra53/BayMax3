"""Conservative, explainable signals for PR triage."""

import re


TINY_DIFF_LINES = 3
VAGUE_BODIES = {"", "update", "updated file", "fixed", "changes", "minor change"}
PROFILE_LINK = re.compile(r"(?:github\.com/|@)[A-Za-z0-9-]+", re.I)
CONTRIBUTOR_WORD = re.compile(r"contributors?|authors?|participants?", re.I)


def _changed_lines(patch):
    return [line for line in patch.splitlines() if line[:1] in ("+", "-") and not line.startswith(("+++", "---"))]


def check_rules(pr):
    files = pr["files"]
    total = sum(file.get("changes", file.get("additions", 0) + file.get("deletions", 0)) for file in files)
    docs_only = bool(files) and all(
        file["filename"].lower().endswith(".md")
        or file["filename"].lower().startswith("docs/")
        or file["filename"].lower() in {"readme", "license"}
        for file in files
    )
    changed = [line[1:] for file in files for line in _changed_lines(file.get("patch") or "")]
    whitespace_heavy = len(changed) >= 2 and len({line.strip() for line in changed}) <= len(changed) // 2

    readme_only = len(files) == 1 and files[0]["filename"].lower().split("/")[-1].startswith("readme")
    patch_lines = _changed_lines(files[0].get("patch") or "") if readme_only else []
    added = [line[1:].strip() for line in patch_lines if line.startswith("+")]
    removed = [line[1:].strip() for line in patch_lines if line.startswith("-")]
    name_only = (
        readme_only
        and 0 < len(added) <= 2
        and not removed
        and all(PROFILE_LINK.search(line) or CONTRIBUTOR_WORD.search(line) for line in added)
    )
    return {
        "tiny_diff": total <= TINY_DIFF_LINES,
        "docs_only": docs_only,
        "empty_or_vague_description": pr["body"].strip().lower().rstrip(".! ") in VAGUE_BODIES,
        "whitespace_heavy": whitespace_heavy,
        "name_only_readme_change": bool(name_only),
    }
