"""
Manifest management for collection and indexing snapshots.
Owner: Chi (collection manifest) / Thanh (ETL + index manifest)

Manifest là file JSON ghi lại kết quả mỗi bước pipeline,
dùng để debug, audit, và idempotency check.
"""
import json
from pathlib import Path
from datetime import datetime, timezone
from typing import List, Dict


def write_collection_manifest(output_path: str, stats: dict) -> None:
    """
    Ghi manifest JSON cho bước collection.

    Args:
        output_path: Đường dẫn file manifest (e.g., data/manifests/collection_manifest.json)
        stats: Dict chứa thống kê thu thập:
               {"total": N, "success": N, "failed": N, "skipped": N,
                "collected_at": ISO8601, "files": [...]}

    Example output file:
        {
            "total": 15,
            "success": 13,
            "failed": 1,
            "skipped": 1,
            "collected_at": "2025-01-01T00:00:00Z",
            "pipeline_version": "1.0.0",
            "files": [
                {"document_id": "eu_ai_act_2024_1689", "path": "data/raw/...", "status": "success", ...}
            ]
        }
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    stats.setdefault("written_at", datetime.now(timezone.utc).isoformat())
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(stats, f, indent=2, ensure_ascii=False)


def write_etl_manifest(output_path: str, quality_report: dict) -> None:
    """
    Ghi manifest JSON cho bước ETL.

    Args:
        output_path: Đường dẫn file manifest ETL
        quality_report: Kết quả từ compute_quality_stats()
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    quality_report.setdefault("written_at", datetime.now(timezone.utc).isoformat())
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(quality_report, f, indent=2, ensure_ascii=False)


def write_index_manifest(output_path: str, index_stats: dict) -> None:
    """
    Ghi manifest JSON cho bước indexing (embedding + Qdrant upsert).

    Args:
        output_path: Đường dẫn file manifest index
        index_stats: {"total_indexed": N, "skipped_existing": N, "embedding_model": str, ...}
    """
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)
    index_stats.setdefault("written_at", datetime.now(timezone.utc).isoformat())
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(index_stats, f, indent=2, ensure_ascii=False)


def read_manifest(manifest_path: str) -> dict:
    """
    Đọc manifest JSON từ file.

    Args:
        manifest_path: Đường dẫn file manifest

    Returns:
        dict: Nội dung manifest, hoặc {} nếu file không tồn tại
    """
    path = Path(manifest_path)
    if not path.exists():
        return {}
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def get_collected_document_ids(manifest_path: str) -> set:
    """
    Lấy tập hợp document_id đã thu thập thành công từ manifest.
    Dùng để skip khi chạy lại pipeline (idempotency).
    """
    manifest = read_manifest(manifest_path)
    return {
        f["document_id"]
        for f in manifest.get("files", [])
        if f.get("status") == "success"
    }
