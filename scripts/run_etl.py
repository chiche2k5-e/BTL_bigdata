"""
Script: Spark ETL - clean, deduplicate, validate, write Processed Parquet
Usage:
    python scripts/run_etl.py [--input data/parsed] [--output data/processed]
    OR with spark-submit:
    spark-submit scripts/run_etl.py --input data/parsed --output data/processed
"""
import argparse
import logging
import sys

sys.path.insert(0, ".")

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="Spark ETL: Clean & Deduplicate documents")
    parser.add_argument("--input", default="data/parsed",
                        help="Input directory containing parsed JSON files")
    parser.add_argument("--output", default="data/processed",
                        help="Output directory for processed Parquet dataset")
    parser.add_argument("--report", default="data/manifests/etl_report.json",
                        help="Path to save quality report JSON")
    args = parser.parse_args()

    logger.info(f"Starting Spark ETL: input={args.input}, output={args.output}")

    from src.processing.spark_etl import create_spark_session, clean_documents
    spark = create_spark_session()
    try:
        report = clean_documents(spark, args.input, args.output)
        logger.info(f"ETL completed successfully: {report}")
        print("\n✅ Spark ETL complete:")
        print(f"   Input records:    {report.get('total_input', 0)}")
        print(f"   Valid records:    {report.get('valid', 0)}")
        print(f"   Duplicates:       {report.get('duplicates', 0)}")
        print(f"   Empty:            {report.get('empty', 0)}")
        print(f"   Language stats:   {report.get('language_dist', {})}")
    finally:
        spark.stop()


if __name__ == "__main__":
    main()
