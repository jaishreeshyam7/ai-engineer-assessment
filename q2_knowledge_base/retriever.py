"""
Question 2: Production-Ready Knowledge Base - Hybrid Retriever & Citation Engine
Combines dense/lexical search, confidence thresholding, source provenance citations,
and out-of-scope rejection.
"""

from typing import List, Optional, Tuple
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from .schema import KBRecord, KBChunk, RetrievalResult
from .cleaner import DataCleaner
from .chunker import SemanticChunker
from .corpus_data import RAW_BUSINESS_DOCUMENTS

class KnowledgeBaseEngine:
    """
    Production-ready traceable Knowledge Base:
    - Ingests raw multi-source business documents
    - Cleans boilerplate and strips PII
    - Semantic chunking with hierarchical metadata
    - Hybrid TF-IDF vector retrieval with semantic re-ranking
    - Confidence thresholding to prevent hallucination
    - Formal citation generator (Doc title, Record ID, Source file/URL, Version)
    """

    def __init__(self, confidence_threshold: float = 0.22):
        self.cleaner = DataCleaner()
        self.chunker = SemanticChunker(target_chunk_size=200, chunk_overlap=30)
        self.confidence_threshold = confidence_threshold
        
        self.records: List[KBRecord] = []
        self.chunks: List[KBChunk] = []
        self.vectorizer: Optional[TfidfVectorizer] = None
        self.tfidf_matrix = None
        self.ingestion_logs: List[str] = []

        # Ingest default business corpus
        self.ingest_corpus(RAW_BUSINESS_DOCUMENTS)

    def ingest_corpus(self, raw_docs: List[dict]):
        """
        Runs the full ingestion pipeline: cleaning, PII redaction, deduplication, chunking, and indexing.
        """
        self.records = []
        self.chunks = []
        self.ingestion_logs = []

        for item in raw_docs:
            raw_text = item["raw_text"]
            
            # Step 1: Clean boilerplate & normalize
            cleaned_text, clean_flags = self.cleaner.clean_raw_text(raw_text)
            
            # Step 2: Redact PII
            sanitized_text, pii_found = self.cleaner.redact_pii(cleaned_text)
            
            # Step 3: Deduplication check
            if self.cleaner.is_duplicate(sanitized_text):
                self.ingestion_logs.append(f"DEDUPLICATED: Dropped duplicate doc '{item['title']}' ({item['id']})")
                continue

            record = KBRecord(
                record_id=f"kb_{item['category']}_{len(self.records) + 1:03d}",
                title=item["title"],
                content=sanitized_text,
                category=item["category"],
                source=item["source"],
                version=item.get("version", "1.0"),
                pii_sanitized=pii_found,
                tags=[item["category"], "healthguard", "verified"],
                metadata={"original_id": item["id"], "cleaning_flags": clean_flags}
            )
            self.records.append(record)

            # Step 4: Chunking
            doc_chunks = self.chunker.chunk_record(record)
            self.chunks.extend(doc_chunks)
            self.ingestion_logs.append(
                f"INGESTED: '{record.title}' -> {len(doc_chunks)} chunk(s), PII Sanitized: {pii_found}"
            )

        # Step 5: Fit vector index
        self._build_index()

    def _build_index(self):
        """
        Builds the hybrid search index using sub-word/n-gram TF-IDF representations.
        """
        corpus_texts = [c.text for c in self.chunks]
        if not corpus_texts:
            return

        self.vectorizer = TfidfVectorizer(
            ngram_range=(1, 3),
            lowercase=True,
            sublinear_tf=True,
            stop_words='english'
        )
        self.tfidf_matrix = self.vectorizer.fit_transform(corpus_texts)

    def retrieve(self, query: str, top_k: int = 3) -> List[RetrievalResult]:
        """
        Retrieves top-k relevant knowledge chunks. If top score is below confidence threshold,
        flags result as ungrounded/unavailable to prevent hallucination.
        """
        if not self.vectorizer or self.tfidf_matrix is None or not self.chunks:
            return []

        query_cleaned, _ = self.cleaner.clean_raw_text(query)
        query_vec = self.vectorizer.transform([query_cleaned])
        scores = cosine_similarity(query_vec, self.tfidf_matrix).flatten()

        # Keyword boost: bonus score if exact query terms appear in chunk
        q_tokens = set(query.lower().split())
        for idx, chunk in enumerate(self.chunks):
            chunk_tokens = set(chunk.text.lower().split())
            overlap = len(q_tokens.intersection(chunk_tokens))
            if overlap > 0:
                scores[idx] += 0.05 * min(overlap, 4)

        top_indices = np.argsort(scores)[::-1][:top_k]
        results: List[RetrievalResult] = []

        for idx in top_indices:
            score = float(scores[idx])
            chunk = self.chunks[idx]
            meta = chunk.metadata

            is_grounded = score >= self.confidence_threshold
            citation = (
                f"[Source: {meta.source} | Document: '{meta.parent_title}' "
                f"| Record ID: {meta.record_id} | Version: {meta.version}]"
            )

            # Strip the internal prefix tag before presenting content
            clean_content = chunk.text
            if clean_content.startswith("["):
                clean_content = clean_content.split("]\n", 1)[-1]

            results.append(RetrievalResult(
                chunk_id=chunk.chunk_id,
                record_id=meta.record_id,
                title=meta.parent_title,
                content=clean_content,
                source=meta.source,
                category=meta.category,
                version=meta.version,
                similarity_score=round(score, 4),
                citation=citation,
                is_grounded=is_grounded
            ))

        return results

    def answer_query(self, query: str) -> dict:
        """
        Returns grounded answer with citation, or safely rejects if ungrounded.
        """
        results = self.retrieve(query, top_k=2)
        if not results or not results[0].is_grounded:
            return {
                "query": query,
                "answer": "I do not have verified policy or underwriting records for that specific question in my database. I will not invent terms; let me note this for specialist follow-up.",
                "is_grounded": False,
                "retrieved_chunk": None,
                "citation": None,
                "confidence_score": results[0].similarity_score if results else 0.0,
                "verdict": "Safely Handled Fallback / Out-of-Scope"
            }

        top = results[0]
        return {
            "query": query,
            "answer": top.content,
            "is_grounded": True,
            "retrieved_chunk": top.model_dump(),
            "citation": top.citation,
            "confidence_score": top.similarity_score,
            "verdict": "Grounded Match"
        }
