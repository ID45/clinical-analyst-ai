"""
Clinical Analytics Dashboard
Interactive Streamlit dashboard for hospital KPIs
"""

import streamlit as st
import pandas as pd
import sys
import os
   
   # Add parent directory to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
   
from agents.data_loader import DataLoaderAgent
from agents.metrics_calculator import MetricsCalculatorAgent
from agents.visualizer import VisualizationAgent

# Page config
st.set_page_config(
    page_title="Clinical Analytics Dashboard",
    page_icon="🏥",
    layout="wide"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f8ff;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1f77b4;
        margin: 0.5rem 0;
    }
    .status-good {
        color: green;
        font-weight: bold;
    }
    .status-warning {
        color: orange;
        font-weight: bold;
    }
    .status-critical {
        color: red;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<h1 class="main-header">🏥 Clinical Data Analytics Dashboard</h1>', unsafe_allow_html=True)
st.markdown('<p style="text-align: center; color: #666;">AI-Powered Hospital Performance Monitoring</p>', unsafe_allow_html=True)

# Load data (cached for performance)
@st.cache_data
def load_hospital_data():
    """Load all clinical data"""
    loader = DataLoaderAgent()
    return loader.load_all_data()

@st.cache_data
def calculate_metrics(data):
    """Calculate all KPIs"""
    calculator = MetricsCalculatorAgent(data)
    return calculator.calculate_all_metrics()

# Load data
with st.spinner('Loading hospital data...'):
    data = load_hospital_data()
    metrics = calculate_metrics(data)
    visualizer = VisualizationAgent(metrics, data)

# Sidebar
with st.sidebar:
    st.header("📊 Dashboard Controls")
    
    st.markdown("---")
    
    st.header("ℹ️ About")
    st.markdown("""
    This dashboard analyzes:
    - **1,000** patient records
    - **Q1 2024** data (Jan-Mar)
    - **15** key performance indicators
    """)
    
    st.markdown("---")
    
    st.header("📈 Data Summary")
    summary = {
        'Total Patients': f"{len(data['patients']):,}",
        'Readmissions': f"{len(data['readmissions']):,}",
        'Infections': f"{len(data['infections']):,}",
        'Claims': f"{len(data['claims']):,}",
        'Appointments': f"{len(data['appointments']):,}",
        'Surveys': f"{len(data['surveys']):,}"
    }
    
    for key, value in summary.items():
        st.metric(key, value)
    
    st.markdown("---")
    
    st.markdown("**Built with:**")
    st.markdown("• Python")
    st.markdown("• Streamlit")
    st.markdown("• Plotly")
    st.markdown("• Pandas")

# Main content - Tabs
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "📊 Executive Summary",
    "🏥 Clinical Quality",
    "⚙️ Operations",
    "💰 Financial",
    "😊 Patient Experience"
])

# TAB 1: Executive Summary
with tab1:
    st.header("Executive Summary")
    st.markdown("**Q1 2024 Hospital Performance Overview**")
    
    # Key metrics in columns
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "30-Day Readmission",
            f"{metrics['readmission_rate']['value']:.1f}%",
            f"{metrics['readmission_rate']['value'] - metrics['readmission_rate']['benchmark']:.1f}%",
            delta_color="inverse"
        )
    
    with col2:
        st.metric(
            "HAI Rate",
            f"{metrics['infection_rate']['value']:.2f}/1000",
            f"{metrics['infection_rate']['value'] - metrics['infection_rate']['benchmark']:.2f}",
            delta_color="inverse"
        )
    
    with col3:
        st.metric(
            "Patient Satisfaction",
            f"{metrics['satisfaction']['value']:.1f}/10",
            f"{metrics['satisfaction']['value'] - metrics['satisfaction']['benchmark']:.1f}",
            delta_color="normal"
        )
    
    with col4:
        st.metric(
            "Collection Rate",
            f"{metrics['collection_rate']['value']:.1f}%",
            f"{metrics['collection_rate']['value'] - metrics['collection_rate']['benchmark']:.1f}%",
            delta_color="normal"
        )
    
    st.markdown("---")
    
    # KPI Summary Chart
    st.subheader("All KPIs vs. Benchmarks")
    fig_kpi = visualizer.create_kpi_summary_chart()
    st.plotly_chart(fig_kpi, use_container_width=True)
    
    st.markdown("---")
    
    # Key insights
    st.subheader("🎯 Key Insights")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**✅ Strengths:**")
        st.markdown("- Low mortality rate (1.4%)")
        st.markdown("- Efficient length of stay (3.7 days)")
        st.markdown("- High patient satisfaction (8.2/10)")
        st.markdown("- Excellent collection rate (96%)")
    
    with col2:
        st.markdown("**⚠️ Areas for Improvement:**")
        st.markdown("- **CRITICAL:** HAI rate 9x benchmark!")
        st.markdown("- High no-show rate (10.6%)")
        st.markdown("- High claim denial rate (8.9%)")
        st.markdown("- Bed underutilization")

