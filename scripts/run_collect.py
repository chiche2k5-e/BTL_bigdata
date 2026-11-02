"""
Script: Collect documents from sources.csv
Usage: python scripts/run_collect.py [--sources data/sources.csv] [--output data/raw]
"""
import argparse
import sys
import logging

sys.path.insert(0, ".")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Collect documents from sources.csv")
    parser.add_argument("--sources", default="data/sources.csv",
                        help="Path to sources CSV file")
    parser.add_argument("--output", default="data/raw",
                        help="Output directory for raw files")
    parser.add_argument("--manifest", default="data/manifests/collection_manifest.json",
                        help="Path to write collection manifest JSON")
    parser.add_argument("--delay", type=float, default=1.0,
                        help="Delay between downloads (seconds)")
    args = parser.parse_args()

    logger.info(f"Starting collection: sources={args.sources}, output={args.output}")

    from src.ingestion.collector import collect_sources
    stats = collect_sources(
        sources_csv=args.sources,
        output_dir=args.output,
        manifest_path=args.manifest,
        delay_seconds=args.delay,
    )

    logger.info(f"Collection complete: {stats}")
    print(f"\n✅ Collection complete:")
    print(f"   Total:   {stats.get('total', 0)}")
    print(f"   Success: {stats.get('success', 0)}")
    print(f"   Failed:  {stats.get('failed', 0)}")
    print(f"   Skipped: {stats.get('skipped', 0)}")


if __name__ == "__main__":
    main()
