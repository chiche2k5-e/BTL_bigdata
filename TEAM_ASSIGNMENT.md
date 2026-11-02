# 📋 Phân Công Công Việc — BTL Big Data: AI Doc RAG

> **Nhóm trưởng:** Nguyễn Thị Thu Trang (Trang)  
> **Thành viên 2:** Chi  
> **Thành viên 3:** Thanh (THTH)  
> **Repo:** https://github.com/trangtretrau2005/BTL_bigdata  
> **Cập nhật:** 02/11/2026

---

## 🗺️ Kiến trúc phân công theo luồng dữ liệu

```
[sources.csv] → [collector.py] → [data/raw/] → [parser.py] → [data/parsed/]
   ↑ CHI            ↑ CHI            ↑ CHI         ↑ CHI          ↑ CHI

[data/parsed/] → [spark_etl.py] → [data/processed/] → [chunker.py] → [data/chunks/]
                   ↑ THANH              ↑ THANH           ↑ THANH        ↑ THANH

[data/chunks/] → [indexer.py] → [Qdrant] → [retriever.py] → [answerer.py]
                  ↑ THANH                     ↑ THANH           ↑ THANH

[app.py Streamlit] — kết nối tất cả — ↑ TRANG
[src/schemas.py] — contract dùng chung — ↑ TRANG (chỉ TRANG merge)
```

---

## 🔵 CHI — Module: Ingestion (Thu thập & Phân tích tài liệu)

### Nhánh Git riêng
```bash
git checkout -b feature/chi/ingestion
```

### Files CHI sở hữu (chỉ CHI commit vào đây)

| File | Mô tả |
|------|-------|
| `src/ingestion/collector.py` | Download tài liệu từ sources.csv (FR01, FR02) |
| `src/ingestion/parser.py` | Parse HTML, PDF, DOCX → text có cấu trúc (FR03) |
| `src/ingestion/manifest.py` | Ghi/đọc collection manifest |
| `scripts/run_collect.py` | Script chạy collector |
| `scripts/run_parse.py` | Script chạy parser |
| `data/bronze/international/**` | 15 tài liệu quốc tế (PDF) |
| `data/bronze/metadata/international_documents.csv` | Metadata catalog quốc tế |

### Danh sách 15 tài liệu quốc tế cần tải

| # | Tài liệu | Nơi lưu |
|---|----------|---------|
| 1 | EU AI Act Regulation (EU) 2024/1689 (consolidated) | `data/bronze/international/eu/` |
| 2 | EU AI Act — Annexes | `data/bronze/international/eu/` |
| 3 | NIST AI RMF 1.0 | `data/bronze/international/nist/` |
| 4 | NIST AI RMF Playbook | `data/bronze/international/nist/` |
| 5 | NIST Generative AI Profile | `data/bronze/international/nist/` |
| 6 | OECD Recommendation on AI | `data/bronze/international/oecd/` |
| 7 | OECD AI Principles explanatory doc | `data/bronze/international/oecd/` |
| 8 | UNESCO Recommendation on the Ethics of AI | `data/bronze/international/unesco/` |
| 9 | UNESCO AI ethics guidance doc | `data/bronze/international/unesco/` |
| 10 | Council of Europe Framework Convention on AI | `data/bronze/international/other/` |
| 11 | Singapore Model AI Governance Framework | `data/bronze/international/other/` |
| 12 | UK AI governance / AI Safety Institute doc | `data/bronze/international/other/` |
| 13 | US Executive Order về AI | `data/bronze/international/other/` |
| 14 | ISO/IEC 42001 overview | `data/bronze/international/other/` |
| 15 | Một tài liệu AI governance từ Canada/Nhật/Hàn/Úc | `data/bronze/international/other/` |

**Tên file convention:** `{nguồn}_{tên_ngắn}_{số_hiệu}_{ngày}.{pdf|html|docx}`  
Ví dụ: `eu_ai_act_2024_1689_consolidated_2026-07-27.pdf`

### Tasks theo mốc

**M1 — Chốt đầu vào:**
- [ ] Tải đủ 15 tài liệu, đúng thư mục
- [ ] Điền `international_documents.csv` (19 cột đầy đủ)
- [ ] Chạy `scripts/generate_checksums.py` để lấy SHA-256

