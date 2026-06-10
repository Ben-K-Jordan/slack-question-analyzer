"""
Similarity analysis module using AI embeddings.
Supports Azure OpenAI, OpenAI, and local Ollama.
Groups similar questions together using semantic similarity.
"""

import os
import requests
from typing import List, Dict, Literal
from concurrent.futures import ThreadPoolExecutor, as_completed
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from openai import AzureOpenAI, OpenAI
from dotenv import load_dotenv


class SimilarityAnalyzer:
    """Analyzes question similarity using AI embeddings."""
    
    def __init__(self, provider: Literal['azure', 'openai', 'ollama'] = 'ollama'):
        """
        Initialize the similarity analyzer.
        
        Args:
            provider: AI provider to use ('azure', 'openai', or 'ollama')
        """
        load_dotenv()
        
        self.provider = provider
        self.similarity_threshold = float(os.getenv('SIMILARITY_THRESHOLD', '0.85'))
        
        if provider == 'azure':
            # Azure OpenAI configuration
            self.client = AzureOpenAI(
                api_key=os.getenv('AZURE_OPENAI_API_KEY'),
                api_version=os.getenv('AZURE_OPENAI_API_VERSION', '2024-02-15-preview'),
                azure_endpoint=os.getenv('AZURE_OPENAI_ENDPOINT')
            )
            self.deployment_name = os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')
            self.embedding_model = os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002')
        elif provider == 'openai':
            # Standard OpenAI configuration
            self.client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))
            self.deployment_name = None
            self.embedding_model = os.getenv('EMBEDDING_MODEL', 'text-embedding-ada-002')
        else:  # ollama
            # Local Ollama configuration
            self.client = None
            self.ollama_url = os.getenv('OLLAMA_URL', 'http://localhost:11434')
            self.embedding_model = os.getenv('OLLAMA_MODEL', 'nomic-embed-text')
            self.deployment_name = None
        
        self.embeddings_cache = {}
    
    def get_embedding(self, text: str) -> List[float]:
        """
        Get embedding vector for text.
        
        Args:
            text: Text to embed
            
        Returns:
            Embedding vector as list of floats
        """
        # Check cache first
        if text in self.embeddings_cache:
            return self.embeddings_cache[text]
        
        try:
            if self.provider == 'ollama':
                # Use Ollama API
                response = requests.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={
                        "model": self.embedding_model,
                        "prompt": text
                    }
                )
                response.raise_for_status()
                embedding = response.json()['embedding']
            elif self.provider == 'azure':
                response = self.client.embeddings.create(
                    input=text,
                    model=self.deployment_name
                )
                embedding = response.data[0].embedding
            else:  # openai
                response = self.client.embeddings.create(
                    input=text,
                    model=self.embedding_model
                )
                embedding = response.data[0].embedding
            
            self.embeddings_cache[text] = embedding
            return embedding
            
        except Exception as e:
            print(f"Error getting embedding: {e}")
    def _get_ollama_embeddings_parallel(self, texts: List[str], max_workers: int = 5):
        """
        Get embeddings from Ollama in parallel for better performance.
        
        Args:
            texts: List of texts to embed
            max_workers: Number of parallel requests (default: 5)
        """
        def get_single_embedding(text: str) -> tuple:
            """Helper function to get a single embedding."""
            try:
                response = requests.post(
                    f"{self.ollama_url}/api/embeddings",
                    json={
                        "model": self.embedding_model,
                        "prompt": text
                    },
                    timeout=30
                )
                response.raise_for_status()
                return (text, response.json()['embedding'])
            except Exception as e:
                print(f"Error getting embedding for text: {e}")
                return (text, None)
        
        # Process embeddings in parallel
        with ThreadPoolExecutor(max_workers=max_workers) as executor:
            futures = {executor.submit(get_single_embedding, text): text for text in texts}
            
            for future in as_completed(futures):
                text, embedding = future.result()
                if embedding is not None:
                    self.embeddings_cache[text] = embedding
    
            raise
    
    def get_embeddings_batch(self, texts: List[str]) -> np.ndarray:
        """
        Get embeddings for multiple texts efficiently.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            2D numpy array of embeddings
        """
        embeddings = []
        
        # Process in batches to avoid rate limits
        batch_size = 100 if self.provider != 'ollama' else 10  # Smaller batches for Ollama
        
        for i in range(0, len(texts), batch_size):
            batch = texts[i:i + batch_size]
            
            # Check which ones are not cached
            uncached_texts = [t for t in batch if t not in self.embeddings_cache]
            
            if uncached_texts:
                try:
                    if self.provider == 'ollama':
                        # Ollama with parallel processing for speed
                        self._get_ollama_embeddings_parallel(uncached_texts)
                    elif self.provider == 'azure':
                        response = self.client.embeddings.create(
                            input=uncached_texts,
                            model=self.deployment_name
                        )
                        for text, data in zip(uncached_texts, response.data):
                            self.embeddings_cache[text] = data.embedding
                    else:  # openai
                        response = self.client.embeddings.create(
                            input=uncached_texts,
                            model=self.embedding_model
                        )
                        for text, data in zip(uncached_texts, response.data):
                            self.embeddings_cache[text] = data.embedding
                        
                except Exception as e:
                    print(f"Error getting batch embeddings: {e}")
                    raise
            
            # Get all embeddings for this batch (from cache)
            batch_embeddings = [self.embeddings_cache[t] for t in batch]
            embeddings.extend(batch_embeddings)
        
        return np.array(embeddings)
    
    def calculate_similarity(self, embedding1: List[float], embedding2: List[float]) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Similarity score between 0 and 1
        """
        vec1 = np.array(embedding1).reshape(1, -1)
        vec2 = np.array(embedding2).reshape(1, -1)
        return cosine_similarity(vec1, vec2)[0][0]
    
    def group_similar_questions(self, questions: List[Dict]) -> List[Dict]:
        """
        Group similar questions together.
        
        Args:
            questions: List of question dictionaries with 'text' and 'normalized_text'
            
        Returns:
            List of question groups with representative questions
        """
        if not questions:
            return []
        
        print(f"Analyzing {len(questions)} questions...")
        
        # Get embeddings for all normalized questions
        texts = [q['normalized_text'] for q in questions]
        embeddings = self.get_embeddings_batch(texts)
        
        # Calculate similarity matrix
        similarity_matrix = cosine_similarity(embeddings)
        
        # Group questions using clustering approach
        groups = []
        assigned = set()
        
        for i in range(len(questions)):
            if i in assigned:
                continue
            
            # Start a new group with this question
            group_indices = [i]
            assigned.add(i)
            
            # Find similar questions
            for j in range(i + 1, len(questions)):
                if j in assigned:
                    continue
                
                # Check similarity with all questions in current group
                max_similarity = max(similarity_matrix[j][idx] for idx in group_indices)
                
                if max_similarity >= self.similarity_threshold:
                    group_indices.append(j)
                    assigned.add(j)
            
            # Create group dictionary
            group_questions = [questions[idx] for idx in group_indices]
            
            # Find the most representative question (closest to centroid)
            if len(group_indices) > 1:
                group_embeddings = embeddings[group_indices]
                centroid = np.mean(group_embeddings, axis=0)
                
                # Find question closest to centroid
                distances = [np.linalg.norm(emb - centroid) for emb in group_embeddings]
                representative_idx = group_indices[np.argmin(distances)]
                representative = questions[representative_idx]['text']
            else:
                representative = questions[group_indices[0]]['text']
            
            # Calculate average similarity (reuse similarity_matrix)
            if len(group_indices) > 1:
                # Extract similarities from pre-computed matrix
                similarities = []
                for idx1 in range(len(group_indices)):
                    for idx2 in range(idx1 + 1, len(group_indices)):
                        i, j = group_indices[idx1], group_indices[idx2]
                        similarities.append(similarity_matrix[i][j])
                avg_sim = float(np.mean(similarities)) if similarities else 1.0
            else:
                avg_sim = 1.0
            
            groups.append({
                'representative_question': representative,
                'questions': group_questions,
                'count': len(group_questions),
                'avg_similarity': avg_sim
            })
        
        # Sort groups by count (most common first)
        groups.sort(key=lambda x: x['count'], reverse=True)
        
        return groups
