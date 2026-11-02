"""
Script: Parse raw documents to text records (JSON).
Usage: python scripts/run_parse.py [--raw data/raw] [--output data/parsed]

Đọc từng file trong data/raw/, gọi parse_document() tương ứng,
ghi kết quả JSON ra data/parsed/.
"""
import argparse
import sys
import logging
import json
from pathlib import Path

sys.path.insert(0, ".")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

# File format mapping
FORMAT_MAP = {
    ".pdf": "pdf",
    ".html": "html",
    ".htm": "html",
    ".docx": "docx",
}


def main():
    parser = argparse.ArgumentParser(description="Parse raw documents to text records")
    parser.add_argument("--raw", default="data/raw",
                        help="Input directory with raw files")
    parser.add_argument("--output", default="data/parsed",
                        help="Output directory for parsed JSON records")
    args = parser.parse_args()

    raw_dir = Path(args.raw)
    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    logger.info(f"Parsing from {raw_dir} → {out_dir}")

    from src.ingestion.parser import parse_document

    success, failed, skipped = 0, 0, 0

    for file_path in sorted(raw_dir.rglob("*")):
        if not file_path.is_file():
            continue
        suffix = file_path.suffix.lower()
        fmt = FORMAT_MAP.get(suffix)
        if not fmt:
            logger.debug(f"Skipping unknown format: {file_path}")
            skipped += 1
            continue

        out_file = out_dir / (file_path.stem + ".json")
        if out_file.exists():
            logger.info(f"Already parsed (skip): {file_path.name}")
            skipped += 1
            continue

        logger.info(f"Parsing: {file_path.name}")
        try:
            result = parse_document(
                raw_path=str(file_path),
                file_format=fmt,
                source_url="",   # Filled from manifest if available
            )
            result["source_file"] = str(file_path)
            with open(out_file, "w", encoding="utf-8") as f:
                json.dump(result, f, ensure_ascii=False, indent=2)
            success += 1
        except NotImplementedError:
            logger.error("parse_document() not yet implemented - Chi cần hoàn thiện src/ingestion/parser.py")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to parse {file_path.name}: {e}")
            failed += 1

    print(f"\n✅ Parsing complete:")
    print(f"   Success: {success}")
    print(f"   Failed:  {failed}")
    print(f"   Skipped: {skipped}")


if __name__ == "__main__":
    main()
