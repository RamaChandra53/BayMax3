# SpamShield

Local AI-assisted pull request triage for open-source maintainers. Built for the MLH × React Hyderabad Hacktoberfest Hack Day 2026.

## Problem and solution

Low-value pull requests consume maintainer time. Small changes can also be useful, so SpamShield combines simple rule signals with a local open-weight model to assess the description and actual diff.

Paste a GitHub PR URL to see a spam verdict, confidence, reason, detected signals, and a separate AI slop quality assessment. A maintainer makes the final decision.

## How it works

```text
PR URL → GitHub metadata and patches → rule signals → Ollama → validated JSON → CLI or Streamlit
```

Rules flag tiny diffs, documentation-only changes, vague descriptions, whitespace-heavy changes, and contributor-style README additions. These signals are hints for the model and do not decide the verdict themselves.

## Open-weight AI

The default model is `gemma3:4b`, running locally through Ollama. Set `OLLAMA_MODEL` to use another installed model. All model calls and response validation live in `model.py`.

The model is essential because rules alone cannot distinguish a useful one-line fix from an unnecessary edit. Local inference avoids paid API calls and makes the prompt and decision process inspectable.

## Windows setup

Install Python 3.11+ and [Ollama](https://ollama.com/download/windows), then run in PowerShell:

```powershell
py -m venv venv
.\venv\Scripts\python.exe -m pip install -r requirements.txt
ollama pull gemma3:4b
Copy-Item .env.example .env
```

Edit `.env` locally:

```dotenv
GITHUB_TOKEN=your_token_here
OLLAMA_MODEL=gemma3:4b
```

Public PRs can be fetched without a token, but GitHub applies a lower rate limit. Keep `.env` private; it is ignored by Git. Start the Ollama app before analyzing a PR.

## Run

Check that the model responds:

```powershell
.\venv\Scripts\python.exe test_model.py
```

Launch the UI:

```powershell
.\venv\Scripts\python.exe -m streamlit run app.py --server.address 127.0.0.1
```

Or use the CLI:

```powershell
.\venv\Scripts\python.exe spamshield.py check https://github.com/psf/requests/pull/7433
```

Results show **Not spam (looks genuine)**, **Likely spam**, or **Uncertain — needs human review**, plus confidence and a concise explanation. The separate AI slop assessment reports likely signs, no clear signs, or uncertainty, with a reason.

## Architecture

| File | Responsibility |
| --- | --- |
| `app.py` | Streamlit interface |
| `spamshield.py` | CLI interface |
| `github_client.py` | PR URL parsing and GitHub requests |
| `rules.py` | Deterministic signals |
| `model.py` | Ollama calls, prompt, JSON validation and retry |
| `analyzer.py` | Pipeline and display labels |

## Demo PRs

- [Requests bug fix](https://github.com/psf/requests/pull/7433)
- [Grafana grammar correction](https://github.com/grafana/grafana/pull/130818)
- [Hello-World practice PR](https://github.com/octocat/Hello-World/pull/5900)

Results can vary. For an intentional spam or AI slop example, use a clearly marked test PR in your own demo repository.

## Limitations

- A small model can be wrong; confidence is a model estimate, not a calibrated probability.
- The AI slop assessment checks quality patterns and cannot prove AI authorship.
- Model input is limited to 10 files, 500 patch lines, and 3,000 description characters. GitHub may omit patches for binary or large files.
- CPU inference can take tens of seconds.
- This MVP displays analysis. GitHub comments and labels are not implemented.
- SpamShield never closes or merges PRs.

## License

MIT. See [LICENSE](LICENSE).
