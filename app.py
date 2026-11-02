"""
Streamlit application - FR06, FR07, FR08, FR09, FR10.
Owner: Trang (group lead)

Giao diện tra cứu và hỏi đáp văn bản pháp luật & chính sách AI.
Chạy: streamlit run app.py
"""
import streamlit as st
import os
from dotenv import load_dotenv
from src.rag.retriever import retrieve
from src.rag.answerer import answer

load_dotenv()

# Config from environment
QDRANT_URL = os.getenv("QDRANT_URL", "http://localhost:6333")
QDRANT_COLLECTION = os.getenv("QDRANT_COLLECTION", "ai_documents")
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "bge-m3")
CHAT_MODEL = os.getenv("CHAT_MODEL", "qwen3:4b")
TOP_K = int(os.getenv("TOP_K", "5"))

st.set_page_config(
    page_title="AI Doc RAG",
    page_icon="📚",
    layout="wide",
    initial_sidebar_state="expanded",
)

# --- Sidebar ---
with st.sidebar:
    st.title("📚 AI Doc RAG")
    st.caption("Tra cứu văn bản pháp luật & chính sách AI")

    # TODO: Trang thêm document count, chunk count, snapshot time từ manifest
    # Ví dụ:
    # from src.ingestion.manifest import read_manifest
    # manifest = read_manifest("data/manifests/collection_manifest.json")
    # st.metric("Tài liệu", manifest.get("success", "—"))

    st.divider()

    jurisdiction = st.selectbox(
        "🌐 Khu vực",
        ["Tất cả", "VN", "EU", "International", "ASEAN"],
        help="Lọc kết quả theo khu vực địa lý",
    )
    doc_filter = st.text_input(
        "📄 Lọc theo tên/ID văn bản (tùy chọn)",
        placeholder="e.g., eu_ai_act_2024_1689",
    )
    top_k = st.slider("Số kết quả tối đa", min_value=1, max_value=10, value=TOP_K)

    st.divider()
    st.caption(f"Model embed: `{EMBEDDING_MODEL}`")
    st.caption(f"Model chat: `{CHAT_MODEL}`")
    st.caption(f"Qdrant: `{QDRANT_URL}`")

# --- Main area ---
tab_search, tab_qa = st.tabs(["🔍 Tra cứu", "💬 Hỏi đáp"])

# ===================== TAB TRA CỨU =====================
with tab_search:
    st.subheader("Tìm kiếm ngữ nghĩa")
    st.caption("Nhập từ khóa hoặc câu hỏi để tìm các đoạn văn bản liên quan nhất.")

    query = st.text_area(
        "Nhập câu hỏi hoặc từ khóa",
        max_chars=2000,
        height=100,
        placeholder="Ví dụ: EU AI Act phân loại hệ thống rủi ro cao như thế nào?",
    )

    if st.button("🔍 Tìm kiếm", key="search_btn", type="primary"):
        if not query.strip():
            st.warning("Vui lòng nhập câu hỏi hoặc từ khóa.")
        else:
            with st.spinner("Đang tìm kiếm..."):
                try:
                    jfilter = None if jurisdiction == "Tất cả" else jurisdiction
                    results = retrieve(
                        query=query,
                        qdrant_url=QDRANT_URL,
                        collection_name=QDRANT_COLLECTION,
                        embedding_model=EMBEDDING_MODEL,
                        top_k=top_k,
                        jurisdiction_filter=jfilter,
                        document_id_filter=doc_filter or None,
                    )
                    if not results:
                        st.info("Không tìm thấy kết quả phù hợp. Thử mở rộng bộ lọc hoặc đổi từ khóa.")
                    else:
                        st.success(f"Tìm thấy {len(results)} kết quả")
                        for i, chunk in enumerate(results, 1):
                            score = chunk.get("score", 0)
                            location = chunk.get("article") or chunk.get("section") or ""
                            with st.expander(
                                f"[{i}] {chunk['title']} — Score: {score:.3f}",
                                expanded=(i == 1),
                            ):
                                cols = st.columns([3, 1])
                                with cols[0]:
                                    st.markdown(f"**📌 Vị trí:** {location or '—'}")
                                    st.markdown(f"**🌐 Khu vực:** `{chunk.get('jurisdiction','—')}`  "
                                                f"**🗣 Ngôn ngữ:** `{chunk.get('language','—')}`")
                                with cols[1]:
                                    if chunk.get("source_url"):
                                        st.link_button("🔗 Xem nguồn", chunk["source_url"])
                                st.divider()
                                st.markdown(chunk["text"])
                except NotImplementedError:
                    st.error("⚠️ Chức năng retrieve() chưa được implement. "
                             "Thanh cần hoàn thiện src/rag/retriever.py")
                except Exception as e:
                    st.error(f"Lỗi kết nối: {e}")
                    st.info("Kiểm tra Qdrant và Ollama đang chạy, sau đó thử lại.")