**M2 — Toàn luồng (5 tài liệu mẫu):**
- [ ] `collector.py::collect_sources()` chạy được
- [ ] `parser.py::parse_pdf()` + `parse_html()` chạy được
- [ ] Output JSON đúng format (xem phần dưới)
- [ ] Bàn giao `data/parsed/sample_5docs/` cho Thanh

**M3 — Mở rộng:**
- [ ] Collector chạy toàn bộ sources.csv, idempotent
- [ ] Log URL lỗi rõ, không dừng toàn bộ khi 1 file lỗi
- [ ] Manifest ghi rõ stats: total/success/failed/skipped

### Format Output bắt buộc (thống nhất với Thanh)

Mỗi tài liệu output là một file JSON tại `data/parsed/{document_id}.json`:

```json
{
  "document_id": "eu_ai_act_2024_1689",
  "version_id": "v1",
  "title": "Regulation (EU) 2024/1689 Artificial Intelligence Act",
  "source_url": "https://eur-lex.europa.eu/eli/reg/2024/1689",
  "raw_path": "data/raw/eu_ai_act_2024_1689_v1.pdf",
  "file_format": "pdf",
  "jurisdiction": "EU",
  "language": "en",
  "document_type": "regulation",
  "collected_at": "2026-11-02T10:00:00Z",
  "content_hash": "abc123...",
  "parse_status": "success",
  "issued_date": "2024-07-12",
  "effective_date": null,
  "pages": [
    {"page_number": 1, "text": "REGULATION (EU) 2024/1689..."}
  ],
  "article_sections": [
    {"article": "Article 1", "section": null, "text": "Subject matter and scope..."}
  ]
}
```

> ⚠️ **KHÔNG đổi tên field** mà không báo Trang và Thanh trước!

### Quy tắc tránh conflict với Thanh và Trang

1. **Chỉ commit vào files của mình** — không đụng `src/processing/`, `src/rag/`, `app.py`
2. **`data/sources.csv`**: Chi thêm dòng quốc tế, không xóa dòng của Thanh
3. **`src/schemas.py`**: CHỈ ĐỌC — nếu cần sửa, tạo PR và ping Trang
4. **`data/bronze/vietnam/`**: Không thêm file vào đây (của Thanh)
5. Mỗi commit cho file data/bronze/international/ phải là riêng biệt, không batch chung với code

---

## 🟢 THANH — Module: Processing + RAG (Spark ETL, Chunking, Embedding, Q&A)

### Nhánh Git riêng
```bash
git checkout -b feature/thanh/processing-rag
```

### Files THANH sở hữu (chỉ THANH commit vào đây)

| File | Mô tả |
|------|-------|
| `src/processing/spark_etl.py` | PySpark: clean, dedup, validate → Parquet (FR04) |
| `src/processing/chunker.py` | Chia đoạn theo điều/khoản/đoạn văn (FR05 partial) |
| `src/rag/indexer.py` | Embed BGE-M3 + upsert Qdrant (FR05 embedding) |
| `src/rag/retriever.py` | Query embedding + Qdrant search + filter (FR06) |
| `src/rag/answerer.py` | LLM Qwen3 + citation validation (FR07, FR09) |
| `scripts/run_etl.py` | Script chạy Spark ETL |
| `scripts/run_chunk.py` | Script chunking |
| `scripts/run_index.py` | Script indexing |
| `data/bronze/vietnam/**` | ✅ Đã push (15 tài liệu VN) |
| `data/bronze/metadata/vietnam_documents.csv` | ✅ Đã push |

### Tasks theo mốc

**M1 — Cài đặt và test nhanh:**
- [ ] `ollama pull bge-m3` và `ollama pull qwen3:4b`
- [ ] Khởi động Qdrant: `docker run -p 6333:6333 qdrant/qdrant`
- [ ] Test nhanh: embed 1 câu → upsert Qdrant → query lại được

**M2 — Toàn luồng (5 tài liệu mẫu từ Chi):**
- [ ] `spark_etl.py::clean_documents()`: đọc JSON từ Chi, output Parquet
  - Normalize Unicode, loại empty, dedup theo content_hash
  - In ra: số hợp lệ, lỗi, trùng, ngôn ngữ, tổng text length
