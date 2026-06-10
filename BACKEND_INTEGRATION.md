# Backend Integration Guide

## Overview

The Slack Question Analyzer now has a complete full-stack architecture:
- **Frontend**: React UI with IBM Carbon Design System
- **Backend**: Flask REST API
- **Analysis Engine**: Python with Ollama AI embeddings

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                     React Frontend                          │
│  (Question Analyzer Design System/ui_kits/analyzer/)       │
│                                                             │
│  - Upload transcript modal                                  │
│  - Dashboard view (ranked questions)                        │
│  - Week in Review (trends & analytics)                      │
└──────────────────┬──────────────────────────────────────────┘
                   │ HTTP POST /api/analyze
                   │ (JSON: transcript content)
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                   Flask API Server                          │
│                  (api_server.py)                            │
│                                                             │
│  Endpoints:                                                 │
│  - GET  /api/health                                         │
│  - POST /api/analyze                                        │
│  - GET  /api/config                                         │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│              Python Analysis Engine                         │
│                  (src/analyzer.py)                          │
│                                                             │
│  1. Extract questions (question_extractor.py)               │
│  2. Generate embeddings (similarity_analyzer.py)            │
│  3. Group similar questions                                 │
│  4. Rank by frequency                                       │
└──────────────────┬──────────────────────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────────────────────┐
│                    Ollama AI                                │
│              (nomic-embed-text model)                       │
│                                                             │
│  Generates semantic embeddings for question similarity      │
└─────────────────────────────────────────────────────────────┘
```

## Running the Full Stack

### 1. Start Ollama (if not already running)

```bash
# Make sure Ollama is running with the nomic-embed-text model
ollama pull nomic-embed-text
ollama serve
```

### 2. Start the Flask API Server

**Option A: Using the batch file**
```bash
cd slack-question-analyzer
.\run_api_server.bat
```

**Option B: Using Python directly**
```bash
cd slack-question-analyzer
python api_server.py
```

The API server will start at `http://localhost:5000`

### 3. Open the React Frontend

Open this file in your browser:
```
slack-question-analyzer/Question Analyzer Design System/ui_kits/analyzer/index.html
```

## API Endpoints

### Health Check
```http
GET http://localhost:5000/api/health
```

Response:
```json
{
  "status": "ok",
  "message": "API server is running"
}
```

### Analyze Transcript
```http
POST http://localhost:5000/api/analyze
Content-Type: application/json

{
  "content": "Slack transcript text...",
  "provider": "ollama",
  "threshold": 0.85
}
```

Response:
```json
{
  "success": true,
  "data": {
    "total_questions": 49,
    "total_groups": 12,
    "groups": [
      {
        "representative_question": "How do I configure virus scanning?",
        "count": 4,
        "avg_similarity": 0.92,
        "keywords": ["mft", "antivirus", "quarantine"],
        "questions": [
          {
            "text": "Copy Task failing with virus scan exception",
            "date": "2026-06-05"
          }
        ]
      }
    ],
    "ungrouped_questions": [],
    "metadata": {
      "similarity_threshold": 0.85,
      "provider": "ollama"
    }
  }
}
```

### Get Configuration
```http
GET http://localhost:5000/api/config
```

Response:
```json
{
  "success": true,
  "config": {
    "provider": "ollama",
    "threshold": 0.85,
    "ollama_url": "http://localhost:11434",
    "ollama_model": "nomic-embed-text"
  }
}
```

## Frontend Integration

The React frontend automatically connects to the backend when you upload a transcript:

1. **Upload Modal** (`Modals.jsx`):
   - User drops/selects a file
   - Clicks "Analyze" button
   - Frontend reads file content
   - Sends POST request to `/api/analyze`
   - Shows progress animation
   - Displays results or error

2. **Dashboard View** (`DashboardView.jsx`):
   - Checks for `window.ANALYSIS_RESULTS`
   - If available, transforms and displays real data
   - Otherwise, shows mock data
   - Supports filtering and search

3. **Data Transformation**:
   - API returns Python format (snake_case)
   - Frontend transforms to UI format (camelCase)
   - Maintains compatibility with existing components

## Testing the Integration

### Test with Example File

1. Start the API server
2. Open the React UI in browser
3. Click "Upload transcript"
4. Select `example_input.txt` from the project root
5. Click "Analyze"
6. Wait for analysis (may take 30-60 seconds)
7. View results in dashboard

### Test with cURL

```bash
# Health check
curl http://localhost:5000/api/health

# Analyze (with file content)
curl -X POST http://localhost:5000/api/analyze \
  -H "Content-Type: application/json" \
  -d @- << 'EOF'
{
  "content": "2026-06-05 | How do I configure virus scanning in MFT?\n2026-06-05 | When a virus is detected, how can we send an email notification?"
}
EOF
```

## Configuration

Edit `.env` to change settings:

```env
AI_PROVIDER=ollama
OLLAMA_URL=http://localhost:11434
OLLAMA_MODEL=nomic-embed-text
SIMILARITY_THRESHOLD=0.85
```

## Troubleshooting

### API Server Won't Start

**Error**: `ModuleNotFoundError: No module named 'flask'`

**Solution**:
```bash
pip install flask flask-cors
```

### CORS Errors in Browser

**Error**: `Access to fetch at 'http://localhost:5000' from origin 'null' has been blocked by CORS policy`

**Solution**: The API server has CORS enabled. Make sure:
1. API server is running
2. You're accessing the HTML file via `file://` protocol (not required to serve via HTTP)

### Ollama Connection Failed

**Error**: `Connection refused to http://localhost:11434`

**Solution**:
```bash
# Start Ollama
ollama serve

# In another terminal, pull the model
ollama pull nomic-embed-text
```

### Analysis Takes Too Long

**Issue**: Analysis hangs or takes >2 minutes

**Solutions**:
1. Check Ollama is running: `curl http://localhost:11434/api/tags`
2. Reduce file size (test with smaller transcript first)
3. Check API server logs for errors
4. Increase timeout in frontend (currently no timeout set)

### Empty Results

**Issue**: Analysis completes but shows 0 questions

**Possible causes**:
1. Transcript format not recognized
2. No questions found in content
3. All questions filtered out

**Solution**: Check API response in browser DevTools Network tab

## Performance

- **Small files** (<50 questions): 10-30 seconds
- **Medium files** (50-200 questions): 30-90 seconds  
- **Large files** (>200 questions): 90-180 seconds

Performance depends on:
- Ollama response time
- Number of questions
- Similarity threshold (higher = more comparisons)

## Next Steps

1. **Add caching**: Store embeddings to avoid regeneration
2. **Add progress streaming**: Real-time progress updates via WebSocket
3. **Add batch processing**: Handle multiple files
4. **Add export**: Download results as JSON/CSV
5. **Add authentication**: Secure the API
6. **Add database**: Persist analysis history

## File Structure

```
slack-question-analyzer/
├── api_server.py                    # Flask API server
├── run_api_server.bat               # Windows launcher
├── src/
│   ├── analyzer.py                  # Main analysis orchestrator
│   ├── question_extractor.py        # Question parsing
│   └── similarity_analyzer.py       # AI embeddings & grouping
└── Question Analyzer Design System/
    └── ui_kits/analyzer/
        ├── index.html               # Main entry point
        ├── Modals.jsx               # Upload & sign-in modals
        ├── DashboardView.jsx        # Results display
        └── app-data.jsx             # Mock data (fallback)