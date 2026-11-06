from __future__ import annotations

from typing import Any

try:
    from mcp.server.fastmcp import FastMCP
except Exception:  # pragma: no cover
    class FastMCP:  # type: ignore[no-redef]
        def __init__(self, name: str):
            self.name = name
            self.tools = {}
            self.resources = {}

        def tool(self, *args, **kwargs):
            def decorator(fn):
                self.tools[fn.__name__] = fn
                return fn
            return decorator

        def resource(self, *args, **kwargs):
            def decorator(fn):
                self.resources[fn.__name__] = fn
                return fn
            return decorator

from uhg_capstone.models import Document
from uhg_capstone.security import detect_prompt_injection, redact_pii
from uhg_capstone.store import build_seed_store

store = build_seed_store()
server = FastMCP("documents-mcp")


@server.tool()
def list_documents(case_id: str) -> dict[str, Any]:
    case = store.get_case(case_id)
    if not case:
        return {"ok": False, "error": "Case not found"}
    return {"ok": True, "documents": [{"document_id": doc.document_id, "doc_type": doc.doc_type, "status": doc.status} for doc in case.documents]}


@server.tool()
def extract_text(case_id: str, document_id: str) -> dict[str, Any]:
    case = store.get_case(case_id)
    if not case:
        return {"ok": False, "error": "Case not found"}
    for doc in case.documents:
        if doc.document_id == document_id:
            sanitized = redact_pii(doc.text)
            return {"ok": True, "text": sanitized, "ocr_confidence": doc.ocr_confidence, "prompt_injection": detect_prompt_injection(doc.text)}
    return {"ok": False, "error": "Document not found"}


@server.tool()
def classify_document(case_id: str, document_id: str) -> dict[str, Any]:
    case = store.get_case(case_id)
    if not case:
        return {"ok": False, "error": "Case not found"}
    for doc in case.documents:
        if doc.document_id == document_id:
            prompt_injection = detect_prompt_injection(doc.text)
            if prompt_injection:
                doc.prompt_injection = True
                doc.validation_warnings.append("Prompt injection detected.")
            return {"ok": True, "document_type": doc.doc_type, "confidence": doc.classification_confidence, "prompt_injection": prompt_injection}
    return {"ok": False, "error": "Document not found"}


@server.tool()
def extract_fields(case_id: str, document_id: str) -> dict[str, Any]:
    case = store.get_case(case_id)
    if not case:
        return {"ok": False, "error": "Case not found"}
    for doc in case.documents:
        if doc.document_id == document_id:
            return {"ok": True, "fields": doc.extracted_fields}
    return {"ok": False, "error": "Document not found"}


@server.tool()
def validate_case_documents(case_id: str) -> dict[str, Any]:
    case = store.get_case(case_id)
    if not case:
        return {"ok": False, "error": "Case not found"}
    issues = []
    for doc in case.documents:
        trigger = detect_prompt_injection(doc.text)
        doc.prompt_injection = trigger or doc.prompt_injection
        if doc.prompt_injection:
            issues.append(f"Document {doc.document_id} contains a prompt injection")
        if doc.ocr_confidence < 0.7:
            issues.append(f"Document {doc.document_id} has low OCR confidence")
    return {"ok": True, "valid": not issues, "issues": issues}


@server.resource("document://{case_id}/{doc_id}")
def document_resource(case_id: str, doc_id: str) -> str:
    case = store.get_case(case_id)
    if not case:
        return "Case not found"
    for doc in case.documents:
        if doc.document_id == doc_id:
            return f"Document {doc.document_id}: type={doc.doc_type}, status={doc.status}, text={doc.text[:180]}"
    return "Document not found"
