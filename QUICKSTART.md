# Quick Start Guide

Get up and running with the Slack Question Analyzer in 5 minutes!

## Prerequisites

- Python 3.8 or higher
- Ollama (for free local AI)

## Step-by-Step Setup

### 1. Install Ollama

**Windows**: Download from https://ollama.ai/download and run installer

**Mac/Linux**:
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### 2. Download the AI Model

```bash
ollama pull nomic-embed-text
```

This downloads the embedding model (274MB, one-time download).

### 3. Install Python Dependencies

Navigate to the project folder and run:

```bash
pip install -r requirements.txt
```

### 4. Run Your First Analysis

The project includes example Slack data. Try it out:

```bash
python -m src.cli analyze example_input.txt -o results.json
```

This will:
- Extract questions from the example file
- Group similar questions using AI
- Rank them by frequency
- Save results to `results.json`

### 5. View Results

The console will show a summary, and `results.json` contains the full analysis:

```json
{
  "total_questions": 25,
  "total_groups": 8,
  "groups": [
    {
      "representative_question": "How do I configure antivirus scanning?",
      "count": 5,
      "avg_similarity": 0.92,
      "keywords": ["antivirus", "scanning", "configure"]
    }
  ]
}
```

## Analyze Your Own Data

### Format Your Input File

Create a text file with your Slack messages in this format:

```
Date

Question or message text...

-----------------------------------------------------------
Date

Another question...

-----------------------------------------------------------
```

### Run Analysis

```bash
python -m src.cli analyze your_slack_data.txt -o your_results.json
```

## Common Commands

```bash
# Analyze with default settings
python -m src.cli analyze input.txt

# Save to specific output file
python -m src.cli analyze input.txt -o output.json

# Use stricter grouping (0.0-1.0, higher = stricter)
python -m src.cli analyze input.txt --threshold 0.9

# Validate input file format
python -m src.cli validate input.txt

# Run setup wizard
python -m src.cli setup
```

## Troubleshooting

### "Connection refused" error
Ollama isn't running. Start it:
```bash
ollama serve
```

### "Model not found" error
Download the model:
```bash
ollama pull nomic-embed-text
```

### Import errors
Install dependencies:
```bash
pip install -r requirements.txt
```

## What's Next?

- Read `OLLAMA_SETUP.md` for detailed Ollama configuration
- Read `README.md` for full documentation
- Adjust `SIMILARITY_THRESHOLD` in `.env` to tune grouping
- Try different AI providers (Azure OpenAI, standard OpenAI)

## File Structure

```
slack-question-analyzer/
├── src/                    # Source code
├── example_input.txt       # Sample data to test with
├── .env                    # Configuration (already set for Ollama)
├── requirements.txt        # Python dependencies
├── README.md              # Full documentation
├── OLLAMA_SETUP.md        # Ollama installation guide
└── QUICKSTART.md          # This file
```

## Need Help?

1. Check `OLLAMA_SETUP.md` for Ollama issues
2. Check `README.md` for detailed usage
3. Run `python -m src.cli --help` for command help

That's it! You're ready to analyze Slack questions.