- [ ] `chunker.py::build_chunks()`: Parquet → Chunks Parquet
  - Ưu tiên ranh giới điều/khoản, chunk_id stable (hash-based)
  - Mỗi chunk có đủ field theo `src/schemas.py::Chunk`
- [ ] `indexer.py::build_index()`: batch embed BGE-M3 (batch=8), upsert Qdrant
  - Idempotent: chạy 2 lần không tăng số chunk trong Qdrant
- [ ] `retriever.py::retrieve()`: query + filter jurisdiction → top-5 kết quả
- [ ] `answerer.py::answer()`: gọi Qwen3, validate citations [S1],[S2]...

**M3 — Mở rộng + minh chứng Spark:**
- [ ] ETL chạy trên toàn corpus, log Spark job chi tiết
- [ ] Lưu Parquet lên HDFS (hoặc local nếu demo 1 máy)
- [ ] Chunk xử lý cả tiếng Việt (VN) và tiếng Anh (EU)

**M4 — RAG Quality:**
- [ ] Hit@5 ≥ 80% trên 10 câu hỏi mẫu
- [ ] TC06: câu hỏi ngoài corpus → `insufficient_evidence`
- [ ] TC07: LLM trả S99 không tồn tại → bị block, retry hoặc error
- [ ] TC08: Ollama tắt → retrieval vẫn chạy, báo lỗi generation

### Format Output bắt buộc (thống nhất với Chi)

```python
# Chunk Parquet schema (phải match src/schemas.py::Chunk)
{
    "chunk_id": "a1b2c3d4e5f6g7h8",  # stable: hash(doc_id+version+index+text[:100])
    "document_id": "eu_ai_act_2024_1689",
    "version_id": "v1",
    "title": "EU AI Act",
    "text": "Article 5 — Prohibited AI practices...",
    "source_url": "https://eur-lex.europa.eu/eli/reg/2024/1689",
    "jurisdiction": "EU",
    "language": "en",
    "document_type": "regulation",
    "article": "Article 5",
    "section": None,
    "page_start": 14,
    "page_end": 16,
    "chunk_index": 0,
    "embedding_model": "bge-m3",
    "indexed_at": "2026-11-02T12:00:00Z"
}
```

### Format Output `answer()` (thống nhất với Trang)

```python
{
    "status": "answered",  # or "insufficient_evidence" or "error"
    "answer": "Theo Điều 5 EU AI Act, các hệ thống AI bị cấm...",
    "citations": [
        {
            "source_id": "S1",
            "chunk_id": "a1b2c3d4e5f6g7h8",
            "document_id": "eu_ai_act_2024_1689",
            "title": "EU AI Act",
            "excerpt": "Article 5 — Prohibited AI practices...",
            "location": "Article 5, Page 14",
            "source_url": "https://eur-lex.europa.eu/eli/reg/2024/1689"
        }
    ],
    "timings": {
        "retrieval_ms": 120,
        "generation_ms": 3500
    }
}
```

### Quy tắc tránh conflict với Chi và Trang

1. **Chỉ commit vào files của mình** — không đụng `src/ingestion/`, `app.py`
2. **`data/bronze/international/`**: Không thêm file vào đây (của Chi)
3. **`src/schemas.py`**: CHỈ ĐỌC — nếu cần sửa, tạo PR và ping Trang
4. **`config.yaml`**: Đọc config, không commit thay đổi config (dùng `.env` local)
5. Đợi Chi bàn giao `data/parsed/sample_5docs/` trước khi bắt đầu ETL (M2)

---

## 🔴 TRANG — Nhóm trưởng: Architecture + Integration + App

### Files TRANG sở hữu

| File | Mô tả |
|------|-------|
| `src/schemas.py` | **Schema dùng chung — chỉ TRANG merge** |
| `app.py` | Streamlit UI (2 tabs: Tra cứu + Hỏi đáp) |
| `config.yaml` | Config chính |
| `.env.example` | Template biến môi trường |
| `README.md` | Hướng dẫn cài đặt và chạy |
| `scripts/run_pipeline.py` | Full pipeline script |
| `tests/` | Test schemas + integration tests TC01-TC09 |
| `evaluation/qa_eval_set.csv` | 30 câu hỏi kiểm thử (25 có đáp + 5 không) |
| `evaluation/eval_runner.py` | Script chạy evaluation |

