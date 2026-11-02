"""
FR05 (embedding+indexing): Batch embedding with BGE-M3, upsert to Qdrant.
Owner: Thanh

BGE-M3:
  - Output dimension: 1024
  - Hỗ trợ đa ngôn ngữ (vi + en)
  - Chạy qua Ollama API

Qdrant:
  - Collection: ai_documents
  - Distance: Cosine
  - Payload = chunk metadata (để filter và hiển thị kết quả)
"""
from qdrant_client import QdrantClient
from qdrant_client.models import (
    Distance, VectorParams, PointStruct, UpdateStatus
)
import ollama
from typing import List
import logging

logger = logging.getLogger(__name__)

BGE_M3_DIM = 1024  # BGE-M3 fixed output dimension


def get_qdrant_client(url: str) -> QdrantClient:
    """
    Tạo Qdrant client với URL cho trước.

    Args:
        url: URL Qdrant server, e.g. "http://localhost:6333"

    Returns:
        QdrantClient instance
    """
    return QdrantClient(url=url)


def ensure_collection(client: QdrantClient, collection_name: str,
                      vector_size: int = BGE_M3_DIM) -> None:
    """
    Tạo Qdrant collection nếu chưa tồn tại.
    Idempotent: gọi nhiều lần không lỗi.

    Args:
        client: QdrantClient
        collection_name: Tên collection (e.g., "ai_documents")
        vector_size: Số chiều vector (1024 cho BGE-M3)

    Gợi ý implement:
        existing = [c.name for c in client.get_collections().collections]
        if collection_name not in existing:
            client.create_collection(
                collection_name=collection_name,
                vectors_config=VectorParams(size=vector_size, distance=Distance.COSINE)
            )
    """
    raise NotImplementedError("Thanh implements ensure_collection()")


def embed_texts(texts: List[str], model: str = "bge-m3",
                batch_size: int = 8) -> List[List[float]]:
    """
    Batch embed texts dùng Ollama BGE-M3.
    Xử lý theo batch để tránh OOM và timeout.

    Args:
        texts: Danh sách văn bản cần embed
        model: Tên Ollama model (mặc định "bge-m3")
        batch_size: Số text mỗi batch

    Returns:
        List[List[float]]: Danh sách embedding vectors (1024-dim mỗi vector)

    Gợi ý implement:
        from tqdm import tqdm
        all_embeddings = []
        for i in tqdm(range(0, len(texts), batch_size), desc="Embedding"):
            batch = texts[i:i+batch_size]
            for text in batch:
                resp = ollama.embeddings(model=model, prompt=text)
                all_embeddings.append(resp["embedding"])
        return all_embeddings

    Lưu ý: Nếu Ollama hỗ trợ batch embed, dùng ollama.embed() thay vì loop đơn.
    """
    raise NotImplementedError("Thanh implements embed_texts()")


def build_index(chunks_parquet_path: str, qdrant_url: str,
                collection_name: str, embedding_model: str = "bge-m3",
                batch_size: int = 8) -> dict:
    """
    FR05: Đọc Chunks Parquet, embed theo batch, upsert vào Qdrant với stable IDs.
    Idempotent: chạy lại không tạo duplicate.

    Args:
        chunks_parquet_path: data/chunks/ (Parquet)
        qdrant_url: URL Qdrant
        collection_name: Tên collection Qdrant
        embedding_model: Tên Ollama model embedding
        batch_size: Số chunk mỗi batch embed

    Returns:
        dict: {
            "total_indexed": N,
            "skipped_existing": N,
            "embedding_model": str,
            "collection": str,
            "indexed_at": ISO8601
        }

    Gợi ý implement:
        import pandas as pd
        from datetime import datetime, timezone
        df = pd.read_parquet(chunks_parquet_path)
        client = get_qdrant_client(qdrant_url)
        ensure_collection(client, collection_name)

        # Batch process
        for i in range(0, len(df), batch_size):
            batch_df = df.iloc[i:i+batch_size]
            texts = batch_df["text"].tolist()
            embeddings = embed_texts(texts, model=embedding_model, batch_size=batch_size)

            points = []
            for idx, (_, row) in enumerate(batch_df.iterrows()):
                point = PointStruct(
                    id=int(row["chunk_id"][:8], 16),  # convert hex to int ID
                    vector=embeddings[idx],
                    payload={
                        "chunk_id": row["chunk_id"],
                        "document_id": row["document_id"],
                        "title": row["title"],
                        "text": row["text"],
                        "source_url": row["source_url"],
                        "jurisdiction": row["jurisdiction"],
                        "language": row["language"],
                        "document_type": row["document_type"],
                        "article": row.get("article"),
                        "section": row.get("section"),
                        "chunk_index": int(row["chunk_index"]),
                    }
                )
                points.append(point)

            client.upsert(collection_name=collection_name, points=points)
    """
    raise NotImplementedError("Thanh implements build_index()")