# ===================== TAB HỎI ĐÁP =====================
with tab_qa:
    st.subheader("Hỏi đáp có trích dẫn")
    st.caption("Đặt câu hỏi — hệ thống sẽ tìm nguồn phù hợp và sinh câu trả lời.")

    qa_query = st.text_area(
        "Câu hỏi",
        max_chars=2000,
        height=100,
        key="qa_input",
        placeholder="Ví dụ: Chiến lược AI quốc gia Việt Nam đặt mục tiêu gì đến năm 2030?",
    )

    if st.button("💬 Hỏi đáp", key="qa_btn", type="primary"):
        if not qa_query.strip():
            st.warning("Vui lòng nhập câu hỏi.")
        else:
            with st.spinner("Đang tìm kiếm nguồn và sinh câu trả lời..."):
                try:
                    jfilter = None if jurisdiction == "Tất cả" else jurisdiction
                    # Step 1: Retrieve
                    retrieved = retrieve(
                        query=qa_query,
                        qdrant_url=QDRANT_URL,
                        collection_name=QDRANT_COLLECTION,
                        embedding_model=EMBEDDING_MODEL,
                        top_k=top_k,
                        jurisdiction_filter=jfilter,
                        document_id_filter=doc_filter or None,
                    )
                    # Step 2: Generate answer
                    result = answer(
                        query=qa_query,
                        retrieved_chunks=retrieved,
                        ollama_url=OLLAMA_BASE_URL,
                        chat_model=CHAT_MODEL,
                    )

                    # Render kết quả
                    status = result.get("status")
                    if status == "answered":
                        st.success("✅ Câu trả lời")
                        st.markdown(result["answer"])
                    elif status == "insufficient_evidence":
                        st.warning("⚠️ Không đủ căn cứ từ tài liệu hiện có.")
                        if result.get("answer"):
                            st.markdown(result["answer"])
                    elif status == "error":
                        st.error(f"❌ Lỗi sinh câu trả lời: {result.get('error_message')}")
                        st.info("Các nguồn tìm được vẫn hiển thị bên dưới.")

                    # Render citations
                    citations = result.get("citations", [])
                    if citations:
                        st.divider()
                        st.subheader("📚 Nguồn tham khảo")
                        for cit in citations:
                            with st.expander(
                                f"[{cit['source_id']}] {cit['title']}",
                                expanded=False,
                            ):
                                if cit.get("location"):
                                    st.markdown(f"**📌 Vị trí:** {cit['location']}")
                                st.markdown(f"> {cit['excerpt']}...")
                                if cit.get("source_url"):
                                    st.link_button("🔗 Xem tài liệu gốc", cit["source_url"])

                    # Timings
                    timings = result.get("timings", {})
                    if timings.get("generation_ms"):
                        st.caption(f"⏱ Sinh câu trả lời: {timings['generation_ms']}ms")

                except NotImplementedError as e:
                    st.error(f"⚠️ Chức năng chưa implement: {e}")
                except Exception as e:
                    st.error(f"Lỗi: {e}")
                    st.info("Kiểm tra Qdrant, Ollama đang chạy và đã có dữ liệu index.")