---

## 🔄 Quy trình Git chung

```bash
# Bước 1: Clone về máy
git clone https://github.com/trangtretrau2005/BTL_bigdata.git
cd BTL_bigdata

# Bước 2: Tạo nhánh của mình
git checkout -b feature/chi/ingestion      # CHI
git checkout -b feature/thanh/processing-rag  # THANH

# Bước 3: Cài packages
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env   # rồi sửa URL theo máy mình

# Bước 4: Làm việc, commit thường xuyên
git add src/ingestion/collector.py
git commit -m "feat(ingestion): implement collect_sources with SHA-256"
git push origin feature/chi/ingestion

# Bước 5: Khi xong milestone, ping Trang để review và merge
```

### Quy ước commit message
```
feat(module): mô tả ngắn gọn
fix(module): mô tả ngắn gọn
test(module): mô tả ngắn gọn
docs(module): mô tả ngắn gọn
```

---

## ⚠️ Files TUYỆT ĐỐI không được đụng chéo

| File/Thư mục | Chủ | Người khác |
|---|---|---|
| `src/ingestion/` | CHI | Chỉ `import`, không sửa |
| `src/processing/` | THANH | Chỉ `import`, không sửa |
| `src/rag/` | THANH | Chỉ `import`, không sửa |
| `src/schemas.py` | TRANG | Tạo PR nếu cần sửa |
| `app.py` | TRANG | Không sửa |
| `data/bronze/vietnam/` | THANH ✅ | Không thêm file |
| `data/bronze/international/` | CHI | Không thêm file |
| `data/bronze/metadata/vietnam_documents.csv` | THANH ✅ | Không sửa |
| `data/bronze/metadata/international_documents.csv` | CHI | Không sửa |

---

## 📅 Mốc quan trọng

| Mốc | Điều kiện | Ai bàn giao |
|-----|-----------|-------------|
| **M1** | Schema OK + 5 tài liệu mẫu + 1 câu hỏi mẫu | Trang (schema) + Chi (5 docs) |
| **M2** | 5 docs → index → Streamlit có nguồn | Trang (tích hợp) |
| **M3** | 20-30 docs, HDFS, Spark ETL, không trùng | Chi + Thanh |
| **M4** | 30 câu frozen, đo Hit@5, fix bugs | Cả nhóm |
| **M5** | README chạy được, demo ổn, báo cáo số đo | Trang (tổng hợp) |

---

## 🤖 HƯỚNG DẪN DÀNH CHO AI AGENT CỦA CHI VÀ THANH (Cursor / Claude Code / Copilot / Antigravity)

> Khi Chi hoặc Thanh dùng AI Assistant (Cursor, Claude Code, Antigravity, Copilot), hãy **copy toàn bộ prompt bên dưới** dán vào ô chat hoặc file `.cursorrules` / `AGENTS.md` để Agent của từng bạn hiểu ngữ cảnh và **tuyệt đối không gây conflict**.

---

### 🔵 Prompt mẫu dành cho Agent của CHI

