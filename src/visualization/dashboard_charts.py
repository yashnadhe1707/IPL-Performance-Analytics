"""
Dashboard Visualizations Module.
Builds general overview charts, venue scoring distributions,
and correlation heatmaps.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict

def plot_toss_distribution_donut(toss_dict: Dict) -> go.Figure:
    if not toss_dict:
        return go.Figure()
    labels = ["Field First", "Bat First"]
    values = [toss_dict.get("field_count", 0), toss_dict.get("bat_count", 0)]
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.5,
            marker=dict(colors=["#3B82F6", "#10B981"]),
            textinfo="label+value+percent"
        )
    )
    fig.update_layout(
        title="Toss Decision Preferences (Bat vs Field)",
        height=360,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def plot_venue_scoring_bar(df_venues: pd.DataFrame, top_n: int = 10) -> go.Figure:
    if df_venues.empty or "Avg Innings Score" not in df_venues.columns:
        return go.Figure()
    top_venues = df_venues.head(top_n).sort_values(by="Avg Innings Score", ascending=True)
    fig = px.bar(
        top_venues,
        x="Avg Innings Score",
        y="Venue",
        orientation="h",
        text="Avg Innings Score",
        title=f"Average Innings Score by Venue (Top {top_n} Most Frequented Grounds)",
        color="Avg Innings Score",
        color_continuous_scale="Viridis"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=450, margin=dict(l=20, r=40, t=50, b=20), coloraxis_showscale=False)
    return fig

def plot_correlation_heatmap(corr_df: pd.DataFrame) -> go.Figure:
    if corr_df.empty:
        return go.Figure()
    fig = px.imshow(
        corr_df,
        text_auto=True,
        aspect="auto",
        color_continuous_scale="RdBu_r",
        title="Metric Correlation Heatmap (Pearson Correlation Matrix)"
    )
    fig.update_layout(height=420, margin=dict(l=20, r=20, t=50, b=20))
    return fig
