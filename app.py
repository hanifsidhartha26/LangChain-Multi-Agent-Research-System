import streamlit as st
import time
from src.agents.agents import build_search_agent, build_reader_agent, writer_chain, critic_chain
from src.pipelines.pipeline import run_research_pipeline

import streamlit as st
import re
from urllib.parse import urlparse
from datetime import datetime



# =========================================================
# PAGE CONFIGURATION
# =========================================================

st.set_page_config(
    page_title="ResearchAI",
    page_icon="🔬",
    layout="wide",
    initial_sidebar_state="expanded"
)


# =========================================================
# SESSION STATE
# =========================================================

if "messages" not in st.session_state:
    st.session_state.messages = []

if "research_history" not in st.session_state:
    st.session_state.research_history = []

if "research_result" not in st.session_state:
    st.session_state.research_result = None

if "research_topic" not in st.session_state:
    st.session_state.research_topic = None


# =========================================================
# CUSTOM CSS
# =========================================================

st.markdown("""
<style>

    .stApp {
        background-color: #F8FAFC;
        color: #1E293B;
    }

    .block-container {
        max-width: 1250px;
        padding-top: 2rem;
        padding-bottom: 3rem;
    }

    header {
        background: transparent !important;
    }

    #MainMenu,
    footer {
        visibility: hidden;
    }

    /* Sidebar */

    section[data-testid="stSidebar"] {
        background-color: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }

    /* Application title */

    .app-title {
        font-size: 36px;
        font-weight: 800;
        color: #4F46E5;
    }

    .app-subtitle {
        color: #64748B;
        font-size: 15px;
        margin-bottom: 25px;
    }

    /* Section headings */

    .section-title {
        font-size: 24px;
        font-weight: 750;
        color: #0F172A;
        margin-top: 20px;
        margin-bottom: 15px;
    }

    /* Cards */

    .info-card {
        background-color: #FFFFFF;
        padding: 18px;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        margin-bottom: 12px;
    }

    .info-label {
        color: #64748B;
        font-size: 13px;
    }

    .info-value {
        color: #4F46E5;
        font-size: 19px;
        font-weight: 700;
        margin-top: 7px;
    }

    /* Report */

    .report-card {
        background-color: #FFFFFF;
        padding: 24px;
        border: 1px solid #E2E8F0;
        border-radius: 14px;
        margin-bottom: 15px;
    }

    /* Buttons */

    .stButton > button {
        border-radius: 10px;
        font-weight: 600;
        min-height: 42px;
    }

    /* Text areas */

    .stTextArea textarea {
        border-radius: 12px;
        border: 1px solid #CBD5E1;
        background-color: #FFFFFF;
        color: #0F172A;
    }

    /* Links */

    a {
        color: #4F46E5 !important;
    }

    /* Tabs */

    .stTabs [data-baseweb="tab-list"] {
        gap: 12px;
        border-bottom: 1px solid #E2E8F0;
    }

    .stTabs [data-baseweb="tab"] {
        color: #64748B;
        font-weight: 600;
    }

    .stTabs [aria-selected="true"] {
        color: #4F46E5 !important;
    }

</style>
""", unsafe_allow_html=True)


# =========================================================
# URL EXTRACTION
# =========================================================

def extract_sources(
    search_results: str,
    scraped_content: str = ""
) -> list:
    """
    Extract unique HTTP/HTTPS URLs from search results
    and scraped content.
    """

    text = f"{search_results}\n{scraped_content}"

    # Find URLs in the text.
    urls = re.findall(
        r'https?://[^\s<>"\']+',
        text
    )

    sources = []
    seen = set()

    for url in urls:

        # Remove common trailing punctuation.
        url = url.rstrip(".,;:!?)\]}")

        try:
            parsed = urlparse(url)

            if parsed.scheme not in ("http", "https"):
                continue

            if not parsed.hostname:
                continue

            # Avoid duplicate links.
            if url in seen:
                continue

            seen.add(url)

            sources.append({
                "title": parsed.hostname,
                "url": url
            })

        except ValueError:
            continue

    return sources


# =========================================================
# SIDEBAR
# =========================================================

