"""
target-rag — RAG Data Poisoning + Indirect Prompt Injection Target
MITRE ATLAS: AML.T0054.002 (Indirect Prompt Injection), AML.T0057 (Exfiltration via RAG)
OWASP LLM Top 10: LLM01 (Prompt Injection), LLM03 (Training Data Poisoning)

Deliberate vulnerabilities:
  1. /add_document is unauthenticated — anyone can inject docs into the KB
  2. Retrieved documents are injected verbatim into the system context with no sanitization
  3. An attacker can embed injection payloads inside normal-looking documents
"""
import sys
import os

sys.path.insert(0, "/shared")
from mock_llm import MockVulnerableLLM

import chromadb
from flask import Flask, request, jsonify

app = Flask(__name__)
llm = MockVulnerableLLM()

chroma = chromadb.PersistentClient(path="/app/chromadb")
collection = chroma.get_or_create_collection("knowledge_base")


@app.route("/health")
def health():
    return jsonify({"status": "ok", "service": "target-rag", "docs": collection.count()})


@app.route("/query", methods=["POST"])
def query():
    data = request.get_json(force=True)
    user_query = data.get("query", "")

    results = collection.query(query_texts=[user_query], n_results=3)
    # VULNERABILITY: retrieved docs injected verbatim — no sanitization of embedded instructions
    context = "\n\n---\n\n".join(results["documents"][0]) if results["documents"] else ""

    system = (
        "You are a knowledge base assistant. Use the retrieved documents to answer queries.\n\n"
        f"Retrieved documents:\n{context}"
    )
    response = llm.respond(system=system, messages=[{"role": "user", "content": user_query}])
    return jsonify({"response": response, "docs_retrieved": len(results["documents"][0])})


# VULNERABILITY: Open write endpoint — no authentication, no content filtering
@app.route("/add_document", methods=["POST"])
def add_document():
    data = request.get_json(force=True)
    doc_id = data.get("id", f"doc_{collection.count()}")
    document = data.get("document", "")
    metadata = data.get("metadata", {})
    collection.add(documents=[document], ids=[doc_id], metadatas=[metadata])
    return jsonify({"status": "added", "id": doc_id, "total": collection.count()})


@app.route("/list_documents")
def list_documents():
    results = collection.get()
    return jsonify({"ids": results["ids"], "count": len(results["ids"])})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)
