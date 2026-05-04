"""
Clinical Analyst AI - Streamlit Dashboard
"""

import sys
import os
import pandas as pd
import streamlit as st
# Auto-generate sample data if CSV files are missing
if not os.path.exists("data/sample_data/patients.csv"):
    os.makedirs("data/sample_data", exist_ok=True)
    exec(open(os.path.join(os.path.dirname(__file__), "generate_sample_data.py")).read())

sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'agents'))

from data_loader import DataLoaderAgent
from metrics_calculator import MetricsCalculatorAgent
from visualizer import VisualizationAgent
from insights_generator import InsightsGeneratorAgent

st.set_page_config(
    page_title="Clinical Analyst AI",
    page_icon="🏥",
    layout="wide",
)

# ── CSV upload specs ──────────────────────────────────────────────────────────

FILE_SPECS = {
    "patients": {
        "label": "Patients",
        "description": "Inpatient admission records",
        "required_cols": ["patient_id", "admission_date", "discharge_date", "length_of_stay", "department", "discharge_status"],
        "date_cols": ["admission_date", "discharge_date"],
    },
    "readmissions": {
        "label": "Readmissions",
        "description": "30-day readmission events",
        "required_cols": ["patient_id", "original_discharge", "readmission_date", "days_between"],
        "date_cols": ["original_discharge", "readmission_date"],
    },
    "infections": {
        "label": "Infections",
        "description": "Healthcare-associated infection cases",
        "required_cols": ["patient_id", "department", "infection_type", "onset_date"],
        "date_cols": ["onset_date"],
    },
    "claims": {
        "label": "Claims",
        "description": "Insurance claims and billing records",
        "required_cols": ["claim_id", "patient_id", "claim_status", "claim_amount", "allowed_amount", "paid_amount", "submission_date", "payment_date", "denial_reason"],
        "date_cols": ["submission_date", "payment_date"],
    },
    "appointments": {
        "label": "Appointments",
        "description": "Outpatient appointment records",
        "required_cols": ["appointment_id", "patient_id", "scheduled_time", "status", "wait_time_minutes"],
        "date_cols": ["scheduled_time"],
    },
    "surveys": {
        "label": "Surveys",
        "description": "Patient satisfaction surveys",
        "required_cols": ["survey_id", "patient_id", "survey_date", "overall_satisfaction"],
        "date_cols": ["survey_date"],
    },
}

# ── Sample data loader (cached) ───────────────────────────────────────────────

@st.cache_resource(show_spinner="Loading sample data...")
def load_sample_data():
    loader = DataLoaderAgent()
    data = loader.load_all_data()
    if data is None:
        return None, None
    metrics = MetricsCalculatorAgent(data).calculate_all_metrics()
    return data, metrics

# ── Helpers ───────────────────────────────────────────────────────────────────

def parse_uploaded_file(uploaded_file, key):
    spec = FILE_SPECS[key]
    try:
        df = pd.read_csv(uploaded_file)
    except Exception as e:
        return None, f"Could not read file: {e}"

    missing = [c for c in spec["required_cols"] if c not in df.columns]
    if missing:
        return None, f"Missing columns: {', '.join(missing)}"

    for col in spec["date_cols"]:
        if col in df.columns:
            try:
                df[col] = pd.to_datetime(df[col])
            except Exception:
                return None, f"Could not parse dates in column '{col}'"

    return df, None


def metric_card(label, metric_dict, unit="", higher_is_better=False):
    value = metric_dict.get('value', 'N/A')
    benchmark = metric_dict.get('benchmark')

    delta_str = None
    delta_color = 'normal'
    if benchmark is not None and isinstance(value, (int, float)):
        diff = value - benchmark
        sign = "+" if diff > 0 else ""
        delta_str = f"{sign}{diff:.1f}{unit} vs benchmark"
        if higher_is_better:
            delta_color = 'normal' if diff >= 0 else 'inverse'
        else:
            delta_color = 'inverse' if diff > 0 else 'normal'

    st.metric(
        label=label,
        value=f"{value}{unit}" if isinstance(value, (int, float)) else value,
        delta=delta_str,
        delta_color=delta_color,
    )

