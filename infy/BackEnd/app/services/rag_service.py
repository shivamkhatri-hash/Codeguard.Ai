import re
from typing import List, Dict, Any, Optional

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

from app.core.rag_kb import SECURE_CODING_DOCUMENTS


class RAGService:
    def __init__(self):
        self.vectorizer = TfidfVectorizer(stop_words="english")
        self.chunks: List[str] = []
        self.metadata: List[Dict[str, Any]] = []
        self.matrix = None
        self._initialize_index()

    def _clean_text(self, text: str) -> str:
        """
        Cleans and normalizes text for indexing and querying.
        """
        text = text.lower().strip()
        text = re.sub(r"\s+", " ", text)
        return text

    def _initialize_index(self):
        """
        Loads documents, creates chunks, and builds the TF-IDF matrix.
        """
        raw_chunks = []
        raw_meta = []

        for doc in SECURE_CODING_DOCUMENTS:
            title = doc["title"]
            category = doc["category"]
            content = doc["content"]
            tags = doc.get("tags", [])

            cleaned_full = self._clean_text(
                f"{title} {content} {' '.join(tags)}"
            )

            raw_chunks.append(cleaned_full)

            raw_meta.append(
                {
                    "title": title,
                    "category": category,
                    "full_text": content,
                    "snippet": content[:200] + "...",
                    "tags": tags,
                }
            )

            paragraphs = [
                p.strip()
                for p in content.split("\n\n")
                if p.strip()
            ]

            for p in paragraphs:
                cleaned_p = self._clean_text(
                    f"{title} {p} {' '.join(tags)}"
                )

                raw_chunks.append(cleaned_p)

                raw_meta.append(
                    {
                        "title": title,
                        "category": category,
                        "full_text": p,
                        "snippet": p,
                        "tags": tags,
                    }
                )

        self.chunks = raw_chunks
        self.metadata = raw_meta

        if self.chunks:
            self.matrix = self.vectorizer.fit_transform(
                self.chunks
            )

    def query(
        self,
        query_text: str,
        language: Optional[str] = None,
        top_k: int = 3,
    ) -> List[Dict[str, Any]]:
        """
        Search the secure-coding knowledge base.

        Only reasonably relevant results are returned.
        """

        if not self.chunks or self.matrix is None:
            return []

        cleaned_query = self._clean_text(query_text)

        if language:
            cleaned_query += f" {language.lower()}"

        query_vec = self.vectorizer.transform(
            [cleaned_query]
        )

        similarities = cosine_similarity(
            query_vec,
            self.matrix,
        ).flatten()

        top_indices = np.argsort(similarities)[::-1][:top_k]

        results = []

        for idx in top_indices:
            score = float(similarities[idx])

            # Reject extremely weak matches.
            if score < 0.15:
                continue

            results.append(
                {
                    "title": self.metadata[idx]["title"],
                    "category": self.metadata[idx]["category"],
                    "content": self.metadata[idx]["full_text"],
                    "score": score,
                    "tags": self.metadata[idx].get("tags", []),
                }
            )

        return results

    def _get_topic_keywords(
        self,
        finding_title: str,
        finding_description: str,
    ) -> List[str]:
        """
        Identify strong topic keywords for a finding.

        These keywords prevent unrelated RAG documents from being
        returned simply because of weak word similarity.
        """

        title = finding_title.lower()
        description = finding_description.lower()
        combined = f"{title} {description}"

        if (
            "missing docstring" in combined
            or "docstring" in combined
            or "missing documentation" in combined
        ):
            return [
                "docstring",
                "documentation",
                "pep 257",
            ]

        if (
            "sql injection" in combined
            or "sql injection vulnerability" in combined
        ):
            return [
                "sql injection",
                "parameterized query",
                "prepared statement",
            ]

        if (
            "xss" in combined
            or "cross-site scripting" in combined
            or "cross site scripting" in combined
        ):
            return [
                "xss",
                "cross-site scripting",
                "output encoding",
                "escape",
            ]

        if (
            "hardcoded credential" in combined
            or "hard-coded credential" in combined
            or "hardcoded password" in combined
            or "hardcoded secret" in combined
            or "hardcoded" in combined
        ):
            return [
                "hardcoded",
                "hard-coded",
                "credential",
                "secret",
                "environment variable",
            ]

        if (
            "debug mode" in combined
            or "debug enabled" in combined
            or "debug" in title
        ):
            return [
                "debug",
                "production",
                "disable debug",
            ]

        if (
            "complexity" in combined
            or "cyclomatic" in combined
            or "maintainability" in combined
            or "code smell" in combined
            or "architecture" in combined
        ):
            return [
                "complexity",
                "cyclomatic",
                "maintainability",
                "refactoring",
                "architecture",
            ]

        if (
            "input validation" in combined
            or "unvalidated input" in combined
        ):
            return [
                "input validation",
                "validate input",
                "user input",
            ]

        if (
            "command injection" in combined
            or "os command" in combined
        ):
            return [
                "command injection",
                "command execution",
                "input validation",
            ]

        if (
            "path traversal" in combined
            or "directory traversal" in combined
        ):
            return [
                "path traversal",
                "directory traversal",
                "file path validation",
            ]

        if (
            "insecure deserialization" in combined
            or "unsafe deserialization" in combined
        ):
            return [
                "deserialization",
                "unsafe deserialization",
                "trusted input",
            ]

        if (
            "weak cryptography" in combined
            or "weak encryption" in combined
            or "weak hash" in combined
        ):
            return [
                "cryptography",
                "encryption",
                "secure hash",
            ]

        return []

    def get_remediation(
        self,
        finding_title: str,
        finding_description: str,
        language: str,
    ) -> str:
        """
        Retrieve remediation guidance specifically related to
        the supplied finding.

        Exact topic matching is preferred over generic similarity.
        """

        topic_keywords = self._get_topic_keywords(
            finding_title,
            finding_description,
        )

        # ---------------------------------------------------------
        # STEP 1: Topic-specific RAG search
        # ---------------------------------------------------------

        if topic_keywords:

            targeted_query = (
                f"{finding_title} "
                f"{finding_description} "
                f"{' '.join(topic_keywords)}"
            )

            hits = self.query(
                targeted_query,
                language=language,
                top_k=5,
            )

            # Only accept a result containing the actual topic.
            for hit in hits:

                content = hit["content"].lower()
                title = hit["title"].lower()
                tags = " ".join(
                    str(tag).lower()
                    for tag in hit.get("tags", [])
                )

                searchable_text = (
                    f"{title} {content} {tags}"
                )

                matched_keywords = [
                    keyword
                    for keyword in topic_keywords
                    if keyword in searchable_text
                ]

                if matched_keywords:
                    return hit["content"].strip()

        # ---------------------------------------------------------
        # STEP 2: Generic RAG search
        # ---------------------------------------------------------

        query_text = (
            f"{finding_title} "
            f"{finding_description}"
        )

        hits = self.query(
            query_text,
            language=language,
            top_k=3,
        )

        for hit in hits:

            score = float(
                hit.get("score", 0.0)
            )

            if score < 0.20:
                continue

            content = hit["content"].strip()
            content_lower = content.lower()

            if any(
                keyword in content_lower
                for keyword in (
                    "remediation",
                    "prevention",
                    "mitigation",
                    "guidelines",
                    "secure coding",
                )
            ):
                return content

        # ---------------------------------------------------------
        # STEP 3: No sufficiently reliable RAG match
        # ---------------------------------------------------------

        return (
            f"No sufficiently specific secure-coding guidance "
            f"was found in the knowledge base for "
            f"'{finding_title}'. Follow the finding's explicit "
            f"recommendation and established {language.capitalize()} "
            f"secure-coding practices."
        )


rag_service = RAGService()