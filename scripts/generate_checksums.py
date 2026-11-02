"""
Generate SHA-256 checksums and file size for files in data/bronze/
Updates international_documents.csv and vietnam_documents.csv in place.
Usage:
    python scripts/generate_checksums.py
"""
import csv
import hashlib
import sys
from pathlib import Path

# Ensure stdout supports UTF-8 on Windows
if sys.platform == "win32":
    sys.stdout.reconfigure(encoding="utf-8")


def sha256_file(path: str) -> str:
    sha256 = hashlib.sha256()
    with open(path, "rb") as f:
        for block in iter(lambda: f.read(8192), b""):
            sha256.update(block)
    return sha256.hexdigest()


def update_csv_checksums(csv_path: str):
    p = Path(csv_path)
    if not p.exists():
        print(f"[WARN] CSV not found: {csv_path}")
        return

    rows = []
    updated_count = 0
    missing_count = 0

    with open(p, newline="", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        fieldnames = reader.fieldnames
        for row in reader:
            file_path = row.get("file_path", "").strip()
            if file_path and Path(file_path).exists():
                file_obj = Path(file_path)
                row["checksum_sha256"] = sha256_file(file_path)
                row["file_size_bytes"] = str(file_obj.stat().st_size)
                updated_count += 1
                print(f"  [OK] {file_path} -> {row['checksum_sha256'][:12]}... ({row['file_size_bytes']} bytes)")
            else:
                missing_count += 1
                print(f"  [MISSING] {file_path}")
            rows.append(row)

    with open(p, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)

    print(f"[DONE] Updated {csv_path}: {updated_count} files verified, {missing_count} missing.\n")


def main():
    print("Computing SHA-256 Checksums for Bronze Layer...")
    csv_files = [
        "data/bronze/metadata/vietnam_documents.csv",
        "data/bronze/metadata/international_documents.csv",
    ]
    for c in csv_files:
        update_csv_checksums(c)


if __name__ == "__main__":
    main()
