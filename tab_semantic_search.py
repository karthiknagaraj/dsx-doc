from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional

import numpy as np
import streamlit as st

from embeddings import load_embeddings_config, embed_texts_openai_compatible, cosine_similarity
from doc_generator import ChatConfig, generate_answer_with_citations




def render_semantic_search_tab() -> None:
    st.header("🔎 Semantic Search")
    st.caption(
        "Upload a generated documentation file (.md or .pdf), create text chunks, generate embeddings, and search semantically."
    )

    # Single-DB mode: keep the UI simple and always use one SQLite file.
    db_path = "dsx_graph_all.sqlite"
    st.caption(f"Using SQLite DB: `{db_path}`")

    st.subheader("Upload Generated Documentation")
    uploaded_file = st.file_uploader(
        "Select a generated documentation file",
        type=["md", "pdf"],
        help="Upload a .md or .pdf file containing generated DataStage job documentation"
    )
    
    if uploaded_file is None:
        st.info("👆 Please upload a generated documentation file (.md or .pdf) to begin.")
        return
    
    # Store file content in session state
    file_content = uploaded_file.read()
    file_name = uploaded_file.name
    file_type = "markdown" if file_name.endswith(".md") else "pdf"
    
    st.success(f"✓ Loaded: `{file_name}` ({len(file_content):,} bytes, {file_type})")

    st.subheader("Embeddings config")
    st.write(
        {
            "DSX_PROVIDER": os.environ.get("DSX_PROVIDER", "openrouter"),
            "DSX_MODEL": os.environ.get("DSX_MODEL", "openai/text-embedding-3-small"),
            "DSX_BASE_URL": os.environ.get("DSX_BASE_URL", "https://openrouter.ai/api/v1"),
            "DSX_API_KEY": "(set)" if os.environ.get("DSX_API_KEY") else "(missing)",
            "DSX_OPENROUTER_HTTP_REFERER": os.environ.get("DSX_OPENROUTER_HTTP_REFERER", "(optional)"),
            "DSX_OPENROUTER_X_TITLE": os.environ.get("DSX_OPENROUTER_X_TITLE", "(optional)"),
        }
    )

    # Initialize session state for chunks if needed
    if "doc_chunks" not in st.session_state:
        st.session_state.doc_chunks = []
    if "doc_embeddings" not in st.session_state:
        st.session_state.doc_embeddings = []

    st.markdown("---")
    st.subheader("1) Build chunks from document")
    
    chunk_size = st.number_input("Chunk size (characters)", min_value=100, max_value=5000, value=1000, step=100)
    chunk_overlap = st.number_input("Chunk overlap (characters)", min_value=0, max_value=500, value=200, step=50)
    
    if st.button("Build chunks", type="primary"):
        # Parse document content
        if file_type == "markdown":
            content = file_content.decode("utf-8")
        else:  # PDF
            try:
                import PyPDF2
                from io import BytesIO
                pdf_reader = PyPDF2.PdfReader(BytesIO(file_content))
                content = "\n\n".join([page.extract_text() for page in pdf_reader.pages])
            except ImportError:
                st.error("PyPDF2 not installed. Install with: pip install PyPDF2")
                return
            except Exception as e:
                st.error(f"Failed to parse PDF: {e}")
                return
        
        # Create chunks
        chunks = []
        start = 0
        chunk_id = 0
        while start < len(content):
            end = min(start + chunk_size, len(content))
            chunk_text = content[start:end]
            chunks.append({
                "chunk_id": f"{file_name}_chunk_{chunk_id}",
                "content": chunk_text,
                "chunk_type": "uploaded_documentation",
                "title": f"{file_name} (chunk {chunk_id})",
                "entity_type": "document",
                "entity_id": file_name,
            })
            chunk_id += 1
            start = end - chunk_overlap if end < len(content) else end
        
        st.session_state.doc_chunks = chunks
        st.success(f"✓ Created {len(chunks)} chunks from document")
    
    if st.session_state.doc_chunks:
        st.caption(f"Current chunks: **{len(st.session_state.doc_chunks)}**")

    st.subheader("2) Generate embeddings (API)")
    batch_size = st.number_input("Batch size", min_value=1, max_value=256, value=64)
    
    if st.button("Generate embeddings"):
        if not st.session_state.doc_chunks:
            st.warning("⚠️ No chunks available. Please build chunks first.")
            return
        
        try:
            cfg = load_embeddings_config()
        except Exception as e:
            st.error(str(e))
            return
        
        # Generate embeddings for chunks in batches
        embeddings = []
        chunks_to_embed = st.session_state.doc_chunks
        
        with st.status(f"Generating embeddings for {len(chunks_to_embed)} chunks...", expanded=False) as status:
            for i in range(0, len(chunks_to_embed), int(batch_size)):
                batch = chunks_to_embed[i:i + int(batch_size)]
                texts = [chunk["content"] for chunk in batch]
                
                try:
                    batch_embeddings = embed_texts_openai_compatible(cfg, texts)
                    
                    for chunk, emb in zip(batch, batch_embeddings):
                        embeddings.append({
                            **chunk,
                            "embedding": emb,
                            "score": 0.0,  # Will be computed during search
                        })
                    
                    status.update(label=f"Embedded {min(i + int(batch_size), len(chunks_to_embed))}/{len(chunks_to_embed)} chunks...")
                except Exception as e:
                    st.error(f"Failed to embed batch {i // int(batch_size)}: {e}")
                    return
        
        st.session_state.doc_embeddings = embeddings
        st.success(f"✓ Embedded {len(embeddings)} chunks using {cfg.provider}:{cfg.model}")


    st.markdown("---")
    st.subheader("3) Search")
    query = st.text_input("Search query", value="What does the DataStage job do?")

    st.subheader("4) Answer (human-readable)")
    st.caption("Uses a chat model to write an answer grounded in the retrieved doc chunks, with citations.")

    chat_model_default = os.environ.get("DSX_CHAT_MODEL", "openai/gpt-5-nano")
    chat_base_url_default = os.environ.get("DSX_CHAT_BASE_URL", "https://openrouter.ai/api/v1")
    answer_model = st.text_input("Answer model", value=chat_model_default)
    answer_base_url = st.text_input("Answer base URL", value=chat_base_url_default)
    answer_timeout = st.number_input("Answer timeout (sec)", min_value=30, max_value=900, value=180, step=30)
    answer_max_retries = st.number_input("Answer retries", min_value=0, max_value=10, value=3, step=1)

    top_k = st.slider("Top K", min_value=1, max_value=25, value=5)

    enable_answer = st.toggle("Generate answer with citations", value=True)

    if st.button("Search", type="primary"):
        if not st.session_state.doc_embeddings:
            st.warning("⚠️ No embeddings available. Please generate embeddings first.")
            return
        
        try:
            cfg = load_embeddings_config()
        except Exception as e:
            st.error(str(e))
            return

        # Get query embedding
        try:
            query_embeddings = embed_texts_openai_compatible(cfg, [query])
            query_emb = query_embeddings[0]
        except Exception as e:
            st.error(f"Failed to embed query: {e}")
            return
        
        # Compute cosine similarity
        results = []
        for chunk in st.session_state.doc_embeddings:
            # Cosine similarity
            chunk_emb = chunk["embedding"]
            similarity = cosine_similarity(query_emb, chunk_emb)
            results.append({
                **chunk,
                "score": float(similarity),
            })

        
        # Sort by score descending and take top K
        results.sort(key=lambda x: x["score"], reverse=True)
        results = results[:int(top_k)]
        
        if not results:
            st.info("No results found.")
            return

        # Generate a human-readable answer on top of retrieval.
        if enable_answer:
            try:
                chat_key = os.environ.get("DSX_API_KEY")
                if not chat_key:
                    st.warning(
                        "No chat API key found. Set DSX_API_KEY in your .env file."
                    )
                else:
                    chat_cfg = ChatConfig(
                        api_key=chat_key,
                        model=answer_model,
                        base_url=answer_base_url,
                        provider=os.environ.get("DSX_CHAT_PROVIDER", "openrouter"),
                        http_referer=os.environ.get("DSX_OPENROUTER_HTTP_REFERER"),
                        x_title=os.environ.get("DSX_OPENROUTER_X_TITLE"),
                        timeout_sec=int(answer_timeout),
                        max_retries=int(answer_max_retries),
                        retry_backoff_sec=1.0,
                    )
                    with st.status("Generating answer…", expanded=False):
                        answer_md, _meta = generate_answer_with_citations(
                            question=query,
                            chunks=results,
                            cfg=chat_cfg,
                        )
                    st.markdown(answer_md)
            except Exception as e:
                st.error(f"Answer generation failed: {type(e).__name__}: {e}")

        st.markdown("---")
        st.subheader("Retrieved chunks (citations source)")
        st.write(f"Results: {len(results)}")
        for r in results:
            st.markdown(
                f"**{r['score']:.3f}** · {r.get('title') or r['chunk_id']}  \n"
                f"`{r['chunk_type']}` · `{r['entity_type']}` `{r.get('entity_id') or ''}`"
            )
            with st.expander("Show chunk"):
                st.code(r["content"], language=None)