# ── Sidebar ───────────────────────────────────────────────────────────────────

st.sidebar.title("🏥 Clinical Analyst AI")
page = st.sidebar.radio(
    "Navigate",
    ["Dashboard", "Clinical Quality", "Operations", "Financial",
     "Patient Experience", "AI Insights", "Chat", "Upload Data"],
)

if page == "Chat" and st.sidebar.button("Clear chat history"):
    st.session_state.chat_history = []

# Data source badge
if st.session_state.get("uploaded_data"):
    st.sidebar.success("Using: Uploaded Data")
    if st.sidebar.button("Switch back to sample data"):
        del st.session_state["uploaded_data"]
        del st.session_state["uploaded_metrics"]
        st.rerun()
else:
    st.sidebar.info("Using: Sample Data")

# ── Active data resolution ────────────────────────────────────────────────────

if st.session_state.get("uploaded_data") and st.session_state.get("uploaded_metrics"):
    data = st.session_state.uploaded_data
    metrics = st.session_state.uploaded_metrics
else:
    data, metrics = load_sample_data()

if data is None or metrics is None:
    st.error(
        "Failed to load sample data. Make sure `data/sample_data/` exists with "
        "patients, readmissions, infections, claims, appointments, and surveys CSV files."
    )
    st.stop()

# ── Pages ─────────────────────────────────────────────────────────────────────

if page == "Dashboard":
    st.title("Hospital Performance Dashboard")
    st.caption(f"Patients: {len(data['patients']):,} | Claims: {len(data['claims']):,} | Appointments: {len(data['appointments']):,}")

    st.subheader("Key Performance Indicators")
    cols = st.columns(4)
    with cols[0]:
        metric_card("30-Day Readmission", metrics['readmission_rate'], unit="%")
    with cols[1]:
        metric_card("HAI Rate (per 1,000)", metrics['infection_rate'])
    with cols[2]:
        metric_card("Claim Denial Rate", metrics['denial_rate'], unit="%")
    with cols[3]:
        metric_card("Patient Satisfaction", metrics['satisfaction'], unit="/10", higher_is_better=True)

    st.divider()
    visualizer = VisualizationAgent(metrics, data)
    st.plotly_chart(visualizer.create_kpi_summary_chart(), use_container_width=True)

elif page == "Clinical Quality":
    st.title("Clinical Quality & Outcomes")

    cols = st.columns(4)
    with cols[0]:
        metric_card("30-Day Readmission", metrics['readmission_rate'], unit="%")
    with cols[1]:
        metric_card("HAI Rate (per 1,000)", metrics['infection_rate'])
    with cols[2]:
        metric_card("Mortality Rate", metrics['mortality_rate'], unit="%")
    with cols[3]:
        metric_card("Avg Length of Stay", metrics['alos'], unit=" days")

    st.divider()
    visualizer = VisualizationAgent(metrics, data)
    st.plotly_chart(visualizer.create_department_performance_chart(), use_container_width=True)

elif page == "Operations":
    st.title("Operational Efficiency")

    cols = st.columns(4)
    with cols[0]:
        metric_card("Bed Turnover Rate", metrics['bed_turnover'], higher_is_better=True)
    with cols[1]:
        metric_card("Avg Wait Time", metrics['wait_time'], unit=" min")
    with cols[2]:
        metric_card("No-Show Rate", metrics['no_show_rate'], unit="%")
    with cols[3]:
        metric_card("ER Wait Time", metrics['er_wait_time'], unit=" min")

    st.divider()
    st.subheader("Appointment Status Breakdown")
    appt_status = data['appointments']['status'].value_counts().reset_index()
    appt_status.columns = ['Status', 'Count']
    st.bar_chart(appt_status.set_index('Status'))

elif page == "Financial":
    st.title("Financial & Revenue Cycle")

    cols = st.columns(4)
    with cols[0]:
        metric_card("Claim Denial Rate", metrics['denial_rate'], unit="%")
    with cols[1]:
        metric_card("Days in A/R", metrics['days_in_ar'], unit=" days")
    with cols[2]:
        metric_card("Collection Rate", metrics['collection_rate'], unit="%", higher_is_better=True)
    with cols[3]:
        cpv = metrics.get('cost_per_visit', {})
        cpv_val = cpv.get('value')
        st.metric("Avg Cost per Visit", f"${cpv_val:,.0f}" if isinstance(cpv_val, (int, float)) else "N/A")

    st.divider()
    visualizer = VisualizationAgent(metrics, data)
    st.plotly_chart(visualizer.create_financial_overview_chart(), use_container_width=True)

