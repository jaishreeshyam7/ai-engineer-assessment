"""
Question 2: Production-Ready Knowledge Base - Data Schemas
Defines structured, traceable records with versioning, PII tracking, and provenance metadata.
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field
from datetime import datetime

class KBRecord(BaseModel):
    record_id: str = Field(..., description="Unique deterministic identifier (e.g., kb_policy_001)")
    title: str = Field(..., description="Human-readable title or heading of the knowledge unit")
    content: str = Field(..., description="Sanitized, cleaned text content")
    category: str = Field(..., description="Taxonomy category: product, policy, qualification, faq, objection, partnership")
    source: str = Field(..., description="Provenance source file, section, or URL")
    version: str = Field(default="1.0", description="Semantic version of document or policy")
    pii_sanitized: bool = Field(default=True, description="Flag confirming personal identifiable information was redacted")
    tags: List[str] = Field(default_factory=list, description="Categorical tags for filtering")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="Additional context such as eligibility criteria, limits")
    created_at: str = Field(default_factory=lambda: datetime.utcnow().isoformat())

class ChunkMetadata(BaseModel):
    chunk_id: str
    record_id: str
    parent_title: str
    category: str
    source: str
    version: str
    token_count: int
    tags: List[str] = Field(default_factory=list)

class KBChunk(BaseModel):
    chunk_id: str
    record_id: str
    text: str
    metadata: ChunkMetadata

class RetrievalResult(BaseModel):
    chunk_id: str
    record_id: str
    title: str
    content: str
    source: str
    category: str
    version: str
    similarity_score: float
    citation: str
    is_grounded: bool = True
