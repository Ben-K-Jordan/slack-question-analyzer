"""
Command-line interface for the Slack Question Analyzer.
"""

import sys
import logging
import click
from pathlib import Path
from .analyzer import QuestionAnalyzer


@click.group()
@click.version_option(version='1.0.0')
@click.option('--verbose', '-v', is_flag=True, help='Show debug-level logs')
def cli(verbose):
    """
    Slack Question Analyzer - AI-powered question grouping and ranking.

    Analyzes Slack questions and groups similar ones together using AI embeddings.
    Supports Ollama (local), Azure OpenAI, and standard OpenAI.
    """
    logging.basicConfig(
        level=logging.DEBUG if verbose else logging.INFO,
        format='%(message)s')


@cli.command()
@click.argument('input_file', type=click.Path(exists=True))
@click.option('--output', '-o', type=click.Path(),
              help='Output file path (.json, .csv, or .md — format inferred from extension)')
@click.option('--provider', '-p', type=click.Choice(['ollama', 'azure', 'openai']),
              help='AI provider to use (default: from .env or ollama)')
@click.option('--threshold', '-t', type=click.FloatRange(0.0, 1.0),
              help='Similarity threshold (0-1)')
@click.option('--no-summary', is_flag=True, help='Skip printing summary to console')
@click.option('--no-cache', is_flag=True, help='Disable the persistent embedding cache')
@click.option('--no-labels', is_flag=True, help='Skip LLM-generated topic labels')
def analyze(input_file, output, provider, threshold, no_summary, no_cache, no_labels):
    """
    Analyze questions from a Slack content file.

    INPUT_FILE: Path to file containing Slack messages/questions

    Example:
        python -m src.cli analyze slack_content.txt -o results.json
    """
    try:
        # Initialize analyzer
        click.echo(f"Initializing analyzer with provider: {provider or 'from .env (default: ollama)'}")
        analyzer = QuestionAnalyzer(provider=provider, use_disk_cache=not no_cache,
                                    threshold=threshold,
                                    label_groups=False if no_labels else None)
        
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
        generation_model = click.prompt(
            'Chat model for LLM features (topic labels, summaries, etc.)',
            default='llama3.2')

        env_content.extend([
            "# Ollama Configuration",
            f"OLLAMA_URL={ollama_url}",
            f"OLLAMA_MODEL={ollama_model}",
            f"OLLAMA_GENERATION_MODEL={generation_model}",
        ])

        click.echo("\nMake sure Ollama is running and the models are pulled:")
        click.echo(f"   ollama pull {ollama_model}")
        click.echo(f"   ollama pull {generation_model}")

    elif provider == 'azure':
        click.echo("\nAzure OpenAI Configuration")
        api_key = click.prompt('Azure OpenAI API Key', hide_input=True)
        endpoint = click.prompt('Azure OpenAI Endpoint')
        deployment = click.prompt('Embedding Deployment Name')
        chat_deployment = click.prompt(
            'Chat Deployment Name for LLM features (leave empty to skip)',
            default='', show_default=False)
        api_version = click.prompt('API Version', default='2024-02-15-preview')

        env_content.extend([
            "# Azure OpenAI Configuration",
            f"AZURE_OPENAI_API_KEY={api_key}",
            f"AZURE_OPENAI_ENDPOINT={endpoint}",
            f"AZURE_OPENAI_DEPLOYMENT_NAME={deployment}",
            f"AZURE_OPENAI_API_VERSION={api_version}",
            "EMBEDDING_MODEL=text-embedding-ada-002",
        ])
        if chat_deployment:
            env_content.append(f"AZURE_OPENAI_CHAT_DEPLOYMENT={chat_deployment}")

    else:  # openai
        click.echo("\nOpenAI Configuration")
        api_key = click.prompt('OpenAI API Key', hide_input=True)
        chat_model = click.prompt('Chat model for LLM features', default='gpt-4o-mini')

        env_content.extend([
            "# OpenAI Configuration",
            f"OPENAI_API_KEY={api_key}",
            "EMBEDDING_MODEL=text-embedding-ada-002",
            f"CHAT_MODEL={chat_model}",
        ])

    env_content.extend([
        "",
        "# Optional LLM features: 'auto' (when the model is available), 'on', or 'off'",
        "GROUP_LABELS=auto",
        "LLM_VERIFY_GROUPS=auto",
        "LLM_EXTRACTION=auto",
        "LLM_ANSWER_DETECTION=auto",
        "EXECUTIVE_SUMMARY=auto",
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
        
        click.echo("File is valid!")
        click.echo("\nStatistics:")
        click.echo(f"  Total questions found: {len(questions)}")
        
        if questions:
            click.echo("\nSample questions:")
            for i, q in enumerate(questions[:5], 1):
                click.echo(f"  {i}. {q['text'][:80]}...")
        
    except Exception as e:
        click.echo(f"Error: {e}", err=True)
        sys.exit(1)


if __name__ == '__main__':
    cli()
