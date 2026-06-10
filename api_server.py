"""
Flask API Server for Slack Question Analyzer
Provides REST endpoints for the React frontend
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import sys
from pathlib import Path
import traceback

# Add src to path
sys.path.append(str(Path(__file__).parent))
from src.analyzer import QuestionAnalyzer

app = Flask(__name__)
CORS(app)  # Enable CORS for React frontend

@app.route('/api/health', methods=['GET'])
def health_check():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'API server is running'})

@app.route('/api/analyze', methods=['POST'])
def analyze_transcript():
    """
    Analyze a Slack transcript
    
    Request body:
    {
        "content": "slack transcript text...",
        "provider": "ollama",  # optional, defaults to ollama
        "threshold": 0.85      # optional, defaults to 0.85
    }
    
    Returns:
    {
        "success": true,
        "data": {
            "total_questions": 49,
            "total_groups": 12,
            "groups": [...],
            "ungrouped_questions": [...],
            "metadata": {...}
        }
    }
    """
    try:
        # Get request data
        data = request.get_json()
        
        if not data or 'content' not in data:
            return jsonify({
                'success': False,
                'error': 'Missing required field: content'
            }), 400
        
        content = data['content']
        provider = data.get('provider', 'ollama')
        threshold = data.get('threshold', 0.85)
        
        # Validate content
        if not content or not content.strip():
            return jsonify({
                'success': False,
                'error': 'Content cannot be empty'
            }), 400
        
        # Run analysis
        analyzer = QuestionAnalyzer(provider=provider)
        results = analyzer.analyze_slack_content(content)
        
        return jsonify({
            'success': True,
            'data': results
        })
        
    except Exception as e:
        print(f"Error during analysis: {str(e)}")
        traceback.print_exc()
        return jsonify({
            'success': False,
            'error': str(e),
            'traceback': traceback.format_exc()
        }), 500

@app.route('/api/config', methods=['GET'])
def get_config():
    """Get current configuration"""
    try:
        from dotenv import load_dotenv
        import os
        
        load_dotenv()
        
        return jsonify({
            'success': True,
            'config': {
                'provider': os.getenv('AI_PROVIDER', 'ollama'),
                'threshold': float(os.getenv('SIMILARITY_THRESHOLD', '0.85')),
                'ollama_url': os.getenv('OLLAMA_URL', 'http://localhost:11434'),
                'ollama_model': os.getenv('OLLAMA_MODEL', 'nomic-embed-text')
            }
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

if __name__ == '__main__':
    print("=" * 60)
    print("Slack Question Analyzer API Server")
    print("=" * 60)
    print("Server running at: http://localhost:5000")
    print("Health check: http://localhost:5000/api/health")
    print("Analyze endpoint: POST http://localhost:5000/api/analyze")
    print("=" * 60)
    print("\nPress Ctrl+C to stop the server\n")
    
    app.run(debug=True, host='0.0.0.0', port=5000)

# Made with Bob
