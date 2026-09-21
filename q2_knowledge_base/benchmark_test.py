"""
Question 2: Retrieval Testing Benchmark Suite
Executes the required 5+ query benchmark spanning:
1. Product
2. Policy
3. Qualification
4. FAQ
5. Objection
6. Out-of-scope safety check (rejecting ungrounded hallucination)

Prints structured evaluation tables with source citations, relevance explanations, and verdicts.
"""

import json
from .retriever import KnowledgeBaseEngine

BENCHMARK_QUERIES = [
    {
        "type": "Product",
        "question": "What are the pre-hospitalization and post-hospitalization medical expense coverage limits?",
        "expected_terms": ["60 days", "180 days", "pre-hospitalization", "post-hospitalization"],
        "relevance_explanation": "Must retrieve Product Specifications specifying 60 days prior and 180 days after hospital discharge."
    },
    {
        "type": "Policy",
        "question": "What is the waiting period for pre-existing medical conditions?",
        "expected_terms": ["24-month", "waiting period", "pre_existing_conditions"],
        "relevance_explanation": "Must retrieve Policy Exclusions & Waiting Periods section detailing the 24-month pre-existing condition clause."
    },
    {
        "type": "Qualification",
        "question": "Can an applicant with controlled diabetes or high blood pressure qualify for coverage?",
        "expected_terms": ["controlled hypertension", "Type-2 diabetes", "15% premium loading", "underwriting"],
        "relevance_explanation": "Must retrieve Underwriting Qualification Guidelines stating controlled diabetes/hypertension qualify with 15% loading."
    },
    {
        "type": "FAQ",
        "question": "How fast are cashless claims pre-authorized at network hospitals?",
        "expected_terms": ["60 minutes", "30 minutes", "pre-authorization", "cashless"],
        "relevance_explanation": "Must retrieve Customer FAQs indicating 60 minutes for planned admissions and 30 minutes for emergencies."
    },
    {
        "type": "Objection",
        "question": "I already have health coverage through my employer, why should I buy a personal policy?",
        "expected_terms": ["employer", "terminates", "laid off", "retire", "super top-up", "continuous"],
        "relevance_explanation": "Must retrieve Objection Playbook explaining company cover terminates upon job transition/retirement."
    },
    {
        "type": "Out-of-Scope / Fallback Test",
        "question": "Does this plan cover elective cosmetic nose jobs or cryptocurrency trading losses?",
        "expected_terms": [],
        "relevance_explanation": "Must safely detect lack of coverage, avoid hallucination, and state information is unavailable or permanently excluded."
    }
]

def run_benchmark():
    kb = KnowledgeBaseEngine()
    print("=" * 80)
    print("QUESTION 2: KNOWLEDGE BASE RETRIEVAL BENCHMARK EVALUATION")
    print(f"Total Ingested Records: {len(kb.records)} | Total Search Chunks: {len(kb.chunks)}")
    print("=" * 80)

    results_report = []

    for idx, test_case in enumerate(BENCHMARK_QUERIES, 1):
        q_text = test_case["question"]
        q_type = test_case["type"]
        explanation = test_case["relevance_explanation"]
        
        response = kb.answer_query(q_text)
        chunk = response.get("retrieved_chunk")
        score = response.get("confidence_score", 0.0)

        # Determine Verdict
        if q_type == "Out-of-Scope / Fallback Test":
            # For out of scope, correct verdict means safely rejecting or returning permanent exclusion
            if not response["is_grounded"] or "excluded" in response.get("answer", "").lower():
                verdict = "CORRECT (Safely Handled / No Hallucination)"
            else:
                verdict = "INCORRECT (Hallucinated)"
        else:
            if response["is_grounded"] and any(term.lower() in response["answer"].lower() for term in test_case["expected_terms"]):
                verdict = "CORRECT"
            elif response["is_grounded"]:
                verdict = "PARTIALLY CORRECT"
            else:
                verdict = "INCORRECT (Failed to retrieve)"

        entry = {
            "query_number": idx,
            "category": q_type,
            "user_question": q_text,
            "retrieved_chunk_id": chunk["chunk_id"] if chunk else "N/A",
            "retrieved_title": chunk["title"] if chunk else "N/A",
            "source_reference": response.get("citation") or "N/A",
            "relevance_explanation": explanation,
            "confidence_score": score,
            "verdict": verdict,
            "retrieved_snippet": response["answer"][:180] + ("..." if len(response["answer"]) > 180 else "")
        }
        results_report.append(entry)

        print(f"\n[Query #{idx}] Category: {q_type}")
        print(f"Question: \"{q_text}\"")
        print(f"Retrieved: {entry['retrieved_title']} (Chunk: {entry['retrieved_chunk_id']})")
        print(f"Confidence Score: {score:.4f}")
        print(f"Citation: {entry['source_reference']}")
        print(f"Snippet: {entry['retrieved_snippet']}")
        print(f"Relevance Explanation: {explanation}")
        print(f"Verdict: >>> {verdict} <<<")

    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY: All 6 queries evaluated.")
    return results_report

if __name__ == "__main__":
    run_benchmark()
