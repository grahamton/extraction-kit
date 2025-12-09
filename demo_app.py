import streamlit as st
import subprocess
import os
import glob
import json
from azure_client_template import AzureEnrichmentClient

# Page Config
st.set_page_config(
    page_title="Extraction Middleware Demo",
    page_icon="🕸️",
    layout="wide"
)

# Title
st.title("🕸️ Extraction Middleware PoC")
st.markdown("### Enterprise-Ready Web Scraper & Markdown Converter")

# Sidebar - Config
st.sidebar.header("Configuration")

# Azure Config Section
with st.sidebar.expander("🔌 Azure OpenAI Settings", expanded=False):
    st.caption("Configure these to run enrichment directly in the app.")
    az_key = st.text_input("API Key", type="password", key="az_key")
    az_endpoint = st.text_input("Endpoint", placeholder="https://my-org.openai.azure.com/", key="az_end")
    az_deployment = st.text_input("Deployment Name", placeholder="gpt-4", key="az_dep")

prompt_path = os.path.join("config", "synthesis-prompt.md")
with st.sidebar.expander("📝 View System Prompt", expanded=False):
    if os.path.exists(prompt_path):
        with open(prompt_path, "r", encoding="utf-8") as f:
            st.sidebar.code(f.read(), language="markdown")
    else:
        st.sidebar.warning("Prompt file not found.")

st.sidebar.info("This demo runs locally. No data is sent to external clouds (unless you use the Azure Connector).")

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
            st.markdown("### Azure OpenAI Enrichment")
            st.markdown("Use your corporate Azure OpenAI credentials to synthesize the extracted content below.")

            # Get the content to start with (Raw or Full)
            full_files = glob.glob(os.path.join(latest_run, "clean", "*_full.md"))
            if full_files:
                with open(full_files[0], "r", encoding="utf-8") as f:
                    content_to_enrich = f.read()
            else:
                content_to_enrich = "No content found."

            st.text_area("Content Preview", value=content_to_enrich[:500]+"...", height=100, disabled=True)

            enrich_btn = st.button("✨ Synthesize with Azure", disabled=not (az_key and az_endpoint))

            if enrich_btn:
                if not az_key or not az_endpoint:
                    st.error("Please configure Azure settings in the Sidebar first.")
                else:
                    with st.spinner("Calling Azure OpenAI..."):
                        client = AzureEnrichmentClient(az_key, az_endpoint, az_deployment or "gpt-4")
                        summary = client.enrich_content(content_to_enrich)

                        if "Error calling Azure API" in summary:
                            st.error(summary)
                        else:
                            st.success("Enrichment Complete!")
                            st.markdown("#### Result:")
                            st.markdown(summary)
                            st.markdown("---")
                            with st.expander("View Raw JSON Response"):
                                st.json({"summary": summary})

    else:
        st.info("No runs found yet. Enter a URL above to start.")
else:
    st.warning("Data directory not found. Run a scrape first.")
