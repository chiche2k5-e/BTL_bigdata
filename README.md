# 📚 Hệ thống Tra cứu và Hỏi đáp Văn bản AI (Data Lake + RAG)

> **Môn học:** Big Data  
> **Nhóm:** Trang (nhóm trưởng) · Chi · Thanh  
> **Stack:** Python 3.10+ · HDFS · PySpark · BGE-M3 · Qwen3 · Qdrant · Streamlit

---

## Giới thiệu dự án

Hệ thống hỗ trợ tra cứu và hỏi đáp các văn bản pháp lý, chính sách về **Trí tuệ nhân tạo** từ nhiều khu vực (Việt Nam, EU, Quốc tế, ASEAN). Kiến trúc gồm hai phần chính:

1. **Data Lake Pipeline** (HDFS + PySpark): Thu thập → Phân tích → Làm sạch → Chia đoạn văn bản.
2. **RAG Q&A** (BGE-M3 + Qdrant + Qwen3): Nhúng vector → Truy xuất ngữ nghĩa → Sinh câu trả lời có trích dẫn.

```
Nguồn (CSV) → Collector → Parser → Spark ETL → Chunker → Embedder → Qdrant
                                                                         ↓
                                                         Streamlit App ← Retriever + LLM
```

---

## Yêu cầu hệ thống

| Thành phần | Phiên bản tối thiểu | Ghi chú |
|---|---|---|
| Python | 3.10+ | Khuyến nghị 3.11 |
| Java | 11+ | Cần cho PySpark/Hadoop |
| Apache Hadoop (HDFS) | 3.3+ | Chạy local hoặc cluster |
| Ollama | 0.4+ | Để chạy BGE-M3 và Qwen3 |
| Qdrant | 1.7+ | Vector database |
| RAM | 16 GB+ | Qwen3:4B cần ~6 GB VRAM hoặc RAM |
| Disk | 20 GB+ | Cho dữ liệu và models |

---

## Cài đặt

### 1. Clone repo

```bash
git clone <repo-url>
cd BTL_bigdata
```

### 2. Tạo virtual environment

```bash
python -m venv .venv

# Windows
.venv\Scripts\activate

# Linux / macOS
source .venv/bin/activate
```

### 3. Cài đặt dependencies

```bash
pip install -r requirements.txt
```

### 4. Cấu hình biến môi trường

```bash
cp .env.example .env
# Chỉnh sửa .env theo môi trường của bạn
```

Các biến quan trọng trong `.env`:

| Biến | Giá trị mặc định | Mô tả |
|---|---|---|
| `HDFS_NAMENODE_URL` | `hdfs://localhost:9000` | URL HDFS namenode |
| `QDRANT_URL` | `http://localhost:6333` | URL Qdrant server |
| `OLLAMA_BASE_URL` | `http://localhost:11434` | URL Ollama API |
| `EMBEDDING_MODEL` | `bge-m3` | Model nhúng vector |
| `CHAT_MODEL` | `qwen3:4b` | Model sinh câu trả lời |

### 5. Tải models Ollama

```bash
# Tải model embedding (BGE-M3 ~1.2 GB)
ollama pull bge-m3

# Tải model chat (Qwen3 4B ~2.6 GB)
ollama pull qwen3:4b

# Kiểm tra
ollama list
```

### 6. Khởi động Qdrant (Docker)

```bash
docker run -d --name qdrant -p 6333:6333 -p 6334:6334 \
  -v $(pwd)/qdrant_storage:/qdrant/storage \
  qdrant/qdrant
```

Hoặc tải binary tại https://qdrant.tech/documentation/quick-start/

---

## Chạy pipeline

### Bước 1: Thu thập tài liệu

```bash
python scripts/run_collect.py --sources data/sources.csv --output data/raw
```

### Bước 2: Phân tích văn bản (extract text)

```bash
python scripts/run_parse.py --raw data/raw --output data/parsed
```

### Bước 3: Spark ETL (làm sạch + deduplicate)

```bash
# Chạy local
python scripts/run_etl.py --input data/parsed --output data/processed

# Hoặc submit Spark job
spark-submit scripts/run_etl.py --input data/parsed --output data/processed
```

### Bước 4: Chia đoạn văn bản (chunking)

```bash
python scripts/run_chunk.py --input data/processed --output data/chunks
```

### Bước 5: Nhúng vector và index vào Qdrant

```bash
python scripts/run_index.py --chunks data/chunks
```

### Chạy toàn bộ pipeline (tất cả bước)

```bash
python scripts/run_pipeline.py --step all
```

### Chạy từng bước riêng lẻ

```bash
python scripts/run_pipeline.py --step collect
python scripts/run_pipeline.py --step parse
python scripts/run_pipeline.py --step etl
python scripts/run_pipeline.py --step chunk
python scripts/run_pipeline.py --step index
```

---

## Chạy ứng dụng Streamlit

```bash
streamlit run app.py
```

Truy cập: http://localhost:8501

**Tính năng:**
- 🔍 **Tra cứu**: Tìm kiếm ngữ nghĩa trong corpus văn bản AI
- 💬 **Hỏi đáp**: Đặt câu hỏi, nhận câu trả lời có trích dẫn từ văn bản gốc
- Lọc theo khu vực (VN, EU, International, ASEAN)
- Lọc theo tên/ID văn bản cụ thể