# TAB 2: Clinical Quality
with tab2:
    st.header("Clinical Quality & Outcomes")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("30-Day Readmission Rate")
        st.metric(
            "Current Rate",
            f"{metrics['readmission_rate']['value']:.1f}%",
            f"Benchmark: {metrics['readmission_rate']['benchmark']}%"
        )
        st.markdown(f"**Total Readmissions:** {metrics['readmission_rate']['readmissions']}")
        st.markdown(f"**Total Discharges:** {metrics['readmission_rate']['total_discharges']}")
        
        if metrics['readmission_rate']['status'] == 'warning':
            st.warning("⚠️ Above benchmark - Review discharge planning processes")
    
    with col2:
        st.subheader("Healthcare-Associated Infections")
        st.metric(
            "HAI Rate",
            f"{metrics['infection_rate']['value']:.2f} per 1000 days",
            f"Benchmark: {metrics['infection_rate']['benchmark']}"
        )
        st.markdown(f"**Total HAI Cases:** {metrics['infection_rate']['cases']}")
        st.markdown(f"**Patient Days:** {metrics['infection_rate']['patient_days']:,}")
        
        if metrics['infection_rate']['status'] == 'critical':
            st.error("❌ CRITICAL - Immediate infection control review needed!")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Mortality Rate")
        st.metric(
            "Inpatient Mortality",
            f"{metrics['mortality_rate']['value']:.1f}%",
            f"Benchmark: {metrics['mortality_rate']['benchmark']}%"
        )
        st.markdown(f"**Deaths:** {metrics['mortality_rate']['deaths']}")
        
        if metrics['mortality_rate']['status'] == 'good':
            st.success("✅ Below national benchmark")
    
    with col2:
        st.subheader("Average Length of Stay")
        st.metric(
            "ALOS",
            f"{metrics['alos']['value']:.1f} days",
            f"Benchmark: {metrics['alos']['benchmark']} days"
        )
        st.markdown(f"**Median:** {metrics['alos']['median']} days")
        st.markdown(f"**Range:** {metrics['alos']['min']}-{metrics['alos']['max']} days")
        
        if metrics['alos']['status'] == 'efficient':
            st.success("✅ Efficient patient throughput")
    
    st.markdown("---")
    
    # Department performance
    st.subheader("Performance by Department")
    fig_dept = visualizer.create_department_performance_chart()
    st.plotly_chart(fig_dept, use_container_width=True)

# TAB 3: Operations
with tab3:
    st.header("Operational Efficiency")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Bed Turnover Rate")
        st.metric(
            "Turnover Rate",
            f"{metrics['bed_turnover']['value']:.2f}",
            f"Benchmark: {metrics['bed_turnover']['benchmark']}"
        )
        utilization = (metrics['bed_turnover']['value'] / metrics['bed_turnover']['benchmark']) * 100
        st.markdown(f"**Bed Utilization:** {utilization:.0f}% of benchmark")
        
        if metrics['bed_turnover']['status'] == 'underutilized':
            st.warning("⚠️ Beds underutilized - Consider capacity optimization")
    
    with col2:
        st.subheader("Patient Wait Times")
        st.metric(
            "Average Wait",
            f"{metrics['wait_time']['value']:.0f} minutes",
            f"Benchmark: {metrics['wait_time']['benchmark']} min"
        )
        st.markdown(f"**Median:** {metrics['wait_time']['median']:.0f} minutes")
        st.markdown(f"**90th Percentile:** {metrics['wait_time']['p90']:.0f} minutes")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Appointment No-Show Rate")
        st.metric(
            "No-Show Rate",
            f"{metrics['no_show_rate']['value']:.1f}%",
            f"Benchmark: {metrics['no_show_rate']['benchmark']}%"
        )
        st.markdown(f"**No-Shows:** {metrics['no_show_rate']['no_shows']}")
        st.markdown(f"**Total Appointments:** {metrics['no_show_rate']['total_appointments']}")
        
        if metrics['no_show_rate']['status'] == 'high':
            st.error("❌ High no-show rate - Implement reminder system")
    
    with col2:
        st.subheader("ER Wait Time")
        st.metric(
            "Average ER Wait",
            f"{metrics['er_wait_time']['value']} minutes",
            f"Benchmark: {metrics['er_wait_time']['benchmark']} min"
        )
        st.markdown(f"**ER Visits:** {metrics['er_wait_time']['er_visits']}")

