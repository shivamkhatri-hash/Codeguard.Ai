import re
from typing import List, Dict, Any, Optional
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.core.rag_kb import SECURE_CODING_DOCUMENTS

class RAGService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words='english')
        self.chunks: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.matrix = None
        self._initialize_index()

    def _clean_text(self, text: str) -> str:
        """
        Cleans and normalizes text for indexing/querying.
        """
        # Lowercase, strip whitespaces, remove excessive lines
        text = text.lower().strip()
        text = re.sub(r'\s+', ' ', text)
        return text

    def _initialize_index(self):
        """
        Loads documents, cleans them, chunks them, and builds the TF-IDF matrix.
        """
        raw_chunks = []
        raw_meta = []

        for doc in SECURE_CODING_DOCUMENTS:
            title = doc["title"]
            category = doc["category"]
            content = doc["content"]
            tags = doc.get("tags", [])

            # We can create a chunk from the entire document content
            cleaned_full = self._clean_text(f"{title} {content} {' '.join(tags)}")
            raw_chunks.append(cleaned_full)
            raw_meta.append({
                "title": title,
                "category": category,
                "full_text": content,
                "snippet": content[:200] + "..."
            })

            # We can also chunk the content by paragraphs to allow more granular matches
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            for p in paragraphs:
                cleaned_p = self._clean_text(f"{title} {p} {' '.join(tags)}")
                raw_chunks.append(cleaned_p)
                raw_meta.append({
                    "title": title,
                    "category": category,
                    "full_text": p,
                    "snippet": p
                })

        self.chunks = raw_chunks
        self.metadata = raw_meta
        
        if self.chunks:
            self.matrix = self.vectorizer.fit_transform(self.chunks)

    def query(self, query_text: str, language: Optional[str] = None, top_k: int = 1) -> List[Dict[str, Any]]:
        """
        Searches the secure coding knowledge base for the most relevant remediation guidelines.
        """
        if not self.chunks or self.matrix is None:
            return []

        # Clean query
        cleaned_query = self._clean_text(query_text)
        if language:
            cleaned_query += f" {language.lower()}"

        query_vec = self.vectorizer.transform([cleaned_query])
        similarities = cosine_similarity(query_vec, self.matrix).flatten()

        # Get top-k indices
        top_indices = np.argsort(similarities)[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score = float(similarities[idx])
            # Set a very low similarity threshold to capture general matches
            if score > 0.02:
                results.append({
                    "title": self.metadata[idx]["title"],
                    "category": self.metadata[idx]["category"],
                    "content": self.metadata[idx]["full_text"],
                    "score": score
                })
        return results

    def get_remediation(self, finding_title: str, finding_description: str, language: str) -> str:
        """
        Retrieves matching secure coding guidelines and extracts the recommendation section.
        """
        # Query with finding details
        query_str = f"{finding_title} {finding_description}"
        hits = self.query(query_str, language=language, top_k=2)

        if hits:
            # Prefer hits that contain specific code snippets or remediation steps
            for hit in hits:
                content = hit["content"]
                if "remediation" in content.lower() or "prevention" in content.lower() or "guidelines" in content.lower():
                    return content.strip()
            return hits[0]["content"].strip()

        # Fallback generic recommendation
        return f"Ensure that all user inputs are fully disinfected, bounds are checked, and standard secure coding patterns for {language.capitalize()} are implemented."

rag_service = RAGService()
