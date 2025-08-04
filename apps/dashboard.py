import streamlit as st
from langfuse import get_client
import langfuse as langfuse_module
import pandas as pd
import plotly.express as px
import time
from datetime import datetime
from streamlit_autorefresh import st_autorefresh


st.set_page_config(
    page_title="Agent Admin Dashboard",
    page_icon="📊",
    layout="wide"
)

# Automatically refresh every 10 seconds
st_autorefresh(interval=10000, key="datarefresh")

try:
    langfuse_client = get_client()
except Exception as e:
    st.error(f"Langfuse error: {e}")
    st.stop()

@st.cache_data(ttl=300)
def get_traces():
    traces = []
    trace_list = langfuse_client.api.trace.list(limit=20)
    for trace_summary in trace_list.data:
        try:
            full_trace = langfuse_client.api.trace.get(trace_summary.id)
            traces.append(full_trace)
            time.sleep(0.1)
        except Exception as e:
            st.sidebar.error(f"Trace error: {e}")
            if "429" in str(e):
                break
    return traces

def render_dashboard(traces):
    if not traces:
        st.warning("No traces found. Trigger some agent calls first.")
        return

    # Build DataFrame
    trace_data = []
    for trace in traces:
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
            "Latency (s)": trace.latency if trace.latency is not None else None,
            "Observations": len(trace.observations) if trace.observations else 0,
            "Trace URL": langfuse_client.get_trace_url(trace_id=trace.id)
        })

    df = pd.DataFrame(trace_data)
    df["Timestamp"] = pd.to_datetime(df["Timestamp"])

    # Sidebar Filters
    st.sidebar.header("🔍 Filters")
    st.sidebar.info(f"Langfuse v{langfuse_module.__version__}")
    st.sidebar.markdown(f"🕒 Last Sync: {datetime.now().strftime('%H:%M:%S')}")

    lang_options = ["All"] + sorted(df["Language"].dropna().unique().tolist())
    selected_lang = st.sidebar.selectbox("Language", lang_options)
    if selected_lang != "All":
        df = df[df["Language"] == selected_lang]

    agent_options = sorted(set(agent for x in df["Agents Run"] for agent in x.split(", ") if agent))
    selected_agents = st.sidebar.multiselect("Agent(s)", agent_options)
    if selected_agents:
        df = df[df["Agents Run"].str.contains("|".join(selected_agents))]

    # KPIs
    kpi1, kpi2 = st.columns(2)
    kpi1.metric("📈 Total Traces", len(df))
    kpi2.metric("⏱️ Avg Latency (s)", f"{df['Latency (s)'].dropna().mean():.2f}" if not df['Latency (s)'].isna().all() else "N/A")

    # Tabs
    tab1, tab2, tab3, tab4 = st.tabs(["📋 Table View", "📊 Visual Analytics", "🧠 Trace Breakdown", "📝 Bookings Overview"])

    with tab1:
        st.dataframe(
            df,
            column_config={
                "Trace URL": st.column_config.LinkColumn("Trace", display_text="🔗 Open")
            },
            use_container_width=True,
            hide_index=True
        )

    with tab2:
        col1, col2 = st.columns(2)

        with col1:
            if "Agents Run" in df.columns:
                agent_counts = (
                    df["Agents Run"]
                    .str.split(", ")
                    .explode()
                    .value_counts()
                    .reset_index()
                )
                agent_counts.columns = ["Agent", "Count"]
                fig_agents = px.bar(
                    agent_counts,
                    x="Agent",
                    y="Count",
                    labels={"Agent": "Agent", "Count": "Usage Count"},
                    title="🧑‍💼 Agent Usage"
                )
                st.plotly_chart(fig_agents, use_container_width=True)

        with col2:
            if "Latency (s)" in df.columns and not df['Latency (s)'].isna().all():
                fig_latency = px.histogram(
                    df,
                    x="Latency (s)",
                    nbins=10,
                    title="⏱️ Latency Distribution"
                )
                st.plotly_chart(fig_latency, use_container_width=True)

        st.markdown("### 📅 Traces Over Time")

        if "Timestamp" in df.columns:
            df["Date"] = pd.to_datetime(df["Timestamp"]).dt.date
            daily_counts = df.groupby("Date").size().reset_index(name="Traces")
            fig_time = px.line(daily_counts, x="Date", y="Traces", title="📈 Daily Trace Count")
            st.plotly_chart(fig_time, use_container_width=True)

    with tab3:
        selected_trace = st.selectbox("Select Trace for Details", df["Trace ID"])
        selected = df[df["Trace ID"] == selected_trace].iloc[0]

        st.markdown(f"**User Query:** {selected['User Query']}")
        st.markdown(f"**Agent Response:** {selected['Agent Response']}")
        st.markdown(f"**Agents Involved:** {selected['Agents Run']}")
        st.markdown(f"**Latency:** {selected['Latency (s)']} seconds")
        st.markdown(f"[🔗 View Full Trace in Langfuse]({selected['Trace URL']})")

    with tab4:
      with tab4:
        st.markdown("## 📝 Bookings Overview")

        table_options = {
            "Room Bookings": "data/bookings.csv",
            "Room Service Orders": "data/room_service.csv",
            "Transport Bookings": "data/transport_bookings.csv"
        }

        selected_table = st.selectbox("Select Booking Table", options=list(table_options.keys()))
        file_path = table_options[selected_table]

        try:
            df_table = pd.read_csv(file_path, dtype=str, on_bad_lines='skip')  # Read all as string for editing

            # Parse 'items' column for Room Service Orders
            if selected_table == "Room Service Orders" and "items" in df_table.columns:
                import ast
                df_table["items"] = df_table["items"].apply(lambda x: ", ".join(ast.literal_eval(x)) if pd.notna(x) else "")

            st.markdown(f"### 📄 {selected_table} (Editable)")

            # If 'status' column exists, enable filtering and editing
            if "status" in df_table.columns:
                # Filter
                unique_statuses = df_table["status"].dropna().unique().tolist()
                selected_statuses = st.multiselect("Filter by Status", unique_statuses, default=unique_statuses)
                df_table = df_table[df_table["status"].isin(selected_statuses)]

                st.markdown("🖋️ **Edit Status or Sort Any Column Below**")

            # Sortable and editable table
            edited_df = st.data_editor(
                df_table,
                use_container_width=True,
                num_rows="dynamic",
                hide_index=True,
                key="editable_table",
            )

            st.metric(f"{selected_table}", len(edited_df))

            if st.button("💾 Save Changes"):
                try:
                    # Save back to CSV (overwriting original)
                    edited_df.to_csv(file_path, index=False)
                    st.success("✅ Changes saved successfully.")
                except Exception as e:
                    st.error(f"❌ Failed to save changes: {e}")

        except FileNotFoundError:
            st.error(f"❌ File not found: {file_path}")
        except Exception as e:
            st.error(f"⚠️ Error loading data: {e}")

# Run app
traces = get_traces()
render_dashboard(traces)
