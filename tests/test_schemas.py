"""Tests for shared schemas in src/schemas.py"""
import pytest
from src.schemas import (
    DocumentType,
    ParseStatus,
    AnswerStatus,
    RawDocument,
    ProcessedDocument,
    Chunk,
    Citation,
    AnswerResult,
)


def test_document_type_values():
    assert DocumentType.LAW == "law"
    assert DocumentType.REGULATION == "regulation"
    assert DocumentType.POLICY == "policy"
    assert DocumentType.GUIDELINE == "guideline"
    assert DocumentType.FRAMEWORK == "framework"


def test_parse_status_values():
    assert ParseStatus.SUCCESS == "success"
    assert ParseStatus.FAILED == "failed"
    assert ParseStatus.EMPTY == "empty"
    assert ParseStatus.SCAN_DETECTED == "scan_detected"


def test_answer_status_values():
    assert AnswerStatus.ANSWERED == "answered"
    assert AnswerStatus.INSUFFICIENT_EVIDENCE == "insufficient_evidence"
    assert AnswerStatus.ERROR == "error"


def test_chunk_required_fields():
    chunk = Chunk(
        chunk_id="abc123",
        document_id="eu_ai_act_2024_1689",
        version_id="v1",
        title="EU AI Act",
        text="Article 1: Subject matter...",
        source_url="https://eur-lex.europa.eu/eli/reg/2024/1689",
        jurisdiction="EU",
        language="en",
        document_type=DocumentType.REGULATION,
    )
    assert chunk.chunk_id == "abc123"
    assert chunk.document_type == DocumentType.REGULATION
    assert chunk.article is None
    assert chunk.chunk_index == 0


def test_answer_result_defaults():
    result = AnswerResult(status=AnswerStatus.INSUFFICIENT_EVIDENCE)
    assert result.citations == []
    assert result.answer is None
    assert result.timings == {}
    assert result.error_message is None


def test_citation_required_fields():
    c = Citation(
        source_id="S1",
        chunk_id="abc123",
        document_id="eu_ai_act_2024_1689",
        title="EU AI Act",
        excerpt="Article 5 — Prohibited AI...",
    )
    assert c.source_id == "S1"
    assert c.location is None
    assert c.source_url is None