---

## Cấu trúc thư mục

```
BTL_bigdata/
├── app.py                          # Streamlit UI (Trang)
├── config.yaml                     # Cấu hình toàn hệ thống
├── requirements.txt                # Python dependencies
├── .env.example                    # Template biến môi trường
├── .gitignore
├── README.md
│
├── src/                            # Source code chính
│   ├── schemas.py                  # ⭐ Shared data schemas (contract)
│   ├── ingestion/                  # Module của Chi
│   │   ├── collector.py            # FR01+FR02: Thu thập tài liệu
│   │   ├── parser.py               # FR03: Trích xuất văn bản
│   │   └── manifest.py             # Quản lý manifest
│   ├── processing/                 # Module của Thanh
│   │   ├── spark_etl.py            # FR04: Spark ETL
│   │   └── chunker.py              # FR05: Chia đoạn văn bản
│   └── rag/                        # Module của Thanh
│       ├── indexer.py              # FR05: Embedding + Qdrant
│       ├── retriever.py            # FR06: Truy xuất ngữ nghĩa
│       └── answerer.py             # FR07-09: Sinh câu trả lời
│
├── scripts/                        # Pipeline scripts
│   ├── run_collect.py
│   ├── run_parse.py
│   ├── run_etl.py
│   ├── run_chunk.py
│   ├── run_index.py
│   ├── run_pipeline.py             # Full pipeline
│   └── generate_checksums.py
│
├── data/
│   ├── sources.csv                 # ⭐ Danh sách nguồn tài liệu
│   ├── bronze/                     # Tài liệu gốc đã tải
│   │   ├── metadata/
│   │   │   ├── international_documents.csv
│   │   │   └── vietnam_documents.csv
│   │   ├── international/          # EU, NIST, OECD, UNESCO...
│   │   ├── vietnam/                # Văn bản pháp luật VN
│   │   └── supplementary/         # ASEAN, nghiên cứu khác
│   ├── raw/                        # Raw downloads (gitignored)
│   ├── parsed/                     # Parsed text records (gitignored)
│   ├── processed/                  # Parquet sau ETL (gitignored)
│   ├── chunks/                     # Chunk Parquet (gitignored)
│   └── manifests/                  # Pipeline manifests
│
├── tests/
│   ├── test_schemas.py             # Unit tests schemas
│   └── test_integration.py        # Integration tests TC01-TC09
│
├── evaluation/
│   ├── qa_eval_set.csv             # 30 câu hỏi kiểm thử
│   └── eval_runner.py             # Script chạy evaluation
│
└── docs/
    └── PRD_Data_Lake_RAG_AI.docx  # Product Requirements Document
```

---

## Kiểm thử

```bash
# Chạy unit tests
pytest tests/test_schemas.py -v

# Chạy integration tests (cần pipeline chạy trước)
pytest tests/test_integration.py -v -m integration

# Chạy tất cả
pytest tests/ -v
```

---

## Đánh giá chất lượng

```bash
python evaluation/eval_runner.py
# Kết quả lưu tại evaluation/eval_results.json
```

Chỉ số đánh giá:
- **Hit@5**: Chunk đúng có trong top 5 kết quả truy xuất
- **Answered correctly**: Câu trả lời đúng khi có đủ căn cứ
- **Insufficient evidence**: Nhận dạng đúng câu hỏi ngoài corpus

---

## Xử lý lỗi thường gặp

### ❌ `JAVA_HOME not set` hoặc PySpark lỗi

```bash
# Windows - thêm vào .env
JAVA_HOME=C:\Program Files\Java\jdk-11

# Linux/macOS
export JAVA_HOME=/usr/lib/jvm/java-11-openjdk
```

### ❌ Ollama không kết nối được

```bash
# Kiểm tra Ollama đang chạy
ollama serve

# Kiểm tra models đã pull
ollama list
```

### ❌ Qdrant connection refused

```bash
# Khởi động lại Qdrant Docker
docker start qdrant

# Hoặc chạy lại
docker run -d -p 6333:6333 qdrant/qdrant
```

### ❌ PDF scan không extract được text

- File PDF là ảnh scan → parser sẽ đánh dấu `parse_status=scan_detected`
- Cần OCR (không nằm trong scope hiện tại)
- Bỏ qua các file này trong pipeline, log lại để xử lý thủ công

### ❌ Memory error khi chạy PySpark

```bash
# Điều chỉnh trong config.yaml hoặc spark-submit
--driver-memory 4g --executor-memory 4g
```

### ❌ Qwen3 trả lời quá chậm

- Dùng `qwen3:4b` thay vì model lớn hơn
- Tăng `REQUEST_TIMEOUT` trong `.env`
- Đảm bảo Ollama dùng GPU nếu có

---

## Phân công công việc

| Module | Thành viên | Chức năng |
|---|---|---|
| `src/ingestion/` | **Chi** | Thu thập + phân tích văn bản |
| `src/processing/` + `src/rag/` | **Thanh** | ETL, Chunking, RAG pipeline |
| `app.py` | **Trang** | Streamlit UI, tích hợp |

---

## Liên hệ & Đóng góp

Mọi thay đổi schema trong `src/schemas.py` **phải thông báo cho toàn nhóm** vì đây là contract chung giữa các module.
