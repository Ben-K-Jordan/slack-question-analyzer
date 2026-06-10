"""
Main analyzer module that orchestrates question extraction, grouping, and ranking.
"""

import os
import json
from typing import List, Dict, Optional, Literal
from datetime import datetime
from dotenv import load_dotenv
from .question_extractor import QuestionExtractor
from .similarity_analyzer import SimilarityAnalyzer


class QuestionAnalyzer:
    """Main analyzer class that coordinates the analysis pipeline."""
    
    def __init__(self, provider: Optional[Literal['azure', 'openai', 'ollama']] = None):
        """
        Initialize the analyzer.
        
        Args:
            provider: AI provider to use ('azure', 'openai', or 'ollama').
                     If None, reads from AI_PROVIDER env variable (defaults to 'ollama')
        """
        load_dotenv()
        
        if provider is None:
            provider = os.getenv('AI_PROVIDER', 'ollama')
        
        self.extractor = QuestionExtractor()
        self.similarity_analyzer = SimilarityAnalyzer(provider=provider)
    
    def analyze_slack_content(self, content: str) -> Dict:
        """
        Analyze Slack content and return grouped questions.
        
        Args:
            content: Raw Slack content string
            
        Returns:
            Dictionary containing analysis results
        """
        print("Step 1: Extracting questions from Slack content...")
        questions = self.extractor.parse_slack_content(content)
        print(f"Found {len(questions)} questions")
        
        if not questions:
            return {
                'total_questions': 0,
                'total_groups': 0,
                'groups': [],
                'metadata': {
                    'analyzed_at': datetime.utcnow().isoformat(),
                    'similarity_threshold': self.similarity_analyzer.similarity_threshold,
                    'model': self.similarity_analyzer.embedding_model
                }
            }
        
        print("\nStep 2: Grouping similar questions using AI...")
        groups = self.similarity_analyzer.group_similar_questions(questions)
        print(f"Created {len(groups)} question groups")
        
        # Add keywords to each group
        print("\nStep 3: Extracting keywords from groups...")
        for group in groups:
            group['keywords'] = self._extract_keywords(group['questions'])
        
        # Separate single-question groups
        multi_question_groups = [g for g in groups if g['count'] > 1]
        single_questions = [g for g in groups if g['count'] == 1]
        
        result = {
            'total_questions': len(questions),
            'total_groups': len(multi_question_groups),
            'groups': multi_question_groups,
            'ungrouped_questions': [q['questions'][0] for q in single_questions],
            'metadata': {
                'analyzed_at': datetime.utcnow().isoformat(),
                'similarity_threshold': self.similarity_analyzer.similarity_threshold,
                'model': self.similarity_analyzer.embedding_model,
                'provider': self.similarity_analyzer.provider
            }
        }
        
        return result
    
    def analyze_from_file(self, input_path: str, output_path: Optional[str] = None) -> Dict:
        """
        Analyze questions from a file.
        
        Args:
            input_path: Path to input file containing Slack content
            output_path: Optional path to save results as JSON
            
        Returns:
            Analysis results dictionary
        """
        print(f"Reading input from: {input_path}")
        
        with open(input_path, 'r', encoding='utf-8') as f:
            content = f.read()
        
        results = self.analyze_slack_content(content)
        
        if output_path:
            print(f"\nSaving results to: {output_path}")
            with open(output_path, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
        
        return results
    
    def _extract_keywords(self, questions: List[Dict]) -> List[str]:
        """
        Extract common keywords from a group of questions.
        
        Args:
            questions: List of question dictionaries
            
        Returns:
            List of keywords
        """
        # Common words to ignore
        stop_words = {
            'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for',
            'of', 'with', 'by', 'from', 'as', 'is', 'was', 'are', 'were', 'been',
            'be', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would',
            'could', 'should', 'may', 'might', 'can', 'this', 'that', 'these',
            'those', 'i', 'you', 'he', 'she', 'it', 'we', 'they', 'what', 'which',
            'who', 'when', 'where', 'why', 'how', 'there', 'here'
        }
        
        # Count word frequencies
        word_freq = {}
        for q in questions:
            words = q['normalized_text'].lower().split()
            for word in words:
                # Remove non-alphanumeric characters
                word = ''.join(c for c in word if c.isalnum())
                if len(word) > 3 and word not in stop_words:
                    word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        keywords = [word for word, freq in sorted_words[:5]]
        
        return keywords
    
    def print_summary(self, results: Dict):
        """
        Print a human-readable summary of the analysis.
        
        Args:
            results: Analysis results dictionary
        """
        print("\n" + "="*80)
        print("QUESTION ANALYSIS SUMMARY")
        print("="*80)
        print(f"\nTotal Questions Analyzed: {results['total_questions']}")
        print(f"Question Groups Found: {results['total_groups']}")
        print(f"Ungrouped Questions: {len(results['ungrouped_questions'])}")
        print(f"Similarity Threshold: {results['metadata']['similarity_threshold']}")
        print(f"Model Used: {results['metadata']['model']}")
        
        if results['groups']:
            print("\n" + "-"*80)
            print("TOP QUESTION GROUPS (Ranked by Frequency)")
            print("-"*80)
            
            for i, group in enumerate(results['groups'][:10], 1):  # Show top 10
                print(f"\n#{i} - Occurrences: {group['count']}")
                print(f"Representative Question: {group['representative_question']}")
                print(f"Keywords: {', '.join(group['keywords'])}")
                print(f"Average Similarity: {group['avg_similarity']:.2%}")
                
                if group['count'] <= 5:  # Show all questions if 5 or fewer
                    print("All questions in this group:")
                    for q in group['questions']:
                        print(f"  - {q['text'][:100]}...")
        
        if results['ungrouped_questions']:
            print("\n" + "-"*80)
            print(f"UNIQUE QUESTIONS ({len(results['ungrouped_questions'])})")
            print("-"*80)
            for q in results['ungrouped_questions'][:5]:  # Show first 5
                print(f"  - {q['text'][:100]}...")
            
            if len(results['ungrouped_questions']) > 5:
                print(f"  ... and {len(results['ungrouped_questions']) - 5} more")
        
        print("\n" + "="*80)