```markdown
Bạn là AI Assistant hỗ trợ CHI trong dự án BTL Big Data: AI Doc RAG (Hệ thống tra cứu và hỏi đáp văn bản về trí tuệ nhân tạo sử dụng Data Lake và RAG).
Repo: https://github.com/trangtretrau2005/BTL_bigdata
Nhánh git của Chi: feature/chi/ingestion

QUY TẮC PHẠM VI (SCOPE BOUNDARIES) CỰC KỲ NGHIÊM NGẶT:
1. Bạn CHỈ ĐƯỢC PHÉP tạo hoặc sửa các file sau:
   - src/ingestion/collector.py
   - src/ingestion/parser.py
   - src/ingestion/manifest.py
   - scripts/run_collect.py
   - scripts/run_parse.py
   - data/sources.csv (chỉ bổ sung dòng quốc tế, không xóa dòng Việt Nam)
   - data/bronze/international/**
   - data/bronze/metadata/international_documents.csv

2. TUYỆT ĐỐI KHÔNG ĐƯỢC CHỈNH SỬA:
   - src/schemas.py (Contract dùng chung - do nhóm trưởng Trang quản lý)
   - src/processing/** (Module của Thanh)
   - src/rag/** (Module của Thanh)
   - app.py (Giao diện Streamlit của Trang)
   - data/bronze/vietnam/** (Dữ liệu của Thanh)
   - data/bronze/metadata/vietnam_documents.csv

3. MỤC TIÊU CÔNG VIỆC CỦA CHI:
   - FR01: Đọc danh sách data/sources.csv
   - FR02: Download tài liệu gốc lưu vào data/raw/, tính SHA-256 checksum, ghi collection_manifest.json
   - FR03: Parser trích xuất text từ PDF (dùng PyMuPDF fitz) và HTML (dùng BeautifulSoup), phát hiện cờ scan-only PDF.
   - Bàn giao data/parsed/{document_id}.json theo đúng schema ProcessedDocument để Thanh làm tiếp.

4. LỆNH KIỂM TRA TRƯỚC KHI COMMIT:
   - python scripts/generate_checksums.py
   - python scripts/run_collect.py --sources data/sources.csv --output data/raw
   - python scripts/run_parse.py --raw data/raw --output data/parsed
   - pytest tests/test_schemas.py
```

---

### 🟢 Prompt mẫu dành cho Agent của THANH

```markdown
Bạn là AI Assistant hỗ trợ THANH trong dự án BTL Big Data: AI Doc RAG (Hệ thống tra cứu và hỏi đáp văn bản về trí tuệ nhân tạo sử dụng Data Lake và RAG).
Repo: https://github.com/trangtretrau2005/BTL_bigdata
Nhánh git của Thanh: feature/thanh/processing-rag

QUY TẮC PHẠM VI (SCOPE BOUNDARIES) CỰC KỲ NGHIÊM NGẶT:
1. Bạn CHỈ ĐƯỢC PHÉP tạo hoặc sửa các file sau:
   - src/processing/spark_etl.py
   - src/processing/chunker.py
   - src/rag/indexer.py
   - src/rag/retriever.py
   - src/rag/answerer.py
   - scripts/run_etl.py
   - scripts/run_chunk.py
   - scripts/run_index.py

2. TUYỆT ĐỐI KHÔNG ĐƯỢC CHỈNH SỬA:
   - src/schemas.py (Contract dùng chung - do nhóm trưởng Trang quản lý)
   - src/ingestion/** (Module của Chi)
   - app.py (Giao diện Streamlit của Trang)
   - data/bronze/international/** (Dữ liệu của Chi)
   - data/bronze/metadata/international_documents.csv (Metadata của Chi)

3. MỤC TIÊU CÔNG VIỆC CỦA THANH:
   - FR04: PySpark ETL: Đọc data/parsed/*.json, chuẩn hóa Unicode & khoảng trắng, loại bản ghi rỗng, khử trùng theo content_hash, xuất data/processed/ Parquet và etl_report.json.
   - FR05: Chunking: Ưu tiên ranh giới Điều / Khoản / Mục (400-800 tokens, overlap 50-100 tokens), tạo chunk_id ổn định theo content hash. Batch embed bằng BGE-M3 (qua Ollama, batch size 8), upsert vào Qdrant collection `ai_documents` (vector size 1024, Cosine).
   - FR06: Retriever: embed câu hỏi bằng BGE-M3, tìm top_k=5 từ Qdrant, hỗ trợ filter jurisdiction và document_id.
   - FR07, FR08, FR09: Answerer: Gọi Qwen3 qua Ollama với context có nhãn [S1], [S2]... Validate ID nguồn trích dẫn, nếu cite nhãn không tồn tại thì reject/retry. Nếu không đủ tài liệu thì trả về insufficient_evidence.

4. LỆNH KIỂM TRA TRƯỚC KHI COMMIT:
   - pytest tests/ -v
   - python scripts/run_etl.py
   - python scripts/run_chunk.py
   - python scripts/run_index.py
   - python evaluation/eval_runner.py
```

---

*Tạo tự động từ PRD_Data_Lake_RAG_AI.docx và phân tích repo — 02/11/2026*
