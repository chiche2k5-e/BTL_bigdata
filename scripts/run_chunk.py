"""
Script: Chunk processed documents into passage chunks
Usage:
    python scripts/run_chunk.py [--input data/processed] [--output data/chunks] [--config config.yaml]
"""
import argparse
import logging
import sys
import yaml

sys.path.insert(0, ".")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Chunk processed documents")
    parser.add_argument("--input", default="data/processed",
                        help="Input directory of processed Parquet")
    parser.add_argument("--output", default="data/chunks",
                        help="Output directory for chunks Parquet")
    parser.add_argument("--config", default="config.yaml",
                        help="Path to config.yaml")
    args = parser.parse_args()

    logger.info(f"Loading config from {args.config}")
    with open(args.config, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    chunking_cfg = config.get("chunking", {})
    logger.info(f"Starting chunking: input={args.input}, output={args.output}, cfg={chunking_cfg}")

    from src.processing.chunker import build_chunks
    stats = build_chunks(args.input, args.output, chunking_cfg)

    logger.info(f"Chunking complete: {stats}")
    print("\n✅ Chunking complete:")
    print(f"   Documents processed: {stats.get('documents_processed', 0)}")
    print(f"   Total chunks:        {stats.get('total_chunks', 0)}")
    print(f"   Avg chunks/doc:      {stats.get('avg_chunks_per_doc', 0.0):.1f}")


if __name__ == "__main__":
    main()
