"""
FR04: Spark-based cleaning, deduplication, and quality reporting.
Owner: Thanh

ETL pipeline chạy trên PySpark:
  1. Đọc parsed JSON records từ data/parsed/
  2. Chuẩn hóa Unicode (NFC), loại bỏ ký tự rác
  3. Deduplication theo content_hash (SHA-256)
  4. Validate metadata bắt buộc
  5. Ghi Processed Parquet ra data/processed/
  6. Tạo quality report
"""
from pyspark.sql import SparkSession, DataFrame
from pyspark.sql import functions as F
from pyspark.sql.types import (
    StructType, StructField, StringType, IntegerType, BooleanType
)
import logging

logger = logging.getLogger(__name__)

# Schema cho parsed records đọc từ data/parsed/
PARSED_SCHEMA = StructType([
    StructField("document_id", StringType(), False),
    StructField("version_id", StringType(), True),
    StructField("title", StringType(), True),
    StructField("text", StringType(), True),
    StructField("document_type", StringType(), True),
    StructField("source_url", StringType(), True),
    StructField("raw_path", StringType(), True),
    StructField("jurisdiction", StringType(), True),
    StructField("language", StringType(), True),
    StructField("content_hash", StringType(), True),
    StructField("parse_status", StringType(), True),
    StructField("article", StringType(), True),
    StructField("section", StringType(), True),
    StructField("page_start", IntegerType(), True),
    StructField("page_end", IntegerType(), True),
    StructField("issued_date", StringType(), True),
    StructField("effective_date", StringType(), True),
])


def create_spark_session(app_name: str = "AI_Docs_ETL") -> SparkSession:
    """
    Tạo SparkSession với cấu hình tối ưu cho Parquet.

    Gợi ý implement:
        return (SparkSession.builder
            .appName(app_name)
            .config("spark.sql.parquet.compression.codec", "snappy")
            .config("spark.sql.shuffle.partitions", "4")   # nhỏ cho local
            .getOrCreate())
    """
    raise NotImplementedError("Thanh implements create_spark_session()")


def clean_documents(spark: SparkSession, raw_records_path: str,
                    output_path: str) -> dict:
    """
    FR04: Đọc parser output, normalize Unicode, remove duplicates theo hash,
    validate metadata, ghi Processed Parquet.

    Args:
        spark: SparkSession đang chạy
        raw_records_path: Thư mục chứa JSON records từ bước parse
                          (mỗi file JSON là một document)
        output_path: Thư mục output Parquet (data/processed/)

    Returns:
        quality_report (dict): {
            "total_input": N,
            "valid": N,
            "duplicates": N,
            "empty": N,
            "failed_parse": N,
            "language_dist": {"vi": N, "en": N},
            "jurisdiction_dist": {"VN": N, "EU": N, ...},
            "doc_type_dist": {"law": N, "regulation": N, ...}
        }

    Gợi ý implement:
        1. df = spark.read.json(raw_records_path, schema=PARSED_SCHEMA)
        2. df = df.withColumn("text_norm", F.regexp_replace("text", r"[\\x00-\\x08\\x0b\\x0c\\x0e-\\x1f]", " "))
        3. df_dedup = df.dropDuplicates(["content_hash"])
        4. df_valid = df_dedup.filter(F.length("text") > 100)
        5. df_valid.write.parquet(output_path, mode="overwrite")
        6. return compute_quality_stats(df) với các counts
    """
    raise NotImplementedError("Thanh implements clean_documents()")


def compute_quality_stats(df: DataFrame) -> dict:
    """
    Tính và trả về thống kê chất lượng dataset.

    Args:
        df: Spark DataFrame (sau khi đã load, trước khi filter)

    Returns:
        dict với các thống kê: total, language_dist, jurisdiction_dist, v.v.

    Gợi ý:
        total = df.count()
        lang_dist = df.groupBy("language").count().collect()
        ...
    """
    raise NotImplementedError("Thanh implements compute_quality_stats()")
