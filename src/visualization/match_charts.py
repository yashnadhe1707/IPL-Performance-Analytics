"""
Match Visualizations Module.
Builds worm chart progression curves and margin distribution plots.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List
from src.utils.helpers import get_team_color

def plot_innings_worm_chart(worm_data: List[Dict]) -> go.Figure:
    if not worm_data:
        return go.Figure()
    df = pd.DataFrame(worm_data)
    fig = go.Figure()
    for team, grp in df.groupby("team"):
        color = get_team_color(team)
        fig.add_trace(
            go.Scatter(
                x=grp["over"],
                y=grp["cumulative_runs"],
                mode="lines+markers",
                name=team,
                line=dict(width=3, color=color),
                marker=dict(size=6)
            )
        )
    fig.update_layout(
        title="Match Worm Chart (Cumulative Runs by Over)",
        xaxis_title="Over",
        yaxis_title="Total Runs",
        xaxis=dict(tickmode="linear", tick0=1, dtick=1),
        height=420,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def plot_victory_margin_distribution(margin_dict: Dict) -> go.Figure:
    runs_data = margin_dict.get("win_by_runs", {}).get("values", [])
    wickets_data = margin_dict.get("win_by_wickets", {}).get("values", [])
    
    fig = go.Figure()
    if runs_data:
        fig.add_trace(go.Histogram(x=runs_data, name="Win by Runs", marker_color="#0078BC", opacity=0.75))
    if wickets_data:
        fig.add_trace(go.Histogram(x=wickets_data, name="Win by Wickets", marker_color="#F9CD05", opacity=0.75))
    
    fig.update_layout(
        title="Distribution of Victory Margins (Runs vs Wickets)",
        xaxis_title="Margin Size",
        yaxis_title="Match Frequency",
        barmode="overlay",
        height=400,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig

def plot_top_potm_awards(df_matches: pd.DataFrame, top_n: int = 10) -> go.Figure:
    if df_matches.empty or "player_of_match" not in df_matches.columns:
        return go.Figure()
    potm_counts = df_matches[df_matches["player_of_match"] != "None Awarded"]["player_of_match"].value_counts().head(top_n).reset_index()
    potm_counts.columns = ["Player", "Awards"]
    potm_counts = potm_counts.sort_values(by="Awards", ascending=True)
    fig = px.bar(
        potm_counts,
        x="Awards",
        y="Player",
        orientation="h",
        text="Awards",
        title=f"Most Player of the Match Awards (Top {top_n})",
        labels={"Awards": "Awards Count", "Player": "Player"},
        color="Awards",
        color_continuous_scale="Teal"
    )
    fig.update_traces(textposition="outside")
    fig.update_layout(height=450, margin=dict(l=20, r=40, t=50, b=20), coloraxis_showscale=False)
    return fig
