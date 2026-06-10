# Slack Question Analyzer

AI-powered tool that analyzes Slack questions, groups similar ones together, and ranks them by frequency. Supports multiple AI providers including local Ollama, Azure OpenAI, and standard OpenAI.

## Features

- **Question Extraction**: Automatically extracts questions from Slack message dumps —
  plain text, Slack JSON exports, or CSV (format auto-detected), with Slack markup
  (mentions, links, emoji, code blocks) stripped automatically
- **Tiered Grouping**: Exact and near-duplicate questions are merged with cheap string
  comparison first — the AI provider is only called for genuinely distinct questions
- **AI-Powered Grouping**: Uses embeddings to group semantically similar questions
- **LLM Topic Labels** (optional): A local Ollama chat model (or OpenAI/Azure) names
  each group and writes a one-sentence summary of what people are asking
- **Multiple AI Providers**: 
  - **Ollama** (Local, Free) - Recommended for privacy and cost
  - **Azure OpenAI** (Copilot integration)
  - **Standard OpenAI**
- **Ranked Results**: Groups questions by frequency with similarity scores
- **Learns Over Time**: A persistent topic bank remembers groups across analyses —
  recurring topics keep their established names (no relabeling drift), skip redundant
  LLM calls, show a "recurring ×N" badge, and accumulate history (`GET /api/topics`;
  disable with `TOPIC_BANK=off`)
- **Keyword Extraction**: Identifies key topics in each question group
- **Date Tracking**: Shows when each question group was first and last asked
- **Persistent Embedding Cache**: Embeddings are cached on disk (`.embedding_cache/`), so re-running an analysis is near-instant and never pays for the same API call twice
- **Automatic Retries**: Transient provider/network failures are retried with exponential backoff
- **Multiple Output Formats**: Export results as JSON, CSV, or a Markdown report
- **CLI Interface**: Easy-to-use command-line tool

## Quick Start (give this to a teammate)

Clone the repo, then run the setup for your platform — it checks Python, installs
everything, downloads the AI models, and opens the dashboard:

- **Windows:** double-click **`setup.bat`** (afterwards, `start.bat` starts the app)
- **macOS / Linux:** run **`./setup.sh`** (afterwards, double-click `start.command`
  on a Mac, or run `python3 api_server.py`)