elif page == "Patient Experience":
    st.title("Patient Experience")

    cols = st.columns(3)
    with cols[0]:
        metric_card("Overall Satisfaction", metrics['satisfaction'], unit="/10", higher_is_better=True)
    with cols[1]:
        st.metric("Survey Responses", f"{metrics['satisfaction'].get('response_count', 'N/A'):,}")
    with cols[2]:
        metric_card("Avg Wait Time", metrics['wait_time'], unit=" min")

    st.divider()
    visualizer = VisualizationAgent(metrics, data)
    st.plotly_chart(visualizer.create_patient_satisfaction_chart(), use_container_width=True)

elif page == "AI Insights":
    st.title("AI-Powered Insights")

    if not os.getenv("OPENAI_API_KEY"):
        st.error("Set your `OPENAI_API_KEY` in the `.env` file to use AI insights.")
        st.stop()

    insights = InsightsGeneratorAgent(metrics, data)

    tab1, tab2, tab3, tab4 = st.tabs(
        ["Executive Summary", "Metric Deep-Dive", "Custom Question", "Action Plan"]
    )

    with tab1:
        st.subheader("Executive Summary")
        if st.button("Generate Executive Summary", type="primary"):
            with st.spinner("Generating summary..."):
                summary = insights.generate_executive_summary()
            st.markdown(summary)

    with tab2:
        st.subheader("Metric Deep-Dive")
        metric_options = [
            'readmission_rate', 'infection_rate', 'mortality_rate', 'alos',
            'bed_turnover', 'wait_time', 'no_show_rate', 'er_wait_time',
            'denial_rate', 'days_in_ar', 'collection_rate', 'satisfaction',
        ]
        selected_metric = st.selectbox("Select a metric to analyze", metric_options)
        custom_q = st.text_input("Optional: ask a specific question about this metric")
        if st.button("Analyze Metric", type="primary"):
            with st.spinner(f"Analyzing {selected_metric}..."):
                result = insights.analyze_specific_metric(selected_metric, custom_q or None)
            st.markdown(result)

    with tab3:
        st.subheader("Ask Anything")
        question = st.text_area(
            "Ask a question about the hospital data",
            placeholder="e.g. Which department has the highest readmission risk?",
        )
        if st.button("Get Answer", type="primary") and question:
            with st.spinner("Thinking..."):
                answer = insights.answer_custom_question(question)
            st.markdown(answer)

    with tab4:
        st.subheader("90-Day Action Plan")
        focus_options = ["Clinical Quality", "Operations", "Financial", "Patient Experience"]
        focus_area = st.selectbox("Select focus area", focus_options)
        if st.button("Generate Action Plan", type="primary"):
            with st.spinner("Building action plan..."):
                plan = insights.generate_action_plan(focus_area)
            st.markdown(plan)

elif page == "Chat":
    st.title("Ask the Clinical Analyst")
    st.caption("Ask any question about hospital metrics, performance, or trends.")

    if not os.getenv("OPENAI_API_KEY"):
        st.error("Set your `OPENAI_API_KEY` in the `.env` file to use the chat.")
        st.stop()

    insights = InsightsGeneratorAgent(metrics, data)

    if "chat_history" not in st.session_state:
        st.session_state.chat_history = []

    if not st.session_state.chat_history:
        st.markdown("**Suggested questions:**")
        suggestions = [
            "What are the top 3 areas needing immediate improvement?",
            "Which department has the highest readmission rate?",
            "Why is our claim denial rate high and how do we fix it?",
            "How does our patient satisfaction compare to benchmark?",
            "What is driving our ER wait times?",
        ]
        cols = st.columns(len(suggestions))
        for col, suggestion in zip(cols, suggestions):
            with col:
                if st.button(suggestion, use_container_width=True):
                    st.session_state.chat_history.append({"role": "user", "content": suggestion})
                    with st.spinner("Thinking..."):
                        response = insights.answer_custom_question(suggestion)
                    st.session_state.chat_history.append({"role": "assistant", "content": response})
                    st.rerun()

    for msg in st.session_state.chat_history:
        with st.chat_message(msg["role"], avatar="🧑" if msg["role"] == "user" else "🏥"):
            st.markdown(msg["content"])

    if prompt := st.chat_input("Ask about any metric or hospital performance area..."):
        st.session_state.chat_history.append({"role": "user", "content": prompt})
        with st.chat_message("user", avatar="🧑"):
            st.markdown(prompt)
        with st.chat_message("assistant", avatar="🏥"):
            with st.spinner("Thinking..."):
                response = insights.answer_custom_question(prompt)
            st.markdown(response)
        st.session_state.chat_history.append({"role": "assistant", "content": response})