with st.sidebar:

    st.markdown("## 🔬 ResearchAI")

    st.caption("Your AI-powered research assistant")

    st.divider()

    # New research button.
    if st.button(
        "＋ New Research",
        use_container_width=True
    ):

        st.session_state.messages = []
        st.session_state.research_result = None
        st.session_state.research_topic = None

        st.rerun()

    st.markdown("### 📚 Research History")

    if not st.session_state.research_history:

        st.caption(
            "Your research history will appear here."
        )

    else:

        # Display the newest research first.
        for index, item in enumerate(
            reversed(st.session_state.research_history)
        ):

            label = item["topic"]

            if len(label) > 35:
                label = label[:35] + "..."

            if st.button(
                f"📄 {label}",
                key=f"history_{index}",
                use_container_width=True
            ):

                st.session_state.research_result = item["result"]

                st.session_state.research_topic = item["topic"]

                st.rerun()

    st.divider()

    st.markdown("### 🤖 Research Pipeline")

    st.markdown("""
    **01 — Search Agent**

    Find relevant information.

    **02 — Reader Agent**

    Extract source content.

    **03 — Writer Chain**

    Generate a research report.

    **04 — Critic Chain**

    Review the report.
    """)

    st.divider()

    st.caption(
        "Built with Python, Streamlit, and AI agents."
    )


# =========================================================
# HEADER
# =========================================================

st.markdown(
    '<div class="app-title">ResearchAI ✨</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="app-subtitle">'
    'Ask a question. Explore sources. Generate research reports.'
    '</div>',
    unsafe_allow_html=True
)


# =========================================================
# CHAT HISTORY
# =========================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])


# =========================================================
# CHAT INPUT
# =========================================================

prompt = st.chat_input(
    "What would you like to research?"
)


# =========================================================
# EXECUTE RESEARCH PIPELINE
# =========================================================

if prompt:

    # Display the user's question.
    st.session_state.messages.append({
        "role": "user",
        "content": prompt
    })

    with st.chat_message("user"):

        st.markdown(prompt)

    # Run the backend.
    with st.chat_message("assistant"):

        status = st.status(
            "Starting research...",
            expanded=True
        )

        try:

            status.write(
                "🔎 Searching for relevant information..."
            )

            with st.spinner(
                "Your AI research team is working..."
            ):

                result = run_research_pipeline(prompt)

            status.write(
                "📚 Collecting source content..."
            )

            status.write(
                "✍️ Generating the research report..."
            )

            status.write(
                "🧠 Reviewing the report..."
            )

            # Save the completed research.
            st.session_state.research_result = result

            st.session_state.research_topic = prompt

            history_item = {
                "topic": prompt,
                "result": result,
                "created_at": datetime.now().strftime(
                    "%Y-%m-%d %H:%M"
                )
            }

            st.session_state.research_history.append(
                history_item
            )

            status.update(
                label="Research completed successfully!",
                state="complete",
                expanded=False
            )

            st.session_state.messages.append({
                "role": "assistant",
                "content": (
                    f"Research on **{prompt}** is complete! "
                    "Your report, source links, and critic feedback "
                    "are available below."
                )
            })

        except Exception as error:

            status.update(
                label="Research failed.",
                state="error",
                expanded=True
            )

            st.error(
                f"An error occurred: {error}"
            )


# =========================================================
# DISPLAY RESEARCH RESULTS
# =========================================================