The only manual prerequisite is [Ollama](https://ollama.com/download) — if it isn't
installed, the script says so and where to get it. After setup, starting the app is
just `python api_server.py` (the browser opens automatically). If a model is missing,
the dashboard offers a **Download now** button — no terminal needed. And when something
seems off, `slack-analyzer doctor` checks the whole setup and prints exact fixes.

Prefer containers? `docker compose up -d` runs everything **including** the model
downloads — then open http://localhost:5000.

## Installation

### Prerequisites

- Python 3.10 or higher
- (Optional) Ollama installed locally for free embeddings
- (Alternative) Docker — see [Running with Docker](#running-with-docker)

### Setup

1. Clone or download this repository

2. Install the package (editable, with dev tools):
```bash
pip install -e ".[dev]"        # or: pip install -r requirements.txt (same thing)
```

This installs the `slack-analyzer` command.

3. Configure your AI provider:
```bash
slack-analyzer setup
```

This will guide you through setting up your preferred AI provider.

### Running with Docker

The compose file runs the whole stack — the analyzer (API + dashboard) and Ollama:

```bash
docker compose up -d --build
docker compose exec ollama ollama pull nomic-embed-text
docker compose exec ollama ollama pull llama3.2   # optional: enables the LLM features
```

Then open http://localhost:5000. Analyses, the embedding cache, and Ollama models
persist in named volumes. To run just the analyzer container against an Ollama on
your host, `docker build -t slack-question-analyzer . && docker run -p 5000:5000
slack-question-analyzer` (it defaults to `host.docker.internal:11434`).

### Ollama Setup (Recommended)

For free, local processing:

1. Install Ollama from https://ollama.ai
2. Pull the embedding model:
```bash
ollama pull nomic-embed-text
```
3. Run the setup wizard and choose 'ollama'

## Usage

### Basic Analysis

Analyze one or more files containing Slack questions — plain files, several at
once, or a zipped Slack export (everything merges into a single corpus):

```bash
slack-analyzer analyze example_input.txt
slack-analyzer analyze slack-export.zip -o report.md
slack-analyzer analyze week1.json week2.json -o combined.md
```

### Save Results to JSON

```bash
slack-analyzer analyze example_input.txt -o results.json
```

### Use Specific AI Provider

```bash
slack-analyzer analyze example_input.txt --provider ollama
slack-analyzer analyze example_input.txt --provider azure
slack-analyzer analyze example_input.txt --provider openai
```

### Adjust Similarity Threshold

Higher threshold = stricter grouping (0.0 to 1.0):

```bash
slack-analyzer analyze example_input.txt --threshold 0.9
```

**By default the threshold is automatic**: it starts at a model-aware value (0.75 for
Ollama — local models score paraphrases lower than OpenAI's ada-002 — 0.85 otherwise),
and if nothing groups, it relaxes itself to just below your most similar pair and says
so. Setting `--threshold`, the Settings slider, or `SIMILARITY_THRESHOLD` pins an exact
value and disables auto-adjustment. Results always include pairwise similarity stats
(`metadata.similarity_stats`) for informed tuning.

### Choose an Output Format

The output format is inferred from the file extension:

```bash
slack-analyzer analyze example_input.txt -o results.json   # machine-readable
slack-analyzer analyze example_input.txt -o results.csv    # one row per question
slack-analyzer analyze example_input.txt -o report.md      # readable report
```

### Caching

Embeddings are cached in `.embedding_cache/` and LLM outputs (topic labels,
summaries, verdicts — deterministic at temperature 0) in `.llm_cache/`, one file per
provider/model. Re-analyzing the same transcript costs zero provider calls. To bypass:

```bash
slack-analyzer analyze example_input.txt --no-cache   # embeddings only
```

Env switches: `EMBEDDING_CACHE=off`, `LLM_CACHE=off`, `EMBEDDING_CACHE_DIR`,
`LLM_CACHE_DIR`.

### Validate Input File

Check if your input file is formatted correctly:

```bash
slack-analyzer validate example_input.txt
```

## Input Formats

The input format is detected automatically:

**Plain text** with dashed separators (see `example_input.txt`):

```
Date

Question or message text here...

-----------------------------------------------------------
Date

Another question or message...

-----------------------------------------------------------
```

**Slack JSON export** — a list of message objects (or `{"messages": [...]}`); Slack
epoch timestamps (`ts`) are converted to dates automatically:

```json
[
  {"type": "message", "user": "U123", "text": "How do I reset my password?", "ts": "1704412800.000100"}
]
```

**CSV** with a `text`/`message`/`question` column and an optional `date`/`ts`/`timestamp` column:

```csv
date,message
2024-01-05,How do I reset my password?
```

## LLM Features

When a generation model is available, the pipeline uses it for five optional passes.
With Ollama:

```bash
ollama pull llama3.2
```

| Feature | What it does | Switch (in `.env`) |
|---|---|---|
| Topic labels | Names each group (2-4 words) and writes a one-sentence summary | `GROUP_LABELS` |
| Group verification | Double-checks group pairs whose similarity falls just below the threshold and merges them when they're the same topic | `LLM_VERIFY_GROUPS` |
| Question extraction | By default (`auto`), the LLM extracts and cleanly rewrites **every** question for transcripts up to 150 messages (best quality; regex fallback per batch); larger transcripts use regex plus an LLM pass for implicit help requests. `full` forces LLM-first at any size, `on` is regex-first only | `LLM_EXTRACTION` |
| Answer detection | Reads thread replies (Slack JSON exports) and decides whether each question was actually answered — feeds the "Answered" metric | `LLM_ANSWER_DETECTION` |
| Executive summary | 2-3 sentence overview of the dominant themes, shown on the dashboard and in Markdown reports | `EXECUTIVE_SUMMARY` |

Each switch accepts `auto` (default: run when the model is available), `on`, or `off`.
`GROUP_LABELS=off` (or `--no-labels` on the CLI) disables all LLM features at once.

```env
# Ollama chat model used for all LLM features (default: llama3.2)
OLLAMA_GENERATION_MODEL=llama3.2
# For openai provider: CHAT_MODEL (default gpt-4o-mini)
# For azure provider: AZURE_OPENAI_CHAT_DEPLOYMENT (LLM features off unless set)

# Borderline verification window and call cap
LLM_VERIFY_MARGIN=0.03
LLM_VERIFY_MAX=10
```

Prompting details: all calls use chat endpoints with JSON-schema-enforced output,
temperature 0, a fixed seed, and `keep_alive` so Ollama keeps the model loaded across
calls. Labeling prompts include few-shot examples, the group's keywords, and a diverse
sample of phrasings; outputs are validated (generic topics like "General Questions" are
rejected) with one corrective retry. Everything degrades gracefully — without a
generation model, groups fall back to keyword-based topics and the analysis still works.

## Output Format

The tool generates a JSON file with the following structure:

```json
{
  "total_questions": 25,
  "total_groups": 8,
  "groups": [
    {
      "representative_question": "How do I configure antivirus scanning?",
      "questions": [...],
      "count": 5,
      "avg_similarity": 0.92,
      "keywords": ["antivirus", "scanning", "configure", "virus", "email"]
    }
  ],
  "ungrouped_questions": [...],
  "metadata": {
    "analyzed_at": "2026-06-09T20:00:00Z",
    "similarity_threshold": 0.85,
    "model": "nomic-embed-text",
    "provider": "ollama"
  }
}
```

## Configuration

Create a `.env` file (or use the setup wizard):

```env
# AI Provider: 'ollama', 'azure', or 'openai'
AI_PROVIDER=ollama

# Ollama Configuration (Local & Free)
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=nomic-embed-text

# Azure OpenAI Configuration
# AZURE_OPENAI_API_KEY=your_key
# AZURE_OPENAI_ENDPOINT=https://your-resource.openai.azure.com/
# AZURE_OPENAI_DEPLOYMENT_NAME=your-deployment
# AZURE_OPENAI_API_VERSION=2024-02-15-preview

# Standard OpenAI Configuration
# OPENAI_API_KEY=your_key

# Analysis Settings
SIMILARITY_THRESHOLD=0.85
```

## How It Works

1. **Question Extraction**: Parses Slack content and identifies questions using pattern matching
2. **Normalization**: Cleans and normalizes questions for better comparison
3. **Embedding Generation**: Converts questions to vector embeddings using AI
4. **Similarity Calculation**: Computes cosine similarity between all question pairs
5. **Grouping**: Clusters similar questions based on similarity threshold
6. **Ranking**: Sorts groups by frequency and extracts keywords

## Examples

### Example 1: Analyze with Ollama (Free)

```bash
# Make sure Ollama is running
ollama serve

# Run analysis
slack-analyzer analyze example_input.txt -o results.json
```

### Example 2: Analyze with Azure OpenAI

```bash
# Set up Azure credentials
slack-analyzer setup

# Run analysis
slack-analyzer analyze example_input.txt --provider azure
```

### Example 3: Strict Grouping

```bash
# Only group very similar questions (threshold 0.95)
slack-analyzer analyze example_input.txt --threshold 0.95
```

## Web Dashboard

A React dashboard (in `Question Analyzer Design System/ui_kits/analyzer/`) provides a visual
front end on top of the same analysis engine. The Flask server serves both the API **and**
the dashboard, so the whole app runs with one command.

### Running the Full Stack

1. **Start Ollama** (if not already running):
   ```bash
   ollama serve
   ```
2. **Start the server** (`run_api_server.bat` on Windows, or):
   ```bash
   python api_server.py
   ```
3. **Open the dashboard**: http://localhost:5000

Upload a transcript via the upload modal. The progress bar reflects real backend progress
(per-embedding), and completed analyses are saved to `analyses/` — the dashboard
automatically reloads your most recent analysis after a page refresh.

Dashboard features:
- **Export buttons**: download the displayed analysis as a Markdown report or CSV
- **History** (clock icon): browse, reload, or delete any past analysis
- **Settings** (gear icon): choose the AI provider and similarity threshold used for
  new analyses (persisted in the browser)
- **Week in Review**: real weekly trends computed from your latest analysis — volume
  vs last week, 6-week trend, and per-topic rank movement (weeks are anchored to the
  most recent question date in the transcript, so historical exports work too)
- Until your first analysis, both views show demo data clearly labeled "sample data"

Analyses are queued one at a time by default so a local Ollama isn't overloaded
(`MAX_CONCURRENT_JOBS` to change), can be **cancelled** mid-run from the upload modal,
and **survive server restarts**: jobs are persisted under `jobs/` and anything that was
queued or running when the server stopped is automatically re-queued on startup.
Other server settings: `API_HOST` (default `127.0.0.1`), `API_PORT` (default `5000`),
`FLASK_DEBUG`, `MAX_CONTENT_MB` (default `50`), `ANALYSES_DIR` (default `analyses/`),
`JOBS_DIR` (default `jobs/`).

Uploads accept `.json`, `.txt`, `.csv` — or a **zipped Slack export**: every
`.json`/`.txt`/`.csv` file inside the zip (e.g. one JSON file per day) is merged and
analyzed as a single corpus.

Very large transcripts are handled too: above `LARGE_CLUSTERING_THRESHOLD` (default
2000) distinct questions, grouping switches to memory-safe leader clustering instead
of a full n×n similarity matrix, and the dashboard paginates long topic lists.

> **Security note:** the server has no authentication and CORS is open — it is meant
> to run on your own machine. Don't set `API_HOST=0.0.0.0` on a shared network.

### API Endpoints

| Endpoint | Method | Description |
|---|---|---|
| `/api/health` | GET | Health check — verifies Ollama/keys for the configured provider (or `?provider=...`) |
| `/api/analyze` | POST | Start an analysis job. JSON body `{"content": "...", "provider": "ollama", "threshold": 0.85}` or multipart `files=` upload (`.json`/`.txt`/`.csv`/`.zip`). Returns `202` with `{"job_id": "..."}` |
| `/api/jobs/<job_id>` | GET | Job status (`queued`/`running`/`done`/`error`/`cancelled`) and progress; includes the full result when done |
| `/api/jobs/<job_id>/cancel` | POST | Cancel a queued or running job |
| `/api/analyses` | GET | List of saved past analyses (newest first) |
| `/api/analyses/latest` | GET | Full results of the most recent analysis |
| `/api/analyses/<id>` | GET | Full results of a specific analysis |
| `/api/analyses/<id>` | DELETE | Delete a saved analysis |
| `/api/analyses/<id>/export` | GET | Download as `?format=md`, `csv`, or `json` |
| `/api/analyses/latest/weekly` | GET | Week-in-Review stats for the most recent analysis |
| `/api/analyses/<id>/weekly` | GET | Week-in-Review stats for a specific analysis |
| `/api/topics` | GET | The learned topic bank (topics accumulated across analyses) |
| `/api/models/pull` | POST | Download a missing Ollama model (`{"model": "..."}`); progress at `GET /api/models/pull/<model>` |
| `/api/config` | GET | Current provider/threshold configuration |

A finished job's `data` field contains the same JSON structure shown in
[Output Format](#output-format).

Example:
```bash
# Start a job
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d '{"content": "2026-06-05\nHow do I configure virus scanning?"}'
# -> {"success": true, "job_id": "abc123..."}

# Poll for progress / result
curl http://localhost:5000/api/jobs/abc123...
# -> {"status": "running", "progress": {"stage": "embedding", "completed": 12, "total": 49}}
```

## Troubleshooting

### Ollama Connection Error ("connection refused")

Make sure Ollama is running:
```bash
ollama serve
```

### Model Not Found

Pull the required model (about 274MB, one time only):
```bash
ollama pull nomic-embed-text
```

### Port 11434 Already in Use

Run Ollama on another port and update `.env` to match:
```bash
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```
```env
OLLAMA_URL=http://localhost:11435
```

### Alternative Ollama Models

Set `OLLAMA_MODEL` in `.env` (and `ollama pull` it first):
- `nomic-embed-text` — recommended (274MB)
- `all-minilm` — smaller and faster (45MB), less accurate
- `mxbai-embed-large` — larger (670MB), more accurate

### Import Errors

```bash
pip install -r requirements.txt
```

### API Key Errors

Verify your `.env` file has the correct API keys and endpoints.

## Development

### Project Structure

```
slack-question-analyzer/
├── slack_question_analyzer/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py              # Command-line interface (the slack-analyzer command)
│   ├── analyzer.py         # Main analysis orchestration
│   ├── question_extractor.py  # Multi-format parsing & question detection
│   ├── similarity_analyzer.py # Embeddings, dedupe tiers & grouping
│   ├── group_labeler.py    # LLM prompting layer
│   ├── weekly_stats.py     # Week-in-Review computation
│   └── exporters.py        # CSV / Markdown export
├── tests/                  # pytest suite
├── api_server.py           # Flask API + dashboard server
├── run_api_server.bat      # Windows launcher for the API server
├── Question Analyzer Design System/  # React dashboard + design system
├── pyproject.toml          # Package metadata & dependencies
├── Dockerfile / docker-compose.yml   # Container setup
├── example_input.txt       # Sample input file
├── .env.example            # Configuration template
└── README.md
```

### Running Tests

```bash
# Run the test suite (no Ollama required — embeddings are mocked)
python -m pytest tests/

# Manual smoke test
slack-analyzer validate example_input.txt
slack-analyzer analyze example_input.txt
```

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.