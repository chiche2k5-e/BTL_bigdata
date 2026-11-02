"""
Script: Embed chunks with BGE-M3 and index into Qdrant
Usage:
    python scripts/run_index.py [--chunks data/chunks] [--collection ai_documents]
"""
import argparse
import logging
import os
import sys
from dotenv import load_dotenv

sys.path.insert(0, ".")
load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Embed chunks and index to Qdrant")
    parser.add_argument("--chunks", default="data/chunks",
                        help="Path to chunks Parquet directory")
    parser.add_argument("--qdrant-url", default=os.getenv("QDRANT_URL", "http://localhost:6333"),
                        help="Qdrant service URL")
    parser.add_argument("--collection", default=os.getenv("QDRANT_COLLECTION", "ai_documents"),
                        help="Qdrant collection name")
    parser.add_argument("--model", default=os.getenv("EMBEDDING_MODEL", "bge-m3"),
                        help="Embedding model tag")
    parser.add_argument("--ollama-url", default=os.getenv("OLLAMA_BASE_URL", "http://localhost:11434"),
                        help="Ollama base URL")
    parser.add_argument("--batch-size", type=int, default=int(os.getenv("EMBED_BATCH_SIZE", "8")),
                        help="Embedding batch size")
    args = parser.parse_args()

    logger.info(f"Starting indexing: chunks={args.chunks}, collection={args.collection}, model={args.model}")

    from src.rag.indexer import build_index
    stats = build_index(
        chunks_parquet_path=args.chunks,
        qdrant_url=args.qdrant_url,
        collection_name=args.collection,
        embedding_model=args.model,
        ollama_url=args.ollama_url,
        batch_size=args.batch_size,
    )

    logger.info(f"Indexing complete: {stats}")
    print("\n✅ Indexing complete:")
    print(f"   Indexed chunks:   {stats.get('total_indexed', 0)}")
    print(f"   Skipped existing: {stats.get('skipped_existing', 0)}")
    print(f"   Model used:       {stats.get('embedding_model', args.model)}")


if __name__ == "__main__":
    main()