# TAB 4: Financial
with tab4:
    st.header("Financial & Revenue Cycle")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Claim Denial Rate")
        st.metric(
            "Denial Rate",
            f"{metrics['denial_rate']['value']:.1f}%",
            f"Benchmark: {metrics['denial_rate']['benchmark']}%"
        )
        st.markdown(f"**Denied Claims:** {metrics['denial_rate']['denied_claims']}")
        st.markdown(f"**Total Claims:** {metrics['denial_rate']['total_claims']}")
        
        if metrics['denial_rate']['status'] == 'critical':
            st.error("❌ High denial rate - Revenue loss opportunity")
    
    with col2:
        st.subheader("Days in A/R")
        st.metric(
            "Average Days",
            f"{metrics['days_in_ar']['value']:.0f} days",
            f"Benchmark: {metrics['days_in_ar']['benchmark']} days"
        )
        
        if metrics['days_in_ar']['status'] == 'slow':
            st.warning("⚠️ Slow collections - Cash flow impact")
    
    st.markdown("---")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Average Cost per Visit")
        st.metric(
            "Cost per Visit",
            f"${metrics['cost_per_visit']['value']:,.0f}"
        )
        st.markdown(f"**Median:** ${metrics['cost_per_visit']['median']:,.0f}")
    
    with col2:
        st.subheader("Net Collection Rate")
        st.metric(
            "Collection Rate",
            f"{metrics['collection_rate']['value']:.1f}%",
            f"Benchmark: {metrics['collection_rate']['benchmark']}%"
        )
        st.markdown(f"**Collected:** ${metrics['collection_rate']['collected']:,.0f}")
        st.markdown(f"**Allowed:** ${metrics['collection_rate']['allowed']:,.0f}")
        
        if metrics['collection_rate']['status'] == 'excellent':
            st.success("✅ Excellent collections performance")
    
    st.markdown("---")
    
    # Financial charts
    st.subheader("Financial Overview")
    fig_financial = visualizer.create_financial_overview_chart()
    st.plotly_chart(fig_financial, use_container_width=True)

# TAB 5: Patient Experience
with tab5:
    st.header("Patient Experience & Data Quality")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Patient Satisfaction (HCAHPS)")
        st.metric(
            "Overall Satisfaction",
            f"{metrics['satisfaction']['value']:.1f}/10",
            f"Benchmark: {metrics['satisfaction']['benchmark']}/10"
        )
        st.markdown(f"**Survey Responses:** {metrics['satisfaction']['response_count']}")
        
        if metrics['satisfaction']['status'] == 'excellent':
            st.success("✅ Excellent patient experience scores")
    
    with col2:
        st.subheader("Data Quality")
        st.metric(
            "Data Completeness",
            f"{metrics['data_quality']['value']:.1f}%"
        )
        st.markdown(f"**Status:** {metrics['data_quality']['status'].upper()}")
        
        if metrics['data_quality']['status'] == 'excellent':
            st.success("✅ High-quality data for analytics")
    
    st.markdown("---")
    
    # Satisfaction distribution
    st.subheader("Patient Satisfaction Score Distribution")
    fig_satisfaction = visualizer.create_patient_satisfaction_chart()
    st.plotly_chart(fig_satisfaction, use_container_width=True)

# Footer
st.markdown("---")
st.markdown("""
<div style='text-align: center; color: #666; font-size: 0.9rem;'>
    <p>Clinical Data Analytics Dashboard v1.0 | Built with AI Agents | Q1 2024 Data</p>
</div>
""", unsafe_allow_html=True)