elif page == "Upload Data":
    st.title("Upload Your Data")
    st.markdown(
        "Upload your own CSV files to replace the sample data. "
        "You can upload any combination — missing files will fall back to sample data."
    )

    sample_data, _ = load_sample_data()
    uploaded_frames = {}
    validation_errors = {}

    st.divider()

    for key, spec in FILE_SPECS.items():
        with st.expander(f"**{spec['label']}** — {spec['description']}", expanded=False):
            st.caption("Required columns: `" + "`, `".join(spec["required_cols"]) + "`")

            uploaded_file = st.file_uploader(
                f"Upload {spec['label']} CSV",
                type="csv",
                key=f"upload_{key}",
            )

            if uploaded_file:
                df, error = parse_uploaded_file(uploaded_file, key)
                if error:
                    st.error(f"{error}")
                    validation_errors[key] = error
                else:
                    uploaded_frames[key] = df
                    st.success(f"{len(df):,} rows loaded successfully.")
                    st.dataframe(df.head(5), use_container_width=True)
            elif sample_data and key in sample_data:
                st.info(f"No file uploaded — using sample data ({len(sample_data[key]):,} rows).")

    st.divider()

    n_uploaded = len(uploaded_frames)
    n_errors = len(validation_errors)

    if n_uploaded > 0:
        if n_errors > 0:
            st.warning(f"{n_uploaded} file(s) ready, {n_errors} file(s) have errors (fix errors before running analysis).")
        else:
            st.success(f"{n_uploaded} of 6 file(s) uploaded and validated.")

        if st.button("Run Analysis on Uploaded Data", type="primary", disabled=(n_errors > 0)):
            # Merge uploaded files with sample data fallback
            merged = {}
            for key in FILE_SPECS:
                if key in uploaded_frames:
                    merged[key] = uploaded_frames[key]
                elif sample_data and key in sample_data:
                    merged[key] = sample_data[key]
                else:
                    st.error(f"No data available for '{key}'. Upload the file or ensure sample data exists.")
                    st.stop()

            with st.spinner("Calculating metrics..."):
                try:
                    new_metrics = MetricsCalculatorAgent(merged).calculate_all_metrics()
                    st.session_state.uploaded_data = merged
                    st.session_state.uploaded_metrics = new_metrics
                    st.session_state.chat_history = []  # reset chat for new dataset
                    st.success("Analysis complete! All pages now reflect your uploaded data.")
                    st.balloons()
                except Exception as e:
                    st.error(f"Failed to calculate metrics: {e}")
    else:
        st.info("Upload at least one CSV file above, then click **Run Analysis**.")

    # Show current data summary
    st.divider()
    st.subheader("Current Data Summary")
    summary_cols = st.columns(3)
    labels = [
        ("Patients", "patients"), ("Readmissions", "readmissions"), ("Infections", "infections"),
        ("Claims", "claims"), ("Appointments", "appointments"), ("Surveys", "surveys"),
    ]
    for i, (label, key) in enumerate(labels):
        with summary_cols[i % 3]:
            source = "Uploaded" if st.session_state.get("uploaded_data") and key in st.session_state.uploaded_data else "Sample"
            count = len(data.get(key, []))
            st.metric(label, f"{count:,}", delta=source, delta_color="normal" if source == "Uploaded" else "off")
