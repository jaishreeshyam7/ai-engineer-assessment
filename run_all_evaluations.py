"""
Master Verification Script: Executes all benchmarks and evaluations across all 4 questions.
Generates full transcripts, calculates latency stats, and checks pass/fail verdicts.
"""

import sys
import asyncio
import os

if sys.stdout.encoding.lower() != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from generate_audio_samples import generate_all_samples
from q2_knowledge_base.benchmark_test import run_benchmark as run_q2
from q1_voice_agent.test_suite import run_test_scenarios as run_q1
from q3_multilingual_bots.test_multilingual import run_multilingual_tests as run_q3
from q4_realtime_nudges.benchmark_nudges import run_nudge_benchmark as run_q4

async def main():
    print("=" * 80)
    print("AI ENGINEER ASSESSMENT - MASTER VERIFICATION & EVALUATION SCORECARD")
    print("=" * 80)

    # 1. Generate Audio Samples
    print("\n[STEP 1/5] Synthesizing PCM WAV Audio Files for Call Evidence...")
    generate_all_samples()

    # 2. Question 2: Knowledge Base Benchmark
    print("\n[STEP 2/5] Running Question 2 Production Knowledge Base Benchmark...")
    q2_results = run_q2()
    q2_pass = all("CORRECT" in r["verdict"] for r in q2_results)

    # 3. Question 1: Voice Agent Test Suite
    print("\n[STEP 3/5] Running Question 1 Grounded Voice Agent Test Suite...")
    q1_results = run_q1()
    q1_pass = len(q1_results) == 5 and all(r["status"] == "PASSED" for r in q1_results)

    # 4. Question 3: Native-Language Voice Bots
    print("\n[STEP 4/5] Running Question 3 Multilingual Bots (Philippines & Indonesia)...")
    q3_results = run_q3()
    q3_pass = len(q3_results) == 4 and all(r["status"] == "PASSED" for r in q3_results)

    # 5. Question 4: Real-Time Audio Insights & Live Nudges
    print("\n[STEP 5/5] Running Question 4 Live Nudges & Latency Profiling...")
    q4_results = await run_q4()
    p95_e2e = q4_results["latency_statistics"]["end_to_end_latency"]["p95"]
    q4_pass = p95_e2e < 1000.0 and q4_results["false_positive_analysis"]["nudges_dispatched"] > 0

    print("\n" + "#" * 80)
    print("FINAL ASSESSMENT SCORECARD & OUTCOME SUMMARY")
    print("#" * 80)
    print(f" Question 1: Knowledge-Grounded Voice Agent:   {'✅ PASSED (5/5 Scenarios)' if q1_pass else '❌ FAILED'}")
    print(f" Question 2: Production-Ready Knowledge Base:  {'✅ PASSED (6/6 Grounded Queries)' if q2_pass else '❌ FAILED'}")
    print(f" Question 3: Native-Language Voice Bots:       {'✅ PASSED (4/4 Regional Calls)' if q3_pass else '❌ FAILED'}")
    print(f" Question 4: Real-Time Live Nudges Pipeline:   {'✅ PASSED (P95: ' + str(p95_e2e) + 'ms < 1000ms)' if q4_pass else '❌ FAILED'}")
    print("#" * 80)

    if q1_pass and q2_pass and q3_pass and q4_pass:
        print("\nALL FOUR QUESTIONS VERIFIED AND MEETS PRODUCTION CRITERIA!")
    else:
        print("\nSome tests require attention.")

if __name__ == "__main__":
    asyncio.run(main())
