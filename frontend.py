
import os

import requests
import streamlit as st


st.set_page_config(
    page_title="EnterpriseFlow AI",
    page_icon="🏢",
    layout="wide",
)

default_api_url = os.getenv(
    "API_BASE_URL", "http://127.0.0.1:8000"
)

with st.sidebar:
    st.title("⚙️ Settings")
    api_url = st.text_input(
        "Backend API URL",
        value=default_api_url,
        help="Example: http://127.0.0.1:8000",
    ).strip().rstrip("/")

    st.caption("Powered by FastAPI, ChromaDB and OpenRouter")

    if st.button("Check backend", use_container_width=True):
        try:
            response = requests.get(
                f"{api_url}/health", timeout=10
            )
            response.raise_for_status()
            st.success("Backend is reachable.")
        except requests.RequestException as exc:
            st.error(f"Backend connection failed: {exc}")

st.title("🏢 EnterpriseFlow AI")
st.write(
    "Your enterprise operations copilot. Upload internal "
    "documents, ask questions, and inspect the sources "
    "used to generate answers."
)

upload_tab, ask_tab = st.tabs(
    ["📄 Knowledge Base", "💬 Ask EnterpriseFlow"]
)

with upload_tab:
    st.subheader("Add knowledge to your copilot")
    st.write(
        "Upload PDF, TXT, or Markdown files. "
        "The backend indexes their text for semantic search."
    )

    uploaded_file = st.file_uploader(
        "Choose a document",
        type=["pdf", "txt", "md"],
        help="Maximum file size: 10 MB.",
    )

    if st.button(
        "Upload and index document",
        disabled=uploaded_file is None,
        type="primary",
    ):
        try:
            response = requests.post(
                f"{api_url}/documents",
                files={
                    "file": (
                        uploaded_file.name,
                        uploaded_file.getvalue(),
                        uploaded_file.type
                        or "application/octet-stream",
                    )
                },
                timeout=180,
            )

            if response.ok:
                result = response.json()
                st.success(
                    f"Indexed {result['chunks_indexed']} chunks "
                    f"from {result['filename']}."
                )
                st.metric(
                    "Total indexed chunks",
                    result["total_chunks"],
                )
            else:
                st.error(
                    f"Upload failed ({response.status_code}): "
                    f"{response.text}"
                )
        except requests.RequestException as exc:
            st.error(f"Could not reach the backend: {exc}")

    if st.button("Refresh knowledge-base status"):
        try:
            response = requests.get(
                f"{api_url}/documents/status", timeout=10
            )
            response.raise_for_status()
            count = response.json()["indexed_chunks"]
            st.metric("Indexed text chunks", count)
        except requests.RequestException as exc:
            st.error(f"Could not get status: {exc}")

with ask_tab:
    st.subheader("Ask your documents")

    if "messages" not in st.session_state:
        st.session_state.messages = []

    if st.button("Clear conversation"):
        st.session_state.messages = []
        st.rerun()

    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

            if message.get("sources"):
                with st.expander("View retrieved sources"):
                    for source in message["sources"]:
                        page = source.get("page")
                        location = source["filename"]
                        if page is not None:
                            location += f" — page {page}"

                        st.markdown(f"**{location}**")
                        st.caption(source["snippet"])

    question = st.chat_input(
        "Ask about your uploaded policies or procedures..."
    )

    if question:
        st.session_state.messages.append(
            {"role": "user", "content": question}
        )

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):
            with st.spinner("Searching documents and generating answer..."):
                try:
                    response = requests.post(
                        f"{api_url}/ask",
                        json={"question": question},
                        timeout=90,
                    )

                    if response.ok:
                        result = response.json()
                        answer = result["answer"]
                        sources = result.get("sources", [])

                        st.markdown(answer)

                        if sources:
                            with st.expander("View retrieved sources"):
                                for source in sources:
                                    location = source["filename"]
                                    if source.get("page") is not None:
                                        location += (
                                            f" — page {source['page']}"
                                        )
                                    st.markdown(f"**{location}**")
                                    st.caption(source["snippet"])
                        else:
                            st.info(
                                "No document excerpts were retrieved. "
                                "This answer is not grounded in the "
                                "uploaded knowledge base."
                            )

                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": answer,
                                "sources": sources,
                            }
                        )
                    else:
                        error_message = (
                            f"API error ({response.status_code}): "
                            f"{response.text}"
                        )
                        st.error(error_message)
                        st.session_state.messages.append(
                            {
                                "role": "assistant",
                                "content": error_message,
                            }
                        )

                except requests.RequestException as exc:
                    error_message = f"Backend connection failed: {exc}"
                    st.error(error_message)
                    st.session_state.messages.append(
                        {
                            "role": "assistant",
                            "content": error_message,
                        }
                    )
