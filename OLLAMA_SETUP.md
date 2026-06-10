# Ollama Setup Guide

This guide will help you set up Ollama to run the Slack Question Analyzer locally and for free.

## What is Ollama?

Ollama is a tool that lets you run AI models locally on your computer. It's:
- **Free** - No API costs
- **Private** - Your data stays on your machine
- **Fast** - No network latency
- **Easy** - Simple installation and usage

## Installation Steps

### Step 1: Install Ollama

#### Windows
1. Download Ollama from: https://ollama.ai/download
2. Run the installer
3. Ollama will start automatically

#### Mac
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

#### Linux
```bash
curl -fsSL https://ollama.ai/install.sh | sh
```

### Step 2: Verify Installation

Open a terminal/command prompt and run:
```bash
ollama --version
```

You should see the version number.

### Step 3: Pull the Embedding Model

The analyzer uses the `nomic-embed-text` model for creating embeddings:

```bash
ollama pull nomic-embed-text
```

This will download the model (about 274MB). It only needs to be done once.

### Step 4: Start Ollama (if not running)

Ollama usually starts automatically, but if needed:

```bash
ollama serve
```

Keep this terminal window open while using the analyzer.

### Step 5: Test Ollama

Test that Ollama is working:

```bash
ollama list
```

You should see `nomic-embed-text` in the list.

## Using with the Analyzer

The `.env` file is already configured for Ollama. Just run:

```bash
# Install Python dependencies first
pip install -r requirements.txt

# Run the analyzer
python -m src.cli analyze example_input.txt -o results.json
```

## Troubleshooting

### "Connection refused" error

**Problem**: Ollama is not running

**Solution**: 
```bash
ollama serve
```

### "Model not found" error

**Problem**: The embedding model isn't downloaded

**Solution**:
```bash
ollama pull nomic-embed-text
```

### Slow performance

**Problem**: First run is slower as it loads the model

**Solution**: Subsequent runs will be faster. The model stays in memory.

### Port already in use

**Problem**: Another service is using port 11434

**Solution**: Change the port in `.env`:
```env
OLLAMA_URL=http://localhost:11435
```

Then start Ollama on that port:
```bash
OLLAMA_HOST=0.0.0.0:11435 ollama serve
```

## Alternative Models

You can use different embedding models by changing the `.env` file:

```env
OLLAMA_MODEL=all-minilm
```

Available models:
- `nomic-embed-text` (recommended, 274MB)
- `all-minilm` (smaller, 45MB, less accurate)
- `mxbai-embed-large` (larger, 670MB, more accurate)

Pull any model before using:
```bash
ollama pull all-minilm
```

## Checking Ollama Status

To see if Ollama is running and what models are loaded:

```bash
# List downloaded models
ollama list

# Check running models
ollama ps
```

## Stopping Ollama

Ollama runs as a background service. To stop it:

**Windows**: Stop the Ollama service from Task Manager

**Mac/Linux**:
```bash
pkill ollama
```

## Resources

- Ollama Website: https://ollama.ai
- Ollama GitHub: https://github.com/ollama/ollama
- Model Library: https://ollama.ai/library

## Quick Reference

```bash
# Install Ollama
curl -fsSL https://ollama.ai/install.sh | sh

# Pull embedding model
ollama pull nomic-embed-text

# Start Ollama
ollama serve

# List models
ollama list

# Check status
ollama ps
```

That's it! You're ready to analyze Slack questions locally and for free.