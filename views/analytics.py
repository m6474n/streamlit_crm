"""
Analytics & Pipeline Overview View
"""
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from config import STATUS_COLORS
from utils import format_currency

def render_analytics(leads):
    """Render CRM Overview Metrics and Interactive Visualizations."""
    st.subheader("📊 Executive Lead Analytics & Pipeline")

    if not leads:
        st.info("No leads available yet. Add your first lead to see analytics!")
        return

    df = pd.DataFrame(leads)

    # Top KPI Metrics
    total_leads = len(df)
    total_value = df["estimated_value"].sum()
    won_leads = len(df[df["status"] == "Won"])
    conversion_rate = (won_leads / total_leads * 100) if total_leads > 0 else 0
    pipeline_value = df[df["status"].isin(["New", "Contacted", "Qualified", "Proposal Sent"])]["estimated_value"].sum()

    col1, col2, col3, col4 = st.columns(4)
    with col1:
        st.metric(label="Total Leads", value=total_leads)
    with col2:
        st.metric(label="Active Pipeline Value", value=format_currency(pipeline_value))
    with col3:
        st.metric(label="Won Revenue", value=format_currency(df[df["status"] == "Won"]["estimated_value"].sum()))
    with col4:
        st.metric(label="Conversion Rate", value=f"{conversion_rate:.1f}%")

    st.markdown("---")

    col_left, col_right = st.columns(2)

    with col_left:
        st.markdown("##### 🚀 Leads by Pipeline Stage")
        status_counts = df["status"].value_counts().reset_index()
        status_counts.columns = ["Status", "Count"]

        fig_stage = px.bar(
            status_counts,
            x="Status",
            y="Count",
            color="Status",
            color_discrete_map=STATUS_COLORS,
            text="Count"
        )
        fig_stage.update_layout(
            template="plotly_dark",
            showlegend=False,
            height=320,
            margin=dict(l=10, r=10, t=20, b=20)
        )
        st.plotly_chart(fig_stage, use_container_width=True)

    with col_right:
        st.markdown("##### 🌐 Lead Distribution by Source")
        source_counts = df["source"].value_counts().reset_index()
        source_counts.columns = ["Source", "Count"]

        fig_source = px.pie(
            source_counts,
            names="Source",
            values="Count",
            hole=0.4,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        fig_source.update_layout(
            template="plotly_dark",
            height=320,
            margin=dict(l=10, r=10, t=20, b=20)
        )
        st.plotly_chart(fig_source, use_container_width=True)