if st.session_state.research_result:

    result = st.session_state.research_result

    st.divider()

    st.markdown(
        '<div class="section-title">📊 Research Overview</div>',
        unsafe_allow_html=True
    )

    st.markdown(
        f"**Research topic:** {st.session_state.research_topic}"
    )

    # -----------------------------------------------------
    # STATUS CARDS
    # -----------------------------------------------------

    col1, col2, col3, col4 = st.columns(4)

    cards = [
        (col1, "🔎 Search Agent", "Information discovery"),
        (col2, "📚 Reader Agent", "Source extraction"),
        (col3, "✍️ Writer Chain", "Report generation"),
        (col4, "🧠 Critic Chain", "Report review")
    ]

    for column, title, description in cards:

        with column:

            st.markdown(
                f"""
                <div class="info-card">
                    <div class="info-label">{description}</div>
                    <div class="info-value">{title}</div>
                </div>
                """,
                unsafe_allow_html=True
            )

    # -----------------------------------------------------
    # RESULTS TABS
    # -----------------------------------------------------

    report_tab, sources_tab, reader_tab, critic_tab, links_tab = st.tabs([
        "📄 Report",
        "🔎 Search Results",
        "📚 Scraped Content",
        "🧠 Critic Feedback",
        "🔗 Sources & Links"
    ])

    # =====================================================
    # REPORT VIEWER
    # =====================================================

    with report_tab:

        st.subheader("📄 Research Report")

        report = result.get("report", "")

        st.markdown(
            '<div class="report-card">',
            unsafe_allow_html=True
        )

        st.markdown(str(report))

        st.markdown(
            "</div>",
            unsafe_allow_html=True
        )

        st.download_button(
            label="📥 Download Report (.md)",
            data=str(report),
            file_name="research_report.md",
            mime="text/markdown",
            use_container_width=True,
            key="download_report"
        )

    # =====================================================
    # SEARCH RESULTS
    # =====================================================

    with sources_tab:

        st.subheader("🔎 Search Agent Results")

        search_results = result.get(
            "search_results",
            ""
        )

        st.text_area(
            "Search results",
            value=str(search_results),
            height=400,
            disabled=True,
            label_visibility="collapsed"
        )

        st.download_button(
            label="📥 Download Search Results",
            data=str(search_results),
            file_name="search_results.txt",
            mime="text/plain",
            key="download_search"
        )

    # =====================================================
    # SCRAPED CONTENT
    # =====================================================

    with reader_tab:

        st.subheader("📚 Extracted Source Content")

        scraped_content = result.get(
            "scraped_content",
            ""
        )

        st.text_area(
            "Scraped content",
            value=str(scraped_content),
            height=400,
            disabled=True,
            label_visibility="collapsed"
        )

        st.download_button(
            label="📥 Download Scraped Content",
            data=str(scraped_content),
            file_name="scraped_content.txt",
            mime="text/plain",
            key="download_scraped"
        )

    # =====================================================
    # CRITIC FEEDBACK
    # =====================================================

    with critic_tab:

        st.subheader("🧠 Critic Review")

        feedback = result.get(
            "feedback",
            ""
        )

        st.markdown(str(feedback))

        st.download_button(
            label="📥 Download Critic Feedback",
            data=str(feedback),
            file_name="critic_feedback.md",
            mime="text/markdown",
            key="download_feedback"
        )

    # =====================================================
    # CLICKABLE SOURCE LINKS
    # =====================================================

    with links_tab:

        st.subheader("🔗 Research Sources")

        search_results = result.get(
            "search_results",
            ""
        )

        scraped_content = result.get(
            "scraped_content",
            ""
        )

        sources = extract_sources(
            str(search_results),
            str(scraped_content)
        )

        if sources:

            st.success(
                f"Found {len(sources)} unique source links."
            )

            for index, source in enumerate(
                sources,
                start=1
            ):

                with st.container(border=True):

                    col1, col2 = st.columns([4, 1])

                    with col1:

                        st.markdown(
                            f"### {index}. {source['title']}"
                        )

                        st.markdown(
                            f"<{source['url']}>"
                        )

                    with col2:

                        st.link_button(
                            "Open Source ↗",
                            source["url"],
                            use_container_width=True
                        )

            # Export the source list.
            source_text = "\n\n".join(
                f"{index}. {source['title']}\n"
                f"{source['url']}"
                for index, source in enumerate(
                    sources,
                    start=1
                )
            )

            st.download_button(
                label="📥 Download Source List",
                data=source_text,
                file_name="research_sources.txt",
                mime="text/plain",
                use_container_width=True,
                key="download_sources"
            )

        else:

            st.warning(
                "No source URLs were found in the search results "
                "or scraped content."
            )

            st.info(
                "Ensure your search agent includes original HTTP/HTTPS "
                "URLs in its output. If it returns only summaries, "
                "modify its instructions to preserve source URLs."
            )


# =========================================================
# FOOTER
# =========================================================

st.divider()

st.markdown(
    """
    <div style="
        text-align:center;
        color:#94A3B8;
        padding:15px;
        font-size:13px;
    ">
        🔬 ResearchAI | Intelligent research, simplified.
    </div>
    """,
    unsafe_allow_html=True
)




