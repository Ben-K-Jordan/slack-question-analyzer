# GitHub Setup Guide

This guide will help you push your Slack Question Analyzer project to GitHub.

## Prerequisites

### 1. Install Git for Windows

1. Download Git from: https://git-scm.com/download/win
2. Run the installer
3. Use default settings (recommended)
4. Restart your PowerShell/terminal after installation

### 2. Create a GitHub Account (if you don't have one)

1. Go to: https://github.com
2. Sign up for a free account
3. Verify your email address

### 3. Create a New Repository on GitHub

1. Log in to GitHub
2. Click the "+" icon in the top right corner
3. Select "New repository"
4. Fill in the details:
   - **Repository name**: `slack-question-analyzer`
   - **Description**: "AI-powered Slack question analyzer with semantic grouping and ranking"
   - **Visibility**: Choose Public or Private
   - **DO NOT** initialize with README, .gitignore, or license (we already have these)
5. Click "Create repository"
6. **Copy the repository URL** (it will look like: `https://github.com/YOUR_USERNAME/slack-question-analyzer.git`)

## Push to GitHub

### Option 1: Using the Batch Script (Easiest)

1. Open `push_to_github.bat` in a text editor
2. Replace `YOUR_GITHUB_USERNAME` with your actual GitHub username
3. Save the file
4. Double-click `push_to_github.bat`
5. Follow the prompts

### Option 2: Manual Commands

Open PowerShell in the `slack-question-analyzer` directory and run these commands:

```powershell
# Initialize git repository
git init

# Add all files
git add .

# Create first commit
git commit -m "Initial commit: Slack Question Analyzer with AI-powered grouping"

# Add your GitHub repository as remote (replace YOUR_USERNAME)
git remote add origin https://github.com/YOUR_USERNAME/slack-question-analyzer.git

# Push to GitHub
git branch -M main
git push -u origin main
```

### Authentication

When you push for the first time, Git will ask for authentication:

**Option A: Personal Access Token (Recommended)**
1. Go to GitHub Settings → Developer settings → Personal access tokens → Tokens (classic)
2. Click "Generate new token (classic)"
3. Give it a name like "Slack Analyzer"
4. Select scopes: `repo` (full control of private repositories)
5. Click "Generate token"
6. **Copy the token** (you won't see it again!)
7. When Git asks for password, paste the token

**Option B: GitHub Desktop (Easiest)**
1. Download GitHub Desktop: https://desktop.github.com/
2. Install and sign in
3. File → Add Local Repository
4. Select your `slack-question-analyzer` folder
5. Click "Publish repository"

## What Gets Pushed

The following files will be uploaded to GitHub:

### Python Backend
- `src/` - All Python source code
- `requirements.txt` - Python dependencies
- `api_server.py` - Flask REST API
- `.env.example` - Environment configuration template

### React Frontend
- `Question Analyzer Design System/` - Complete UI with all components

### Documentation
- `README.md` - Main project documentation
- `QUICKSTART.md` - Quick start guide
- `OLLAMA_SETUP.md` - Ollama installation guide
- `TESTING.md` - Testing instructions
- `BACKEND_INTEGRATION.md` - API integration guide

### Configuration
- `.gitignore` - Files to exclude from Git
- `package.json` - Node.js metadata
- `tsconfig.json` - TypeScript configuration

### What's Excluded (via .gitignore)

These files will NOT be pushed (they're in .gitignore):
- `.env` - Your personal API keys and secrets
- `__pycache__/` - Python cache files
- `*.pyc` - Compiled Python files
- `node_modules/` - Node dependencies
- `venv/` - Python virtual environment
- `*.log` - Log files
- Test output files

## After Pushing

Your repository will be available at:
```
https://github.com/YOUR_USERNAME/slack-question-analyzer
```

### Add a Repository Description

1. Go to your repository on GitHub
2. Click the gear icon next to "About"
3. Add description: "AI-powered Slack question analyzer with semantic grouping and ranking"
4. Add topics: `slack`, `ai`, `nlp`, `question-analysis`, `ollama`, `python`, `react`
5. Save changes

### Enable GitHub Pages (Optional)

If you want to host the UI documentation:
1. Go to Settings → Pages
2. Source: Deploy from a branch
3. Branch: main, folder: /Question Analyzer Design System
4. Save

## Updating Your Repository

After making changes to your code:

```powershell
# Stage all changes
git add .

# Commit with a message
git commit -m "Description of your changes"

# Push to GitHub
git push
```

## Troubleshooting

### "git: command not found"
- Git is not installed or not in PATH
- Restart your terminal after installing Git
- Or use GitHub Desktop instead

### Authentication Failed
- Use a Personal Access Token instead of password
- Or use GitHub Desktop for easier authentication

### "Repository already exists"
- You may have already initialized git
- Check with: `git status`
- If so, skip `git init` and go straight to `git add .`

### Large Files Warning
- The Design System folder is large
- GitHub has a 100MB file size limit
- If you get warnings, the files are still pushed (unless they're over 100MB)

## Need Help?

- GitHub Docs: https://docs.github.com
- Git Basics: https://git-scm.com/book/en/v2/Getting-Started-Git-Basics
- GitHub Desktop: https://docs.github.com/en/desktop