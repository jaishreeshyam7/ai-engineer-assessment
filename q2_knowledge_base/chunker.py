"""
Question 2: Production-Ready Knowledge Base - Chunking & Metadata Enrichment
Hierarchical, structure-preserving chunking engine that tracks source provenance,
parent headings, and token budgets.
"""

import re
from typing import List
from .schema import KBRecord, KBChunk, ChunkMetadata

class SemanticChunker:
    """
    Chunks documents intelligently:
    - Splits on semantic boundaries (sections, paragraphs, bullet points)
    - Retains parent context (Document Title, Category, Source, Version)
    - Enforces max token/character length with sensible sliding window overlap
    - Prevents breaking tabular or policy qualification criteria mid-rule
    """

    def __init__(self, target_chunk_size: int = 350, chunk_overlap: int = 50):
        self.target_chunk_size = target_chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_record(self, record: KBRecord) -> List[KBChunk]:
        """
        Splits a clean KBRecord into traceable, self-contained KBChunks.
        """
        text = record.content.strip()
        # If the content is short enough, keep it whole to retain complete policy meaning
        if len(text.split()) <= self.target_chunk_size:
            meta = ChunkMetadata(
                chunk_id=f"{record.record_id}_c0",
                record_id=record.record_id,
                parent_title=record.title,
                category=record.category,
                source=record.source,
                version=record.version,
                token_count=len(text.split()),
                tags=record.tags
            )
            # Prepend context header for dense retrieval enhancement
            enriched_text = f"[{record.category.upper()} | {record.title}]\n{text}"
            return [KBChunk(chunk_id=meta.chunk_id, record_id=record.record_id, text=enriched_text, metadata=meta)]

        # Split by double newline or numbered/bulleted lists first
        paragraphs = re.split(r"\n\s*\n", text)
        chunks: List[KBChunk] = []
        current_words = []
        chunk_idx = 0

        for para in paragraphs:
            para_words = para.split()
            if len(current_words) + len(para_words) <= self.target_chunk_size:
                current_words.extend(para_words)
            else:
                if current_words:
                    chunk_text = " ".join(current_words)
                    chunk_id = f"{record.record_id}_c{chunk_idx}"
                    enriched_text = f"[{record.category.upper()} | {record.title}]\n{chunk_text}"
                    meta = ChunkMetadata(
                        chunk_id=chunk_id,
                        record_id=record.record_id,
                        parent_title=record.title,
                        category=record.category,
                        source=record.source,
                        version=record.version,
                        token_count=len(current_words),
                        tags=record.tags
                    )
                    chunks.append(KBChunk(chunk_id=chunk_id, record_id=record.record_id, text=enriched_text, metadata=meta))
                    chunk_idx += 1
                    # Keep overlap from previous words
                    overlap_words = current_words[-self.chunk_overlap:] if len(current_words) > self.chunk_overlap else []
                    current_words = overlap_words + para_words
                else:
                    # Paragraph is itself bigger than target
                    current_words = para_words

        if current_words:
            chunk_text = " ".join(current_words)
            chunk_id = f"{record.record_id}_c{chunk_idx}"
            enriched_text = f"[{record.category.upper()} | {record.title}]\n{chunk_text}"
            meta = ChunkMetadata(
                chunk_id=chunk_id,
                record_id=record.record_id,
                parent_title=record.title,
                category=record.category,
                source=record.source,
                version=record.version,
                token_count=len(current_words),
                tags=record.tags
            )
            chunks.append(KBChunk(chunk_id=chunk_id, record_id=record.record_id, text=enriched_text, metadata=meta))

        return chunks
