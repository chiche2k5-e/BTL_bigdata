"""
FR06: Semantic retrieval from Qdrant with optional filters.
Owner: Thanh

Embed query với BGE-M3, search Qdrant, áp dụng filter jurisdiction/document_id.
Trả về list chunk dicts với score để hiển thị và generate answer.
"""
from qdrant_client import QdrantClient
from qdrant_client.models import Filter, FieldCondition, MatchValue
from typing import List, Optional
import ollama
import logging

logger = logging.getLogger(__name__)


def _build_filter(jurisdiction: Optional[str] = None,
                  document_id: Optional[str] = None) -> Optional[Filter]:
    """
    Xây dựng Qdrant Filter từ các tham số lọc.

    Args:
        jurisdiction: "VN" | "EU" | "International" | "ASEAN" | None (không lọc)
        document_id: ID văn bản cụ thể | None

    Returns:
        Filter object hoặc None nếu không có filter
    """
    conditions = []
    if jurisdiction and jurisdiction.lower() != "tất cả":
        conditions.append(
            FieldCondition(key="jurisdiction", match=MatchValue(value=jurisdiction))
        )
    if document_id and document_id.strip():
        conditions.append(
            FieldCondition(key="document_id", match=MatchValue(value=document_id.strip()))
        )
    if not conditions:
        return None
    return Filter(must=conditions)


def retrieve(query: str, qdrant_url: str, collection_name: str,
             embedding_model: str = "bge-m3", top_k: int = 5,
             jurisdiction_filter: Optional[str] = None,
             document_id_filter: Optional[str] = None) -> List[dict]:
    """
    FR06: Embed query, search Qdrant, áp dụng filters.

    Args:
        query: Câu hỏi của người dùng
        qdrant_url: URL Qdrant server
        collection_name: Tên collection
        embedding_model: Ollama model dùng để embed query
        top_k: Số kết quả trả về
        jurisdiction_filter: Lọc theo khu vực (VN/EU/International/ASEAN)
        document_id_filter: Lọc theo document_id cụ thể

    Returns:
        List[dict]: Danh sách chunk dicts, mỗi chunk có:
            {
                "chunk_id": str,
                "document_id": str,
                "title": str,
                "text": str,
                "source_url": str,
                "jurisdiction": str,
                "language": str,
                "document_type": str,
                "article": str | None,
                "section": str | None,
                "chunk_index": int,
                "score": float          # Cosine similarity score
            }

    Gợi ý implement:
        from src.rag.indexer import get_qdrant_client
        client = get_qdrant_client(qdrant_url)

        # Embed query
        query_resp = ollama.embeddings(model=embedding_model, prompt=query)
        query_vector = query_resp["embedding"]

        # Build filter
        search_filter = _build_filter(jurisdiction_filter, document_id_filter)

        # Search
        results = client.search(
            collection_name=collection_name,
            query_vector=query_vector,
            limit=top_k,
            query_filter=search_filter,
            with_payload=True,
        )

        return [
            {**hit.payload, "score": hit.score}
            for hit in results
        ]
    """
    raise NotImplementedError("Thanh implements retrieve()")
