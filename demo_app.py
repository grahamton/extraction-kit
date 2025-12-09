import streamlit as st
import subprocess
import os
import glob
import json

# Page Config
st.set_page_config(
    page_title="Extraction Middleware Demo",
    page_icon="🕸️",
    layout="wide"
)

# Title
st.title("🕸️ Extraction Middleware PoC")
st.markdown("### Enterprise-Ready Web Scraper & Markdown Converter")

# Sidebar - Config & Prompts
st.sidebar.header("Configuration")
with st.sidebar.expander("View System Prompt"):
    prompt_path = os.path.join("config", "synthesis-prompt.md")
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            st.sidebar.code(f.read(), language="markdown")
    else:
        st.sidebar.warning("Prompt file not found.")

st.sidebar.info("This demo runs locally. No data is sent to external clouds.")

# Main Workflow
col1, col2 = st.columns([2, 1])

with col1:
    url_input = st.text_input("Target URL", placeholder="https://example.com")
    run_btn = st.button("🚀 Run Extraction Pipeline", type="primary")

    if run_btn and url_input:
        with st.status("Running Middleware Pipeline...", expanded=True) as status:
            st.write("🌐 Connecting towards target...")

            # Run the extraction runner as a subprocess
            cmd = ["python", "local_extraction_runner.py", "--url", url_input]
            result = subprocess.run(cmd, capture_output=True, text=True)

            if result.returncode == 0:
                st.write("✅ Scraping & Text Extraction Complete")
                st.write("📄 Saving Raw Markdown...")
                st.write("✂️  Chunking Content...")
                status.update(label="Extraction Complete!", state="complete", expanded=False)
                st.success("Pipeline Finished Successfully.")
            else:
                status.update(label="Extraction Failed", state="error")
                st.error("Error running pipeline:")
                st.code(result.stderr)

# Results Viewer
st.markdown("---")
st.header("📦 Pipeline Output")

# Find latest run
scrapes_dir = os.path.join("data", "scrapes")
if os.path.exists(scrapes_dir):
    # Find latest run folder by name (timestamped)
    runs = sorted(glob.glob(os.path.join(scrapes_dir, "*_run")), reverse=True)

    if runs:
        latest_run = runs[0]
        st.caption(f"Showing results for Run ID: `{os.path.basename(latest_run)}`")

        # Tabs for Raw vs Clean
        tab1, tab2, tab3 = st.tabs(["📄 Raw Markdown", "📚 Chunked Content", "🔌 Azure Integration"])

        with tab1:
            raw_files = glob.glob(os.path.join(latest_run, "raw", "*_raw.md"))
            if raw_files:
                for rf in raw_files:
                    with open(rf, "r", encoding="utf-8") as f:
                        st.code(f.read(), language="markdown")
            else:
                st.info("No raw files found.")

        with tab2:
            clean_files = glob.glob(os.path.join(latest_run, "clean", "*.md"))
            if clean_files:
                for cf in clean_files:
                    with st.expander(os.path.basename(cf), expanded=False):
                        with open(cf, "r", encoding="utf-8") as f:
                            st.markdown(f.read())
            else:
                st.info("No clean files found.")

        with tab3:
            st.markdown("### Ready for Azure OpenAI")
            st.markdown("The content above is now clean, structured Markdown ready to be sent to the Azure OpenAI API.")

            st.code("""
# Example Integration
from azure_client_template import AzureEnrichmentClient

client = AzureEnrichmentClient(
    api_key="YOUR_KEY",
    endpoint="YOUR_ENDPOINT",
    deployment="gpt-4"
)

# processed_content comes from the scraper above
summary = client.enrich_content(processed_content)
print(summary)
            """, language="python")

    else:
        st.info("No runs found yet. Enter a URL above to start.")
else:
    st.warning("Data directory not found. Run a scrape first.")
