# Testing & Validation Guide

This guide helps you verify the Slack Question Analyzer works correctly.

## Prerequisites Check

Before testing, ensure you have:

1. **Python 3.8+** installed
   ```bash
   python --version
   # Should show: Python 3.8.x or higher
   ```

2. **Dependencies installed**
   ```bash
   pip install -r requirements.txt
   ```

3. **Ollama running** (if using Ollama)
   ```bash
   ollama serve
   ollama pull nomic-embed-text
   ```

## Step 1: Syntax Validation

Test that all Python files have valid syntax:

```bash
python test_syntax.py
```

**Expected Output:**
```
============================================================
SYNTAX VALIDATION TEST
============================================================
✓ src/__init__.py - Syntax OK
✓ src/__main__.py - Syntax OK
✓ src/question_extractor.py - Syntax OK
✓ src/similarity_analyzer.py - Syntax OK
✓ src/analyzer.py - Syntax OK
✓ src/cli.py - Syntax OK

============================================================
✓ ALL FILES PASSED SYNTAX CHECK
============================================================
```

## Step 2: Import Test

Test that all modules can be imported:

```bash
python -c "from src.question_extractor import QuestionExtractor; print('✓ QuestionExtractor imports OK')"
python -c "from src.similarity_analyzer import SimilarityAnalyzer; print('✓ SimilarityAnalyzer imports OK')"
python -c "from src.analyzer import QuestionAnalyzer; print('✓ QuestionAnalyzer imports OK')"
```

## Step 3: CLI Help Test

Verify the CLI works:

```bash
python -m src.cli --help
```

**Expected Output:**
```
Usage: cli [OPTIONS] COMMAND [ARGS]...

  Slack Question Analyzer - AI-powered question grouping and ranking.
  ...

Commands:
  analyze   Analyze questions from a Slack content file.
  setup     Setup wizard to configure the analyzer.
  validate  Validate input file format and show statistics.
```

## Step 4: Validate Example Input

Test the question extractor on the example file:

```bash
python -m src.cli validate example_input.txt
```

**Expected Output:**
```
Validating: example_input.txt

File is valid!

Statistics:
  Total questions found: 25

Sample questions:
  1. Can I check if the WebMethods Metering Agent comes pre-installed with WebMet...
  2. Anyone here have some good examples on using the IWHI e2e monitoring for mon...
  ...
```

## Step 5: Full Analysis Test (Requires Ollama)

Run a complete analysis:

```bash
python -m src.cli analyze example_input.txt -o test_results.json
```

**Expected Output:**
```
Initializing analyzer with provider: from .env (default: ollama)

Analyzing: example_input.txt
Step 1: Extracting questions from Slack content...
Found 25 questions

Step 2: Grouping similar questions using AI...
Analyzing 25 questions...
Created 15 question groups

Step 3: Extracting keywords from groups...

============================================================
QUESTION ANALYSIS SUMMARY
============================================================

Total Questions Analyzed: 25
Question Groups Found: 8
Ungrouped Questions: 7
...

Analysis complete! Results saved to: test_results.json
```

## Step 6: Verify Output

Check that the JSON output is valid:

```bash
python -c "import json; data=json.load(open('test_results.json')); print(f'✓ Valid JSON with {data[\"total_questions\"]} questions')"
```

## Common Issues & Solutions

### Issue: "Module not found" errors

**Solution:** Install dependencies
```bash
pip install -r requirements.txt
```

### Issue: "Connection refused" (Ollama)

**Solution:** Start Ollama
```bash
ollama serve
```

### Issue: "Model not found" (Ollama)

**Solution:** Pull the model
```bash
ollama pull nomic-embed-text
```

### Issue: Syntax errors

**Solution:** Check you're using Python 3.8+
```bash
python --version
```

## Manual Code Review Checklist

- [ ] All Python files have no syntax errors
- [ ] All imports resolve correctly
- [ ] CLI commands work (--help, validate, analyze)
- [ ] Question extraction works on example file
- [ ] Full analysis completes without errors
- [ ] Output JSON is valid and contains expected fields
- [ ] No "Made with Bob" comments in code
- [ ] No emojis in code
- [ ] No TypeScript/Node.js files present

## Expected File Structure

```
slack-question-analyzer/
├── src/
│   ├── __init__.py
│   ├── __main__.py
│   ├── analyzer.py
│   ├── cli.py
│   ├── question_extractor.py
│   └── similarity_analyzer.py
├── .env
├── .env.example
├── .gitignore
├── requirements.txt
├── example_input.txt
├── README.md
├── QUICKSTART.md
├── OLLAMA_SETUP.md
├── TESTING.md
└── test_syntax.py
```

## Performance Expectations

- **Question Extraction**: < 1 second for 100 messages
- **Embedding Generation**: ~1-2 seconds per question with Ollama
- **Grouping**: < 5 seconds for 50 questions
- **Total Analysis**: ~2-3 minutes for 25 questions with Ollama

## Success Criteria

✅ All syntax tests pass
✅ All imports work
✅ CLI commands execute
✅ Example validation succeeds
✅ Full analysis completes
✅ Valid JSON output generated
✅ No errors in console output

If all tests pass, the application is working correctly!