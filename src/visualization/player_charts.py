"""
Player Visualizations Module.
Builds interactive Plotly visualizations for player performance,
strike-rate distributions, and multi-player comparisons.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Dict

def plot_top_batsmen_bar(df_batsmen: pd.DataFrame, top_n: int = 10) -> go.Figure:
    if df_batsmen.empty:
        return go.Figure()
    top_df = df_batsmen.head(top_n).sort_values(by="Runs", ascending=True)
    fig = px.bar(
        top_df,
        x="Runs",
        y="Batsman",
        orientation="h",
        text="Runs",
        title=f"Top {top_n} Run Scorers",
        labels={"Runs": "Total Runs Scored", "Batsman": "Player"},
        color="Runs",
        color_continuous_scale="Viridis"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=450, margin=dict(l=20, r=40, t=50, b=20), coloraxis_showscale=False)
    return fig

def plot_top_bowlers_bar(df_bowlers: pd.DataFrame, top_n: int = 10) -> go.Figure:
    if df_bowlers.empty:
        return go.Figure()
    top_df = df_bowlers.head(top_n).sort_values(by="Wickets", ascending=True)
    fig = px.bar(
        top_df,
        x="Wickets",
        y="Bowler",
        orientation="h",
        text="Wickets",
        title=f"Top {top_n} Wicket Takers",
        labels={"Wickets": "Total Wickets", "Bowler": "Player"},
        color="Wickets",
        color_continuous_scale="Purples"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=450, margin=dict(l=20, r=40, t=50, b=20), coloraxis_showscale=False)
    return fig

def plot_runs_vs_strike_rate(df_batsmen: pd.DataFrame, min_runs: int = 100) -> go.Figure:
    if df_batsmen.empty:
        return go.Figure()
    filtered = df_batsmen[df_batsmen["Runs"] >= min_runs]
    if filtered.empty:
        filtered = df_batsmen
    fig = px.scatter(
        filtered,
        x="Runs",
        y="Strike Rate",
        text="Batsman",
        size="Sixes",
        color="Average",
        color_continuous_scale="Bluered",
        hover_data=[c for c in ["Balls", "Fours", "Sixes", "Highest Score"] if c in filtered.columns],
        title="Runs vs Strike Rate (Circle Size = Sixes, Color = Average)"
    )
    fig.update_traces(textposition="top center")
    fig.update_layout(height=500, margin=dict(l=20, r=20, t=50, b=20))
    return fig

def plot_player_comparison_grouped_bar(df_comparison: pd.DataFrame, metrics: List[str], role: str = "batting") -> go.Figure:
    if df_comparison.empty:
        return go.Figure()
    player_col = "Batsman" if role == "batting" else "Bowler"
    melted = df_comparison.melt(id_vars=[player_col], value_vars=metrics, var_name="Metric", value_name="Value")
    fig = px.bar(
        melted,
        x="Metric",
        y="Value",
        color=player_col,
        barmode="group",
        title=f"Player Comparison - Key {role.title()} Metrics",
        text="Value"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=450, margin=dict(l=20, r=20, t=50, b=20))
    return fig
