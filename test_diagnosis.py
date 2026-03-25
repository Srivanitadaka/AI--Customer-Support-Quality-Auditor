"""
CallAudit Pro — Diagnostic Script
Run this in your project folder:
    python test_diagnosis.py
"""

import sys
import traceback

print("=" * 55)
print("  CallAudit Pro — Module Diagnostic")
print("=" * 55)

results = {}

# ── Test 1: langchain_groq ──────────────────────────────
print("\n[1] Testing langchain_groq...")
try:
    from langchain_groq import ChatGroq
    print("    ✅ langchain_groq OK")
    results["langchain_groq"] = "OK"
except Exception:
    print("    ❌ langchain_groq FAILED:")
    traceback.print_exc()
    results["langchain_groq"] = "FAILED"

# ── Test 2: langchain_core ──────────────────────────────
print("\n[2] Testing langchain_core...")
try:
    from langchain_core.prompts import PromptTemplate
    from langchain_core.output_parsers import StrOutputParser
    print("    ✅ langchain_core OK")
    results["langchain_core"] = "OK"
except Exception:
    print("    ❌ langchain_core FAILED:")
    traceback.print_exc()
    results["langchain_core"] = "FAILED"

# ── Test 3: chromadb ────────────────────────────────────
print("\n[3] Testing chromadb...")
try:
    import chromadb
    print(f"    ✅ chromadb OK (version: {chromadb.__version__})")
    results["chromadb"] = "OK"
except Exception:
    print("    ❌ chromadb FAILED:")
    traceback.print_exc()
    results["chromadb"] = "FAILED"

# ── Test 4: chroma_store ────────────────────────────────
print("\n[4] Testing vector_db.chroma_store...")
try:
    from vector_db.chroma_store import index_stats
    stats = index_stats()
    print(f"    ✅ chroma_store OK — stats: {stats}")
    results["chroma_store"] = "OK"
except Exception:
    print("    ❌ chroma_store FAILED:")
    traceback.print_exc()
    results["chroma_store"] = "FAILED"

# ── Test 5: faiss ───────────────────────────────────────
print("\n[5] Testing faiss...")
try:
    import faiss
    print(f"    ✅ faiss OK")
    results["faiss"] = "OK"
except Exception:
    print("    ❌ faiss FAILED:")
    traceback.print_exc()
    results["faiss"] = "FAILED"

# ── Test 6: sentence_transformers ──────────────────────
print("\n[6] Testing sentence_transformers...")
try:
    from sentence_transformers import SentenceTransformer
    print("    ✅ sentence_transformers OK")
    results["sentence_transformers"] = "OK"
except Exception:
    print("    ❌ sentence_transformers FAILED:")
    traceback.print_exc()
    results["sentence_transformers"] = "FAILED"

# ── Test 7: rag_pipeline ────────────────────────────────
print("\n[7] Testing rag_pipeline import...")
try:
    from rag_pipeline.rag_pipeline import RAGPipeline
    print("    ✅ RAGPipeline import OK")
    results["rag_pipeline"] = "OK"
except Exception:
    print("    ❌ RAGPipeline import FAILED:")
    traceback.print_exc()
    results["rag_pipeline"] = "FAILED"

# ── Test 8: langchain_scorer ────────────────────────────
print("\n[8] Testing llm.langchain_scorer import...")
try:
    from llm.langchain_scorer import score_with_langchain
    print("    ✅ langchain_scorer import OK")
    results["langchain_scorer"] = "OK"
except Exception:
    print("    ❌ langchain_scorer import FAILED:")
    traceback.print_exc()
    results["langchain_scorer"] = "FAILED"

# ── Test 9: alert_engine ────────────────────────────────
print("\n[9] Testing realtime.alert_engine import...")
try:
    from realtime.alert_engine import AlertEngine
    print("    ✅ alert_engine import OK")
    results["alert_engine"] = "OK"
except Exception:
    print("    ❌ alert_engine import FAILED:")
    traceback.print_exc()
    results["alert_engine"] = "FAILED"

# ── Test 10: deepgram ───────────────────────────────────
print("\n[10] Testing deepgram...")
try:
    from deepgram import DeepgramClient
    print("    ✅ deepgram OK")
    results["deepgram"] = "OK"
except Exception:
    print("    ❌ deepgram FAILED:")
    traceback.print_exc()
    results["deepgram"] = "FAILED"

# ── Summary ─────────────────────────────────────────────
print("\n" + "=" * 55)
print("  SUMMARY")
print("=" * 55)
for module, status in results.items():
    icon = "✅" if status == "OK" else "❌"
    print(f"  {icon}  {module:<30} {status}")

failed = [m for m, s in results.items() if s == "FAILED"]
if failed:
    print(f"\n  ⚠️  {len(failed)} module(s) failed: {', '.join(failed)}")
    print("  → Share the output above and the fix will be provided.")
else:
    print("\n  ✅ All modules OK!")
    print("  → The error is a runtime data issue, not an import issue.")

print("=" * 55)