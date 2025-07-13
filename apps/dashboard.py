import streamlit as st
from langfuse import get_client
import langfuse as langfuse_module
import pandas as pd
import time

st.set_page_config(
    page_title="Agent Admin Dashboard",
    page_icon="📊",
    layout="wide"
)

try:
    langfuse_client = get_client()
except Exception as e:
    st.error(f"Failed to initialize Langfuse client. Make sure your .env file is configured correctly. Error: {e}")
    st.stop()

@st.cache_data(ttl=300)
def get_traces():
    """Fetches all traces from Langfuse."""
    full_traces = []
    # 1. List traces to get their IDs. The list method returns a lightweight object.
    trace_list = langfuse_client.api.trace.list(limit=20) # Adjust limit as needed
    
    # 2. Fetch each trace individually to get the full object with metadata.
    for trace_summary in trace_list.data:
        try:
            # The full trace object from .get() has the metadata attribute.
            full_trace = langfuse_client.api.trace.get(trace_summary.id)
            full_traces.append(full_trace)
            # Add a small delay to avoid hitting API rate limits.
            time.sleep(0.1) # 100ms delay
        except Exception as e:
            st.sidebar.error(f"Failed to load trace {trace_summary.id}: {e}")
            # If we hit a rate limit, it's best to stop trying.
            if "429" in str(e):
                st.sidebar.error("Rate limit exceeded. Stopping trace fetch.")
                break
    return full_traces

def render_dashboard(traces):
    if not traces:
        st.warning("No traces found. Run your agent to generate some data.")
        return

    trace_data = []
    for trace in traces:
        # Defensively access input/output, as they can be None for incomplete traces
        trace_input = trace.input or {}
        trace_output = trace.output or {}
        metadata = trace.metadata or {}
        trace_data.append({
            "Trace ID": trace.id,
            "Timestamp": trace.timestamp,
            "Language": trace_input.get("detected_language", "N/A"),
            "User Query": trace_input.get("original_query", "N/A"),
            "Agent Response": trace_output.get("aggregated_output", "N/A"),
            "Intents": ", ".join(trace_output.get("intents") or []),
            "Agents Run": ", ".join(trace_output.get("processed_intents") or []),
            "No. of Observations": len(trace.observations) if trace.observations else 0,
            "Trace URL": langfuse_client.get_trace_url(trace_id=trace.id)  # Use the SDK method
        })

    df = pd.DataFrame(trace_data)
    st.sidebar.header("Filters")
    st.sidebar.info(f"Langfuse Version: {langfuse_module.__version__}")

    # Filter out None values from the list before sorting to prevent the TypeError.
    unique_langs = [lang for lang in df["Language"].unique().tolist() if lang is not None]
    languages = ["All"] + sorted(unique_langs)
    selected_language = st.sidebar.selectbox("Filter by Language", options=languages)
    if selected_language != "All":
        df = df[df["Language"] == selected_language]

    all_agents = sorted(list(set(agent for agents in df["Agents Run"] for agent in agents.split(", ") if agent)))
    selected_agent = st.sidebar.multiselect("Filter by Agent Run", options=all_agents)
    if selected_agent:
        df = df[df["Agents Run"].str.contains("|".join(selected_agent))]

    st.title("📊 Agent Admin Dashboard")
    st.markdown("An overview of agent interactions, powered by Langfuse traces.")
    st.dataframe(
        df,
        column_config={
            "Trace URL": st.column_config.LinkColumn("View Trace", display_text="🔗 Open")
        },
        hide_index=True,
        use_container_width=True
    )
    st.info(f"Displaying {len(df)} of {len(traces)} total traces.")

traces = get_traces()
render_dashboard(traces)