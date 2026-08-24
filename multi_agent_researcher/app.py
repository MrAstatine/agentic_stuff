import streamlit as st

from pipelines.pipeline import run_research_pipeline

DEFAULT_TOPIC = (
    "Comparison between Andaman and Nicobar Islands and Lakshadweep Islands "
    "in terms of geography, culture, biodiversity, and tourism potential."
)

st.set_page_config(
    page_title="Research Atelier",
    page_icon="RA",
    layout="wide",
    initial_sidebar_state="expanded",
)

st.markdown(
    """
	<style>
	:root { --ink: #17221f; --muted: #60716a; --accent: #d65a3a; --paper: #f5f1e8; }
	.stApp { background: var(--paper); color: var(--ink); }
	[data-testid="stSidebar"] { background: #183b35; }
	[data-testid="stSidebar"] * { color: #f5f1e8; }
	.hero { padding: 2.5rem 0 1.5rem; border-bottom: 1px solid #d8d0c0; }
	.kicker { color: var(--accent); font-size: .75rem; font-weight: 700; letter-spacing: .14em; text-transform: uppercase; }
	h1 { font-family: Georgia, serif; font-size: 5rem; line-height: .95; margin: .45rem 0 1rem; color: var(--ink); }
	.lede { color: var(--muted); font-size: 1.1rem; max-width: 42rem; }
	.stButton > button[kind="primary"] { background: var(--accent); border: 0; color: white; }
	.stDownloadButton > button { border-color: var(--accent); color: var(--accent); }
	section[data-testid="stSidebar"] .stTextArea textarea { background: var(--paper); color: var(--ink); }
	@media (max-width: 700px) { h1 { font-size: 3.2rem; } }
	</style>
	""",
    unsafe_allow_html=True,
)


def render_results(results):
    st.divider()
    st.subheader("Research desk")
    report_tab, review_tab, evidence_tab = st.tabs(
        ["Report", "Editorial review", "Evidence"]
    )
    with report_tab:
        st.markdown(results["report"])
        st.download_button(
            "Download report",
            data=results["report"],
            file_name="research-report.md",
            mime="text/markdown",
        )
    with review_tab:
        st.markdown(results["feedback"])
    with evidence_tab:
        st.caption("Search results")
        st.code(results["search_results"], language="text")
        st.caption("Scraped source summary")
        st.code(results["scraped_content"], language="text")


st.markdown(
    '<div class="hero"><div class="kicker">Multi-agent research desk</div>'
    "<h1>Turn a question<br>into a clear brief.</h1>"
    '<div class="lede">A search agent gathers the trail, a reader finds the substance, '
    "and an editor challenges the finished report.</div></div>",
    unsafe_allow_html=True,
)

with st.sidebar:
    st.markdown("### Research brief")
    st.caption("Describe the subject you want investigated.")
    with st.form("research_form"):
        topic = st.text_area("Topic", value=DEFAULT_TOPIC, height=170)
        submitted = st.form_submit_button(
            "Start research", type="primary", use_container_width=True
        )
    st.divider()
    st.caption("Uses your configured OpenRouter and Tavily credentials.")

if submitted:
    if not topic.strip():
        st.error("Enter a research topic to begin.")
    else:
        try:
            with st.status("Researching your brief...", expanded=True) as status:
                st.write("Searching, reading, writing, and reviewing")
                results = run_research_pipeline(topic.strip())
                status.update(
                    label="Research complete", state="complete", expanded=False
                )
            st.session_state["results"] = results
        except Exception as error:
            st.error(f"Research could not be completed: {error}")

if "results" in st.session_state:
    render_results(st.session_state["results"])
else:
    st.info("Your finished report will appear here after you start a research run.")
