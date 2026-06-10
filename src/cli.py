"""
Command-line interface for the Slack Question Analyzer.
"""

import os
import sys
import click
from pathlib import Path
from .analyzer import QuestionAnalyzer


@click.group()
@click.version_option(version='1.0.0')
def cli():
    """
    Slack Question Analyzer - AI-powered question grouping and ranking.
    
    Analyzes Slack questions and groups similar ones together using AI embeddings.
    Supports Ollama (local), Azure OpenAI, and standard OpenAI.
    """
    pass


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(), help='Output JSON file path')
@click.option('--provider', '-p', type=click.Choice(['ollama', 'azure', 'openai']), 
              help='AI provider to use (default: from .env or ollama)')
@click.option('--threshold', '-t', type=float, help='Similarity threshold (0-1)')
@click.option('--no-summary', is_flag=True, help='Skip printing summary to console')
def analyze(input_file, output, provider, threshold, no_summary):
    """
    Analyze questions from a Slack content file.
    
    INPUT_FILE: Path to file containing Slack messages/questions
    
    Example:
        python -m src.cli analyze slack_content.txt -o results.json
    """
    try:
        # Set threshold if provided
        if threshold:
            os.environ['SIMILARITY_THRESHOLD'] = str(threshold)
        
        # Initialize analyzer
        click.echo(f"Initializing analyzer with provider: {provider or 'from .env (default: ollama)'}")
        analyzer = QuestionAnalyzer(provider=provider)
        
        # Set default output path if not provided
        if not output:
            input_path = Path(input_file)
            output = input_path.parent / f"{input_path.stem}_analysis.json"
        
        # Run analysis
        click.echo(f"\nAnalyzing: {input_file}")
        results = analyzer.analyze_from_file(input_file, str(output))
        
        # Print summary unless disabled
        if not no_summary:
            analyzer.print_summary(results)
        
        click.echo(f"\nAnalysis complete! Results saved to: {output}")
        
    except FileNotFoundError as e:
        click.echo(f"Error: File not found - {e}", err=True)
        sys.exit(1)
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


@cli.command()
def setup():
    """
    Setup wizard to configure the analyzer.
    
    Creates a .env file with your preferred AI provider settings.
    """
    click.echo("=== Slack Question Analyzer Setup ===\n")
    
    # Choose provider
    provider = click.prompt(
        'Choose AI provider',
        type=click.Choice(['ollama', 'azure', 'openai']),
        default='ollama'
    )
    
    env_content = [
        f"AI_PROVIDER={provider}",
        "",
        "# Similarity threshold (0-1, higher = more strict grouping)",
        "SIMILARITY_THRESHOLD=0.85",
        ""
    ]
    
    if provider == 'ollama':
        click.echo("\nOllama Configuration (Local & Free)")
        ollama_url = click.prompt('Ollama URL', default='http://localhost:11434')
        ollama_model = click.prompt('Embedding model', default='nomic-embed-text')
        
        env_content.extend([
            "# Ollama Configuration",
            f"OLLAMA_URL={ollama_url}",
            f"OLLAMA_MODEL={ollama_model}",
        ])
        
        click.echo("\nMake sure Ollama is running and the model is pulled:")
        click.echo(f"   ollama pull {ollama_model}")
        
    elif provider == 'azure':
        click.echo("\nAzure OpenAI Configuration")
        api_key = click.prompt('Azure OpenAI API Key', hide_input=True)
        endpoint = click.prompt('Azure OpenAI Endpoint')
        deployment = click.prompt('Deployment Name')
        api_version = click.prompt('API Version', default='2024-02-15-preview')
        
        env_content.extend([
            "# Azure OpenAI Configuration",
            f"AZURE_OPENAI_API_KEY={api_key}",
            f"AZURE_OPENAI_ENDPOINT={endpoint}",
            f"AZURE_OPENAI_DEPLOYMENT_NAME={deployment}",
            f"AZURE_OPENAI_API_VERSION={api_version}",
            "EMBEDDING_MODEL=text-embedding-ada-002",
        ])
        
    else:  # openai
        click.echo("\nOpenAI Configuration")
        api_key = click.prompt('OpenAI API Key', hide_input=True)
        
        env_content.extend([
            "# OpenAI Configuration",
            f"OPENAI_API_KEY={api_key}",
            "EMBEDDING_MODEL=text-embedding-ada-002",
        ])
    
    # Write .env file
    env_path = Path('.env')
    with open(env_path, 'w') as f:
        f.write('\n'.join(env_content))
    
    click.echo(f"\nConfiguration saved to {env_path}")
    click.echo("\nYou're all set! Run 'python -m src.cli analyze <input_file>' to start analyzing.")


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
def validate(input_file):
    """
    Validate input file format and show statistics.
    
    INPUT_FILE: Path to file containing Slack messages/questions
    """
    try:
        from .question_extractor import QuestionExtractor
        
        click.echo(f"Validating: {input_file}\n")
        
        with open(input_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        extractor = QuestionExtractor()
        questions = extractor.parse_slack_content(content)
        
        click.echo(f"File is valid!")
        click.echo(f"\nStatistics:")
        click.echo(f"  Total questions found: {len(questions)}")
        
        if questions:
            click.echo(f"\nSample questions:")
            for i, q in enumerate(questions[:5], 1):
                click.echo(f"  {i}. {q['text'][:80]}...")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
