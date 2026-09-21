from pathlib import Path

from ticket_assistant.retriever import load_document_chunks

def test_chunks_have_source_metadata():
    chunks = load_document_chunks()
    assert len(chunks) > 0
    assert all("source" in c.metadata for c in chunks)