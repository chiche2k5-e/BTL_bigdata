"""
FR01 + FR02: Source management and document collection.
Owner: Chi

Thu thập tài liệu từ sources.csv, tải về local/HDFS, ghi manifest.
"""
import hashlib
import csv
import json
import requests
import time
from pathlib import Path
from datetime import datetime, timezone
from typing import Optional
import logging

logger = logging.getLogger(__name__)


def sha256_file(path: Path) -> str:
    """Tính SHA-256 checksum cho file."""
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            sha256.update(block)
    return sha256.hexdigest()


def _download_file(url: str, dest_path: Path, timeout: int = 60,
                   max_retries: int = 3) -> bool:
    """
    Tải file từ URL về dest_path. Retry tối đa max_retries lần.
    Returns True nếu thành công.
    """
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Tải [{attempt}/{max_retries}]: {url}")
            response = requests.get(url, timeout=timeout, stream=True,
                                    headers={"User-Agent": "BTL-BigData-Collector/1.0"})
            response.raise_for_status()
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            with open(dest_path, "wb") as f:
                for chunk in response.iter_content(chunk_size=8192):
                    f.write(chunk)
            logger.info(f"Đã tải: {dest_path} ({dest_path.stat().st_size} bytes)")
            return True
        except Exception as e:
            logger.warning(f"Lỗi lần {attempt}: {e}")
            if attempt < max_retries:
                time.sleep(2 ** attempt)
    logger.error(f"Thất bại sau {max_retries} lần: {url}")
    return False


def collect_sources(sources_csv: str, output_dir: str, manifest_path: str,
                    delay_seconds: float = 1.0) -> dict:
    """
    FR01 + FR02: Đọc sources.csv, tải từng tài liệu về output_dir.
    Ghi manifest JSON tổng kết quá trình thu thập.

    Args:
        sources_csv: Đường dẫn tới data/sources.csv
        output_dir: Thư mục đích (HDFS hoặc local)
        manifest_path: Nơi ghi file manifest JSON
        delay_seconds: Thời gian nghỉ giữa các request (lịch sự với server)

    Returns:
        dict: {"total": N, "success": N, "failed": N, "skipped": N, "files": [...]}
    """
    raise NotImplementedError(
        "Chi implements this in src/ingestion/collector.py\n"
        "Gợi ý:\n"
        "  1. Đọc sources_csv bằng csv.DictReader\n"
        "  2. Với mỗi hàng có file_url, gọi _download_file()\n"
        "  3. Tính content_hash với sha256_file()\n"
        "  4. Skip nếu file đã tồn tại và hash khớp (idempotent)\n"
        "  5. Ghi manifest JSON với write_collection_manifest()\n"
        "  6. Trả về dict stats"
    )
