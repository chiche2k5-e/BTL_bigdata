"""
FR03: Text extraction from HTML, PDF, DOCX.
Owner: Chi

Trích xuất văn bản thuần từ các định dạng file khác nhau,
chuẩn bị cho bước ETL và chunking.
"""
from pathlib import Path
from typing import Optional, List, Tuple
import logging

logger = logging.getLogger(__name__)


def parse_html(file_path: Path, source_url: str) -> dict:
    """
    Trích xuất nội dung chính từ file HTML.
    Loại bỏ nav, header, footer, sidebar, quảng cáo.

    Args:
        file_path: Đường dẫn file HTML đã tải
        source_url: URL gốc (để xác định cấu trúc trang nếu cần)

    Returns:
        dict: {
            "text": str,               # Full text đã làm sạch
            "title": str,             # Tiêu đề trang
            "article_sections": [],   # [{"heading": str, "text": str}]
            "parse_status": str       # "success" | "empty" | "failed"
        }

    Gợi ý implement:
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(html_content, "lxml")
        # Xóa script, style, nav, footer
        for tag in soup(["script","style","nav","footer","header","aside"]):
            tag.decompose()
        # Lấy main content
        main = soup.find("main") or soup.find("article") or soup.body
    """
    raise NotImplementedError("Chi implements parse_html()")


def parse_pdf(file_path: Path) -> dict:
    """
    Trích xuất văn bản theo trang từ PDF dùng PyMuPDF (fitz).
    Phát hiện PDF scan (không có text layer).

    Args:
        file_path: Đường dẫn file PDF

    Returns:
        dict: {
            "text": str,               # Toàn bộ text nối lại
            "pages": [                 # Danh sách text từng trang
                {"page": 1, "text": str}
            ],
            "parse_status": str,       # "success" | "scan_detected" | "empty" | "failed"
            "article_sections": []     # Các section phát hiện được (nếu có)
        }

    Gợi ý implement:
        import fitz  # PyMuPDF
        doc = fitz.open(str(file_path))
        for page_num, page in enumerate(doc, 1):
            text = page.get_text("text")
            if len(text.strip()) < 50 and page_num == 1:
                # Có thể là scan PDF
                ...
    """
    raise NotImplementedError("Chi implements parse_pdf()")


def parse_docx(file_path: Path) -> dict:
    """
    Trích xuất văn bản từ DOCX, giữ lại cấu trúc tiêu đề và bảng.

    Args:
        file_path: Đường dẫn file DOCX

    Returns:
        dict: {
            "text": str,               # Full text
            "pages": [],              # DOCX không có trang, để []
            "parse_status": str,
            "article_sections": [{"heading": str, "text": str}]
        }

    Gợi ý implement:
        from docx import Document
        doc = Document(str(file_path))
        for para in doc.paragraphs:
            if para.style.name.startswith("Heading"):
                # Đây là tiêu đề điều/khoản
                ...
    """
    raise NotImplementedError("Chi implements parse_docx()")


def parse_document(raw_path: str, file_format: str, source_url: str) -> dict:
    """
    Dispatch đến parser phù hợp dựa trên file_format.

    Args:
        raw_path: Đường dẫn file đã tải về
        file_format: "pdf" | "html" | "docx"
        source_url: URL gốc của tài liệu

    Returns:
        dict: {
            "text": str,
            "pages": list,
            "parse_status": str,       # ParseStatus value
            "article_sections": list
        }
    """
    raise NotImplementedError(
        "Chi implements parse_document() - dispatch sang parse_html/parse_pdf/parse_docx\n"
        "Xử lý exception và set parse_status='failed' nếu lỗi"
    )
