"""Small Streamlit interface for the live demo."""

import streamlit as st

from analyzer import AI_SLOP_LABELS, VERDICT_LABELS, analyze_pr
from github_client import GitHubError


st.set_page_config(page_title="SpamShield", page_icon="🛡️")
st.title("🛡️ SpamShield")
st.caption("First-pass PR triage with a local open-weight model. Maintainers make the final decision.")
url = st.text_input("GitHub pull request URL", placeholder="https://github.com/owner/repo/pull/123")

if st.button("Analyze PR", type="primary"):
    if not url.strip():
        st.warning("Paste a GitHub pull request URL first.")
    else:
        status = st.empty()
        try:
            result = analyze_pr(url.strip(), progress=lambda message: status.info(message))
        except GitHubError as exc:
            status.error(str(exc))
        else:
            status.empty()
            st.subheader(result["pr"]["title"])
            st.metric("Verdict", VERDICT_LABELS[result["verdict"]])
            st.write(f"Confidence: {result['confidence']:.0%} · Model time: {result['model_seconds']:.1f}s")
            st.write(result["reason"])
            st.subheader("AI slop assessment")
            st.write(AI_SLOP_LABELS[result["ai_slop"]])
            st.write(result["ai_slop_reason"])
            st.caption("Assesses content quality; it does not prove whether AI wrote the PR.")
            st.subheader("Signals")
            active = [name.replace("_", " ") for name, enabled in result["signals"].items() if enabled]
            st.write(", ".join(active) if active else "No rule signals detected")
            with st.expander("PR details"):
                st.write(result["pr"]["body"] or "No description")
                for file in result["pr"]["files"]:
                    st.write(file["filename"])
