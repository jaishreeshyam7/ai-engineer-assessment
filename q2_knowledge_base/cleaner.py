"""
Question 2: Production-Ready Knowledge Base - Ingestion, Cleaning, and PII Anonymization
Pipeline that ingests unstructured documents/web content, strips boilerplate,
normalizes terminology, detects extraction flaws, and redacts PII.
"""

import re
import hashlib
from typing import Dict, List, Tuple, Any, Optional

class DataCleaner:
    """
    Cleans raw HTML/Text/PDF extractions:
    - Removes boilerplate (navbars, headers, footers, cookies, disclaimers)
    - Deduplicates identical and near-duplicate records
    - Standardizes terminology, currency formats, dates, and headings
    - Detects & redacts PII (Emails, Phones, SSN/TIN, Credit Cards, Names)
    """

    # Terminology standardization dictionary
    TERMINOLOGY_MAP = {
        r"\bpre-existing conditions?\b": "pre_existing_conditions",
        r"\bopd\b": "outpatient_department",
        r"\bipd\b": "inpatient_department",
        r"\btpa\b": "third_party_administrator",
        r"\bco-pay(ment)?\b": "copayment",
        r"\bdeductable\b": "deductible",  # typo fix
        r"\bno-claim bonus\b": "no_claim_discount",
        r"\bdp\b": "down_payment",
        r"\bcicilan\b": "installment",
        r"\btenor\b": "loan_term",
    }

    # Regex patterns for PII protection
    PII_PATTERNS = [
        (r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", "[REDACTED_EMAIL]"),
        (r"(?:\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}\b", "[REDACTED_PHONE]"),
        (r"\b\d{3}-\d{2}-\d{4}\b", "[REDACTED_SSN]"),
        (r"\b(?:\d{4}[-\s]?){3}\d{4}\b", "[REDACTED_CARD]"),
        (r"\b(?:Customer ID|Policyholder Name):\s*[A-Z][a-z]+ [A-Z][a-z]+", "Customer: [REDACTED_NAME]"),
    ]

    # Boilerplate patterns (navigation, footers, cookie banners)
    BOILERPLATE_PATTERNS = [
        r"(?i)cookie policy|we use cookies.*?(accept|manage)",
        r"(?i)all rights reserved\.\s*copyright.*?\d{4}",
        r"(?i)terms of service\s*\|\s*privacy policy\s*\|\s*contact us",
        r"(?i)skip to main content",
        r"(?i)navigation menu.*?(home|about|products|contact)",
        r"(?i)subscribe to our newsletter.*",
    ]

    def __init__(self):
        self.seen_fingerprints = set()

    def clean_raw_text(self, text: str) -> Tuple[str, List[str]]:
        """
        Removes boilerplate, normalizes whitespace, standardizes terms,
        and logs cleaning flags.
        """
        flags = []
        cleaned = text

        # Strip navigation/boilerplate
        for pattern in self.BOILERPLATE_PATTERNS:
            if re.search(pattern, cleaned):
                cleaned = re.sub(pattern, " ", cleaned)
                flags.append(f"Boilerplate pattern removed: {pattern[:30]}...")

        # Whitespace & line-break normalization
        cleaned = re.sub(r"\r\n|\r", "\n", cleaned)
        cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
        cleaned = re.sub(r"[ \t]{2,}", " ", cleaned)
        cleaned = cleaned.strip()

        # Handle obvious extraction corruption or empty text
        if len(cleaned) < 20:
            flags.append("FLAG_SHORT_OR_CORRUPT: content too short or malformed")

        # Standardize terminology
        for raw_pattern, standard_term in self.TERMINOLOGY_MAP.items():
            if re.search(raw_pattern, cleaned, flags=re.IGNORECASE):
                cleaned = re.sub(raw_pattern, standard_term, cleaned, flags=re.IGNORECASE)

        return cleaned, flags

    def redact_pii(self, text: str) -> Tuple[str, bool]:
        """
        Scans for sensitive personally identifiable information (PII)
        and replaces with privacy-safe redaction tokens.
        """
        pii_found = False
        sanitized = text
        for pattern, replacement in self.PII_PATTERNS:
            if re.search(pattern, sanitized):
                pii_found = True
                sanitized = re.sub(pattern, replacement, sanitized)
        return sanitized, pii_found

    def compute_simhash_fingerprint(self, text: str) -> str:
        """
        Produces a normalized lexical hash for deduplication.
        """
        normalized = re.sub(r"\W+", " ", text.lower()).strip()
        tokens = sorted(list(set(normalized.split())))
        content_repr = " ".join(tokens)
        return hashlib.sha256(content_repr.encode("utf-8")).hexdigest()

    def is_duplicate(self, text: str) -> bool:
        """
        Checks if the document or chunk has already been processed or is near-duplicate.
        """
        fingerprint = self.compute_simhash_fingerprint(text)
        if fingerprint in self.seen_fingerprints:
            return True
        self.seen_fingerprints.add(fingerprint)
        return False
