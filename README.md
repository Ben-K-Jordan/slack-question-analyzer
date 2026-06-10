# Slack Question Analyzer

AI-powered tool that analyzes Slack questions, groups similar ones together, and ranks them by frequency. Supports multiple AI providers including local Ollama, Azure OpenAI, and standard OpenAI.

## Features

- **Question Extraction**: Automatically extracts questions from Slack message dumps
- **AI-Powered Grouping**: Uses embeddings to group semantically similar questions
- **Multiple AI Providers**: 
  - **Ollama** (Local, Free) - Recommended for privacy and cost
  - **Azure OpenAI** (Copilot integration)
  - **Standard OpenAI**
- **Ranked Results**: Groups questions by frequency with similarity scores
- **Keyword Extraction**: Identifies key topics in each question group
- **Date Tracking**: Shows when each question group was first and last asked
- **Persistent Embedding Cache**: Embeddings are cached on disk (`.embedding_cache/`), so re-running an analysis is near-instant and never pays for the same API call twice
- **Automatic Retries**: Transient provider/network failures are retried with exponential backoff
- **Multiple Output Formats**: Export results as JSON, CSV, or a Markdown report
- **CLI Interface**: Easy-to-use command-line tool

## Installation

### Prerequisites

- Python 3.8 or higher
- (Optional) Ollama installed locally for free embeddings

### Setup

1. Clone or download this repository

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure your AI provider:
```bash
python -m src.cli setup
```

This will guide you through setting up your preferred AI provider.

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

Analyze a file containing Slack questions:

```bash
python -m src.cli analyze example_input.txt
```

### Save Results to JSON

```bash
python -m src.cli analyze example_input.txt -o results.json
```

### Use Specific AI Provider

```bash
python -m src.cli analyze example_input.txt --provider ollama
python -m src.cli analyze example_input.txt --provider azure
python -m src.cli analyze example_input.txt --provider openai
```

### Adjust Similarity Threshold

Higher threshold = stricter grouping (0.0 to 1.0):

```bash
python -m src.cli analyze example_input.txt --threshold 0.9
```

### Choose an Output Format

The output format is inferred from the file extension:

```bash
python -m src.cli analyze example_input.txt -o results.json   # machine-readable
python -m src.cli analyze example_input.txt -o results.csv    # one row per question
python -m src.cli analyze example_input.txt -o report.md      # readable report
```

### Embedding Cache

Embeddings are cached in `.embedding_cache/` (one file per provider/model), making
repeat runs near-instant. To bypass it:

```bash
python -m src.cli analyze example_input.txt --no-cache
```

You can also set `EMBEDDING_CACHE=off` or `EMBEDDING_CACHE_DIR=/path/to/cache` in `.env`.

### Validate Input File

Check if your input file is formatted correctly:

```bash
python -m src.cli validate example_input.txt
```

## Running Tests

```bash
pip install pytest
python -m pytest tests/
```

## Input Format

The tool expects Slack content in the following format:

```
Date

Question or message text here...

-----------------------------------------------------------
Date

Another question or message...

-----------------------------------------------------------
```

See `example_input.txt` for a complete example.

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
python -m src.cli analyze example_input.txt -o results.json
```

### Example 2: Analyze with Azure OpenAI

```bash
# Set up Azure credentials
python -m src.cli setup

# Run analysis
python -m src.cli analyze example_input.txt --provider azure
```

### Example 3: Strict Grouping

```bash
# Only group very similar questions (threshold 0.95)
python -m src.cli analyze example_input.txt --threshold 0.95
```

## Troubleshooting

### Ollama Connection Error

Make sure Ollama is running:
```bash
ollama serve
```

### Model Not Found

Pull the required model:
```bash
ollama pull nomic-embed-text
```

### API Key Errors

Verify your `.env` file has the correct API keys and endpoints.

## Development

### Project Structure

```
slack-question-analyzer/
├── src/
│   ├── __init__.py
│   ├── __main__.py
│   ├── cli.py              # Command-line interface
│   ├── analyzer.py         # Main analysis orchestration
│   ├── question_extractor.py  # Question parsing logic
│   └── similarity_analyzer.py # AI embedding & grouping
├── example_input.txt       # Sample input file
├── requirements.txt        # Python dependencies
├── .env.example           # Configuration template
└── README.md
```

### Running Tests

```bash
# Validate input format
python -m src.cli validate example_input.txt

# Run analysis on example
python -m src.cli analyze example_input.txt
```

## License

MIT License

## Contributing

Contributions welcome! Please feel free to submit issues or pull requests.