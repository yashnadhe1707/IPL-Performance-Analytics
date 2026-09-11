"""
Team Visualizations Module.
Builds interactive Plotly charts for team win rates, season standings,
and head-to-head records.
"""

import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import Dict, List
from src.utils.helpers import get_team_color

def plot_team_win_percentages(df_teams: pd.DataFrame) -> go.Figure:
    if df_teams.empty:
        return go.Figure()
    sorted_df = df_teams.sort_values(by="Win %", ascending=True)
    colors = [get_team_color(t) for t in sorted_df["Team"]]
    fig = go.Figure(
        go.Bar(
            x=sorted_df["Win %"],
            y=sorted_df["Team"],
            orientation="h",
            text=[f"{v:.1f}% ({w}/{m})" for v, w, m in zip(sorted_df["Win %"], sorted_df["Wins"], sorted_df["Matches"])],
            textposition="outside",
            marker=dict(color=colors)
        )
    )
    fig.update_layout(
        title="Historical Team Win Percentages (Wins / Matches)",
        xaxis_title="Win Percentage (%)",
        yaxis_title="Team",
        height=480,
        margin=dict(l=20, r=50, t=50, b=20)
    )
    return fig

def plot_head_to_head_comparison(h2h: Dict) -> go.Figure:
    if not h2h or "error" in h2h:
        return go.Figure()
    t1 = h2h["team1"]
    t2 = h2h["team2"]
    labels = [t1, t2]
    values = [h2h["team1_wins"], h2h["team2_wins"]]
    if h2h["ties_or_no_result"] > 0:
        labels.append("Ties / No Result")
        values.append(h2h["ties_or_no_result"])
    colors = [get_team_color(t1), get_team_color(t2), "#CBD5E1"]
    fig = go.Figure(
        go.Pie(
            labels=labels,
            values=values,
            hole=0.45,
            marker=dict(colors=colors),
            textinfo="label+value+percent"
        )
    )
    fig.update_layout(
        title=f"Head-to-Head: {t1} vs {t2} ({h2h['total_matches']} Matches)",
        height=400,
        margin=dict(l=20, r=20, t=50, b=20)
    )
    return fig
