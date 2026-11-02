"""
FR05 (partial): Chunking logic. Prioritizes article/clause boundaries.
Owner: Thanh

NOTE: build_index (embedding + Qdrant upsert) nằm ở src/rag/indexer.py

Chiến lược chia đoạn (theo thứ tự ưu tiên):
  1. Điều (Điều 1, Article 1, Section 1, §1, v.v.)
  2. Khoản (1., 2., a., b., i., ii., v.v.)
  3. Đoạn văn (blank line separator)
  4. Câu (sentence split) - chỉ khi đoạn vẫn quá dài
"""
from typing import List
import hashlib
import logging

logger = logging.getLogger(__name__)


def stable_chunk_id(document_id: str, version_id: str, chunk_index: int,
                    text: str) -> str:
    """
    Tạo stable chunk ID dựa trên content hash.
    Cùng input → cùng ID, dùng để idempotent upsert vào Qdrant.

    Args:
        document_id: ID tài liệu
        version_id: Phiên bản tài liệu
        chunk_index: Thứ tự chunk trong tài liệu
        text: Nội dung chunk (lấy 100 ký tự đầu để tránh collide)

    Returns:
        str: 16 ký tự hex (64-bit hash)
    """
    content = f"{document_id}_{version_id}_{chunk_index}_{text[:100]}"
    return hashlib.sha256(content.encode()).hexdigest()[:16]


def chunk_by_article(text: str, document_id: str, version_id: str,
                     metadata: dict, max_tokens: int = 600,
                     overlap_tokens: int = 75) -> List[dict]:
    """
    Chia tài liệu thành chunks, ưu tiên ranh giới điều/khoản.

    Args:
        text: Toàn bộ văn bản đã extract
        document_id: ID tài liệu
        version_id: Phiên bản tài liệu
        metadata: Dict chứa title, source_url, jurisdiction, language,
                  document_type, issued_date, effective_date
        max_tokens: Kích thước tối đa một chunk (tính gần đúng: 1 token ≈ 4 ký tự)
        overlap_tokens: Số token overlap khi split đoạn dài

    Returns:
        List[dict]: Danh sách chunk dicts, mỗi dict khớp với Chunk schema

    Gợi ý implement:
        import re
        # Pattern điều khoản tiếng Việt + tiếng Anh
        article_pattern = re.compile(
            r'(?m)^(Điều\\s+\\d+[\\.:：]|Article\\s+\\d+[\\.:：]|§\\s*\\d+|Section\\s+\\d+)',
            re.IGNORECASE
        )
        # Split theo pattern
        sections = article_pattern.split(text)
        # Với mỗi section, nếu quá dài thì split tiếp theo paragraph
        # Nếu vẫn quá dài thì split theo câu với overlap
    """
    raise NotImplementedError(
        "Thanh implements chunk_by_article()\n"
        "Tham khảo: src/schemas.py → Chunk dataclass cho cấu trúc output"
    )


def build_chunks(processed_parquet_path: str, output_parquet_path: str,
                 config: dict) -> dict:
    """
    Đọc Processed Parquet, chunk toàn bộ tài liệu, ghi Chunks Parquet.

    Args:
        processed_parquet_path: data/processed/ (Parquet)
        output_parquet_path: data/chunks/ (Parquet output)
        config: Dict config từ config.yaml (dùng chunking.target_tokens, v.v.)

    Returns:
        dict: {
            "total_chunks": N,
            "documents_processed": N,
            "avg_chunks_per_doc": float,
            "empty_docs_skipped": N
        }

    Gợi ý implement:
        import pandas as pd
        df = pd.read_parquet(processed_parquet_path)
        all_chunks = []
        for _, row in df.iterrows():
            chunks = chunk_by_article(row["text"], row["document_id"], ...)
            all_chunks.extend(chunks)
        pd.DataFrame(all_chunks).to_parquet(output_parquet_path)
    """
    raise NotImplementedError("Thanh implements build_chunks()")
