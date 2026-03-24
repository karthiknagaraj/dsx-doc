import streamlit as st

# Optional: load environment variables from a local .env file.
# Keep dependency optional (works if python-dotenv is installed).
try:
    from dotenv import find_dotenv  # type: ignore
    from dotenv import load_dotenv  # type: ignore

    _dotenv_path = find_dotenv(usecwd=True)
    load_dotenv(_dotenv_path, override=True)
except Exception:
    pass

from tab_documentation import render_docs_tab  # this is the "Documentation" tab
from tab_semantic_search import render_semantic_search_tab  # this is the "Semantic Search" tab


def _safe_render(label: str, fn) -> None:
    """Render a tab and show any exceptions instead of failing silently."""
    try:
        fn()
    except Exception as e:
        st.error(f"Tab '{label}' failed: {type(e).__name__}: {e}")
        st.exception(e)

def main():
    st.set_page_config(
        page_title="DSX Documentation Assistant",
        page_icon="📄",
        layout="wide"
    )
    
    st.title("📄 DSX Documentation Assistant")
    st.markdown("Upload your .dsx files to extract metadata and generate human-friendly documentation.")

    # Use native tabs for clean horizontal navigation
    tab1, tab2 = st.tabs(["📝 Documentation", "🔎 Semantic Search"])
    
    with tab1:
        _safe_render("Documentation", render_docs_tab)
    
    with tab2:
        _safe_render("Semantic Search", render_semantic_search_tab)
    
    # Footer
    st.markdown("---")
    st.markdown("*Built with Streamlit | DSX Documentation Assistant*")

if __name__ == "__main__":
    main()
