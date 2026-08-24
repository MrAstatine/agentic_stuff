"""Legacy command-line entry point; use app.py for the Streamlit application."""

from .pipelines.pipeline import run_research_pipeline

if __name__ == "__main__":
    topic = (
        "Comparison between Andaman and Nicobar Islands and Lakshadweep Islands "
        "in terms of geography, culture, biodiversity, and tourism potential."
    )
    run_research_pipeline(topic)
