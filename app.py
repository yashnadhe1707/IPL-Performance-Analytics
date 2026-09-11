"""
================================================================================
IPL PERFORMANCE ANALYTICS USING DATA SCIENCE AND ANALYTICS
Main Streamlit Application Entry Point
TY B.Sc. Data Science College Project
================================================================================
"""

import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# Add project root to sys.path
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if BASE_DIR not in sys.path:
    sys.path.insert(0, BASE_DIR)

from src.preprocessing.data_loader import IPLDataLoader
from src.preprocessing.data_cleaner import IPLCleaner
from src.player_analysis.batting_analysis import BattingAnalysis
from src.player_analysis.bowling_analysis import BowlingAnalysis
from src.player_analysis.player_comparison import PlayerComparison
from src.team_analysis.team_performance import TeamPerformance
from src.team_analysis.season_analysis import SeasonAnalysis
from src.team_analysis.team_comparison import TeamComparison
from src.match_analysis.match_analysis import MatchAnalysis
from src.match_analysis.toss_analysis import TossAnalysis
from src.match_analysis.venue_analysis import VenueAnalysis
from src.statistics.performance_metrics import compute_distribution_summary, compute_correlation_matrix
from src.statistics.rankings import PerformanceRankings
from src.statistics.trends import StatisticalTrends
from src.insights.insight_generator import InsightGenerator
from src.visualization.player_charts import (
    plot_top_batsmen_bar,
    plot_top_bowlers_bar,
    plot_runs_vs_strike_rate,
    plot_player_comparison_grouped_bar
)
from src.visualization.team_charts import (
    plot_team_win_percentages,
    plot_head_to_head_comparison
)
from src.visualization.match_charts import (
    plot_innings_worm_chart,
    plot_victory_margin_distribution,
    plot_top_potm_awards
)
from src.visualization.dashboard_charts import (
    plot_toss_distribution_donut,
    plot_venue_scoring_bar,
    plot_correlation_heatmap
)
from src.utils.helpers import safe_divide, get_team_color

# -----------------------------------------------------------------------------
# Streamlit Page Configuration & Styling
# -----------------------------------------------------------------------------
st.set_page_config(
    page_title="IPL Performance Analytics",
    page_icon="🏏",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS for modern sports analytics aesthetic
st.markdown("""
<style>
    .main-header {
        font-size: 2.2rem;
        font-weight: 800;
        color: #1E293B;
        margin-bottom: 0.2rem;
    }
    .sub-header {
        font-size: 1.05rem;
        color: #64748B;
        margin-bottom: 1.5rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #1E293B 0%, #0F172A 100%);
        padding: 1.2rem 1rem;
        border-radius: 10px;
        color: #FFFFFF;
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        text-align: center;
    }
    .metric-title {
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: #94A3B8;
        margin-bottom: 0.3rem;
    }
    .metric-value {
        font-size: 1.8rem;
        font-weight: 700;
        color: #38BDF8;
    }
    .disclaimer-box {
        background-color: #FEF3C7;
        border-left: 4px solid #F59E0B;
        padding: 0.8rem 1rem;
        border-radius: 4px;
        color: #92400E;
        font-size: 0.9rem;
        margin-bottom: 1rem;
    }
    .insight-card {
        background-color: #F8FAFC;
        border-left: 4px solid #3B82F6;
        padding: 0.8rem 1.2rem;
        border-radius: 6px;
        margin-bottom: 0.8rem;
        color: #1E293B;
        font-size: 0.95rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.05);
    }
</style>
""", unsafe_allow_html=True)

# -----------------------------------------------------------------------------
# Data Loading Pipeline with Streamlit Caching
# -----------------------------------------------------------------------------
@st.cache_data(show_spinner=False)
def load_data():
    loader = IPLDataLoader(BASE_DIR)
    
    # Check if processed data is cached on disk
    df_matches, df_deliveries = loader.load_processed_data()
    if df_matches is not None and df_deliveries is not None:
        return df_matches, df_deliveries
    
    # If raw data exists, clean and save
    if loader.raw_data_exists():
        raw_m, raw_d = loader.load_raw_data()
        cleaner = IPLCleaner(map_franchise_history=True)
        cm, cd = cleaner.clean_pipeline(raw_m, raw_d)
        loader.save_processed_data(cm, cd)
        return cm, cd
    
    return None, None

df_matches, df_deliveries = load_data()

# Handle missing data scenario
if df_matches is None or df_deliveries is None:
    st.error("⚠️ No IPL dataset found in `data/raw/` or `data/processed/`.")
    st.info("Please place `matches.csv` and `deliveries.csv` inside the `data/raw/` folder.")
    if st.button("🚀 Generate Realistic Multi-Season Starter Dataset (180 Matches)"):
        with st.spinner("Simulating multi-season historical IPL dataset..."):
            from src.preprocessing.generate_sample_data import build_starter_data_files
            build_starter_data_files(os.path.join(BASE_DIR, "data"))
            # Run clean
            loader = IPLDataLoader(BASE_DIR)
            raw_m, raw_d = loader.load_raw_data()
            cleaner = IPLCleaner(map_franchise_history=True)
            cm, cd = cleaner.clean_pipeline(raw_m, raw_d)
            loader.save_processed_data(cm, cd)
            st.cache_data.clear()
            st.rerun()
    st.stop()

# -----------------------------------------------------------------------------
# Sidebar Filters & Navigation
# -----------------------------------------------------------------------------
st.sidebar.image("https://images.unsplash.com/photo-1540747913346-19e32dc3e97e?w=500&auto=format&fit=crop&q=60", use_container_width=True)
st.sidebar.title("🏏 IPL Analytics Hub")
st.sidebar.markdown("**TY B.Sc. Data Science**")

pages = [
    "🏟️ Overview",
    "🏏 Player Analytics",
    "🛡️ Team Analytics",
    "📅 Season Analysis",
    "🎯 Match Analysis",
    "📍 Venue Analysis",
    "🪙 Toss Analysis",
    "👥 Player Comparison",
    "⚔️ Team Comparison",
    "🏆 Performance Rankings",
    "💡 Data-Driven Insights",
    "📊 Data Quality & Evaluation"
]

selected_page = st.sidebar.radio("Navigate Sections", pages)

st.sidebar.markdown("---")
st.sidebar.subheader("🔍 Global Filters")

# Available Seasons
available_seasons = ["All Seasons"] + sorted(df_matches["season"].dropna().unique().astype(str).tolist())
selected_season = st.sidebar.selectbox("Filter by Season", available_seasons)

# Available Teams
available_teams = ["All Teams"] + sorted(list(set(df_matches["team1"].dropna().unique()).union(set(df_matches["team2"].dropna().unique()))))
selected_team = st.sidebar.selectbox("Filter by Team", available_teams)

# Apply global filters
active_season = None if selected_season == "All Seasons" else selected_season
active_team = None if selected_team == "All Teams" else selected_team

# Filtered dataframes for global views
filtered_matches = df_matches.copy()
filtered_deliveries = df_deliveries.copy()

if active_season:
    filtered_matches = filtered_matches[filtered_matches["season"].astype(str) == active_season]
    filtered_deliveries = filtered_deliveries[filtered_deliveries["season"].astype(str) == active_season]

if active_team:
    filtered_matches = filtered_matches[
        (filtered_matches["team1"] == active_team) | (filtered_matches["team2"] == active_team)
    ]
    filtered_deliveries = filtered_deliveries[
        (filtered_deliveries["batting_team"] == active_team) | (filtered_deliveries["bowling_team"] == active_team)
    ]

# Instantiate analytical engines
batting_engine = BattingAnalysis(filtered_deliveries, filtered_matches)
bowling_engine = BowlingAnalysis(filtered_deliveries, filtered_matches)
team_engine = TeamPerformance(filtered_matches, filtered_deliveries)
match_engine = MatchAnalysis(filtered_matches, filtered_deliveries)
toss_engine = TossAnalysis(filtered_matches)
venue_engine = VenueAnalysis(filtered_matches, filtered_deliveries)
rankings_engine = PerformanceRankings(filtered_matches, filtered_deliveries)
trends_engine = StatisticalTrends(filtered_matches, filtered_deliveries)
insight_engine = InsightGenerator(filtered_matches, filtered_deliveries)

st.sidebar.markdown("---")
st.sidebar.caption("Data Science & Analytics Capstone Project")

# =============================================================================
# PAGE 1: OVERVIEW DASHBOARD
# =============================================================================
if selected_page == "🏟️ Overview":
    st.markdown('<div class="main-header">🏟️ IPL Tournament Overview</div>', unsafe_allow_html=True)
    st.markdown(f'<div class="sub-header">Comprehensive historical statistics across {selected_season} • {selected_team}</div>', unsafe_allow_html=True)

    # Dynamic KPI Cards
    total_m = len(filtered_matches)
    total_seasons = filtered_matches["season"].nunique()
    total_teams_count = len(set(filtered_matches["team1"].dropna().unique()).union(set(filtered_matches["team2"].dropna().unique())))
    total_runs = int(filtered_deliveries["total_runs"].sum())
    total_wickets = int(filtered_deliveries["is_bowler_wicket"].sum()) if "is_bowler_wicket" in filtered_deliveries.columns else int(filtered_deliveries["is_wicket"].sum())
    total_sixes = int((filtered_deliveries["batsman_runs"] == 6).sum())
    total_fours = int((filtered_deliveries["batsman_runs"] == 4).sum())

    c1, c2, c3, c4, c5, c6 = st.columns(6)
    with c1:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Seasons</div><div class="metric-value">{total_seasons}</div></div>', unsafe_allow_html=True)
    with c2:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Matches</div><div class="metric-value">{total_m}</div></div>', unsafe_allow_html=True)
    with c3:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Teams</div><div class="metric-value">{total_teams_count}</div></div>', unsafe_allow_html=True)
    with c4:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Runs</div><div class="metric-value">{total_runs:,}</div></div>', unsafe_allow_html=True)
    with c5:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Wickets</div><div class="metric-value">{total_wickets:,}</div></div>', unsafe_allow_html=True)
    with c6:
        st.markdown(f'<div class="metric-card"><div class="metric-title">Total Sixes</div><div class="metric-value">{total_sixes:,}</div></div>', unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # Charts Row 1
    col_l, col_r = st.columns([3, 2])
    with col_l:
        df_teams = team_engine.get_all_teams_summary()
        st.plotly_chart(plot_team_win_percentages(df_teams), use_container_width=True)
    with col_r:
        toss_dist = toss_engine.get_toss_decision_distribution()
        st.plotly_chart(plot_toss_distribution_donut(toss_dist), use_container_width=True)

    # Charts Row 2
    col_b1, col_b2 = st.columns(2)
    with col_b1:
        df_venues = venue_engine.get_all_venues_summary()
        st.plotly_chart(plot_venue_scoring_bar(df_venues, top_n=8), use_container_width=True)
    with col_b2:
        margins_dict = match_engine.get_margin_distribution()
        st.plotly_chart(plot_victory_margin_distribution(margins_dict), use_container_width=True)

# =============================================================================
# PAGE 2: PLAYER ANALYTICS
# =============================================================================
elif selected_page == "🏏 Player Analytics":
    st.markdown('<div class="main-header">🏏 Player Analytics Engine</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">In-depth batting and bowling metrics calculated from historical ball-by-ball records</div>', unsafe_allow_html=True)

    tab_bat, tab_bowl = st.tabs(["🏏 Batting Performance", "🎯 Bowling Performance"])

    with tab_bat:
        c_filter1, c_filter2 = st.columns([3, 1])
        with c_filter1:
            all_batsmen = sorted(filtered_deliveries["batsman"].dropna().unique().tolist())
            selected_batsman = st.selectbox("Select Player for Batting Profile", all_batsmen)
        with c_filter2:
            min_r = st.number_input("Min Runs Filter", min_value=0, max_value=2000, value=50, step=25)

        # Player Profile Header
        profile = batting_engine.get_player_profile(selected_batsman)
        if "error" not in profile:
            k1, k2, k3, k4, k5, k6 = st.columns(6)
            k1.metric("Total Runs", profile.get("Runs", 0))
            k2.metric("Innings", profile.get("Innings", 0))
            k3.metric("Batting Avg", f"{profile.get('Average', 0):.2f}")
            k4.metric("Strike Rate", f"{profile.get('Strike Rate', 0):.2f}")
            k5.metric("Highest Score", profile.get("Highest Score", "0"))
            k6.metric("Boundary %", f"{profile.get('Boundary %', 0):.1f}%")

            # Phase Breakdown if available
            if "phase_analysis" in profile and profile["phase_analysis"]:
                st.subheader(f"📊 {selected_batsman} - Match Phase Analysis")
                df_phase = pd.DataFrame(profile["phase_analysis"])
                fig_phase = px.bar(
                    df_phase, x="over_phase", y="Strike Rate",
                    text="Strike Rate", color="over_phase",
                    title=f"Strike Rate across Powerplay, Middle, and Death Overs",
                    labels={"over_phase": "Match Phase", "Strike Rate": "Strike Rate"}
                )
                fig_phase.update_traces(texttemplate='%{text:.1f}', textposition='outside')
                fig_phase.update_layout(height=350)
                st.plotly_chart(fig_phase, use_container_width=True)

        st.markdown("---")
        st.subheader("Leaderboard & Distribution")
        df_batsmen = batting_engine.get_all_batsmen_summary(min_runs=min_r)
        
        c_chart1, c_chart2 = st.columns([1, 1])
        with c_chart1:
            st.plotly_chart(plot_top_batsmen_bar(df_batsmen, top_n=10), use_container_width=True)
        with c_chart2:
            st.plotly_chart(plot_runs_vs_strike_rate(df_batsmen, min_runs=min_r), use_container_width=True)

        with st.expander("📋 View Complete Batting Summary Table"):
            st.dataframe(df_batsmen, use_container_width=True)

    with tab_bowl:
        c_bfilter1, c_bfilter2 = st.columns([3, 1])
        with c_bfilter1:
            all_bowlers = sorted(filtered_deliveries["bowler"].dropna().unique().tolist())
            selected_bowler = st.selectbox("Select Player for Bowling Profile", all_bowlers)
        with c_bfilter2:
            min_o = st.number_input("Min Overs Filter", min_value=0, max_value=200, value=10, step=5)

        b_profile = bowling_engine.get_bowler_profile(selected_bowler)
        if "error" not in b_profile:
            bk1, bk2, bk3, bk4, bk5, bk6 = st.columns(6)
            bk1.metric("Wickets", b_profile.get("Wickets", 0))
            bk2.metric("Overs", b_profile.get("Overs", "0.0"))
            bk3.metric("Economy", f"{b_profile.get('Economy', 0):.2f}")
            avg_val = b_profile.get('Average', np.nan)
            bk4.metric("Bowling Avg", f"{avg_val:.2f}" if pd.notna(avg_val) else "N/A")
            bk5.metric("Best Figures", b_profile.get("Best Bowling", "0/0"))
            bk6.metric("Dot Ball %", f"{b_profile.get('Dot %', 0):.1f}%")

        st.markdown("---")
        df_bowlers = bowling_engine.get_all_bowlers_summary(min_overs=min_o)
        st.plotly_chart(plot_top_bowlers_bar(df_bowlers, top_n=10), use_container_width=True)

        with st.expander("📋 View Complete Bowling Summary Table"):
            st.dataframe(df_bowlers, use_container_width=True)

# =============================================================================
# PAGE 3: TEAM ANALYTICS
# =============================================================================
elif selected_page == "🛡️ Team Analytics":
    st.markdown('<div class="main-header">🛡️ Franchise Team Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Historical win records, scoring averages, and situational splits</div>', unsafe_allow_html=True)

    df_teams = team_engine.get_all_teams_summary()
    st.plotly_chart(plot_team_win_percentages(df_teams), use_container_width=True)

    st.subheader("Team Specific Breakdown")
    selected_t = st.selectbox("Select Team to Inspect", df_teams["Team"].tolist())
    t_profile = team_engine.get_team_profile(selected_t)

    if "error" not in t_profile:
        col_t1, col_t2 = st.columns(2)
        with col_t1:
            st.markdown("#### 🏏 Batting First Record")
            bf = t_profile["batting_first"]
            st.write(f"**Matches**: {bf['matches']} | **Wins**: {bf['wins']} | **Win Rate**: {bf['win_pct']:.1f}%")
            st.progress(min(1.0, bf['win_pct'] / 100))

        with col_t2:
            st.markdown("#### 🎯 Chasing Record")
            ch = t_profile["chasing"]
            st.write(f"**Matches**: {ch['matches']} | **Wins**: {ch['wins']} | **Win Rate**: {ch['win_pct']:.1f}%")
            st.progress(min(1.0, ch['win_pct'] / 100))

        # Season trends line chart
        if "season_trends" in t_profile and t_profile["season_trends"]:
            st.markdown("#### 📈 Season-by-Season Win Percentage")
            df_st = pd.DataFrame(t_profile["season_trends"])
            fig_st = px.line(
                df_st, x="Season", y="Win %", markers=True,
                title=f"{selected_t} - Historical Season Win % Trend"
            )
            fig_st.update_layout(height=350)
            st.plotly_chart(fig_st, use_container_width=True)

    with st.expander("📋 View Complete Teams Table"):
        st.dataframe(df_teams, use_container_width=True)

# =============================================================================
# PAGE 4: SEASON ANALYSIS
# =============================================================================
elif selected_page == "📅 Season Analysis":
    st.markdown('<div class="main-header">📅 Season-Wise Standings & Trends</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Standings, points progression, and tournament scoring dynamics</div>', unsafe_allow_html=True)

    season_eng = SeasonAnalysis(df_matches, df_deliveries)
    seasons_list = season_eng.get_available_seasons()

    sel_s = st.selectbox("Select IPL Season", seasons_list, index=len(seasons_list)-1 if seasons_list else 0)
    
    # Season Overview KPIs
    s_kpis = season_eng.get_season_overview_kpis(sel_s)
    if s_kpis:
        k1, k2, k3, k4, k5 = st.columns(5)
        k1.metric("Matches", s_kpis.get("Total Matches", 0))
        k2.metric("Total Runs", f"{s_kpis.get('Total Runs', 0):,}")
        k3.metric("Total Wickets", s_kpis.get("Total Wickets", 0))
        k4.metric("Total Sixes", s_kpis.get("Total Sixes", 0))
        k5.metric("Avg Innings Score", s_kpis.get("Average Innings Score", 0.0))

    st.subheader(f"🏆 {sel_s} Points Table & Standings")
    standings = season_eng.get_season_standings(sel_s)
    st.dataframe(standings, use_container_width=True)

    st.markdown("---")
    st.subheader("Tournament Evolution Across All Seasons")
    trends_df = season_eng.get_all_seasons_trend()
    if not trends_df.empty:
        fig_trend = px.bar(
            trends_df, x="Season", y="Average Innings Score",
            text="Average Innings Score",
            title="Average Innings Score by Season",
            color="Average Innings Score",
            color_continuous_scale="Blues"
        )
        fig_trend.update_traces(textposition="outside")
        st.plotly_chart(fig_trend, use_container_width=True)

# =============================================================================
# PAGE 5: MATCH ANALYSIS
# =============================================================================
elif selected_page == "🎯 Match Analysis":
    st.markdown('<div class="main-header">🎯 Match Scorecards & Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Individual match scorecard drill-downs, worm progression curves, and victory margins</div>', unsafe_allow_html=True)

    matches_list = match_engine.get_matches_list()
    
    # Select match dropdown
    match_options = {
        f"Match {row['match_id']}: {row['team1']} vs {row['team2']} ({row['season']}) - Winner: {row['winner']}": row['match_id']
        for _, row in matches_list.iterrows()
    }
    selected_label = st.selectbox("Select Match to Inspect Scorecard", list(match_options.keys()))
    sel_match_id = match_options[selected_label]

    scorecard = match_engine.get_match_scorecard(sel_match_id)
    if "match_info" in scorecard:
        info = scorecard["match_info"]
        st.markdown(f"### 🏟️ {info['team1']} vs {info['team2']}")
        st.markdown(f"**Date:** {info['date']} | **Venue:** {info['venue']} | **Player of Match:** 🌟 {info['player_of_match']}")
        st.markdown(f"**Toss:** {info['toss_winner']} won toss and chose to **{info['toss_decision']}**")
        st.success(f"🏆 **Winner:** {info['winner']} won by **{info['margin_display']}**")

        st.markdown("---")
        # Innings Summaries
        if "innings" in scorecard:
            c_inn1, c_inn2 = st.columns(2)
            for idx, inn in enumerate(scorecard["innings"]):
                col = c_inn1 if idx == 0 else c_inn2
                with col:
                    st.markdown(f"#### Innings {inn['inning']}: {inn['batting_team']}")
                    st.markdown(f"**Score:** {inn['total_runs']} / {inn['total_wickets']} ({inn['overs']} Overs)")
                    
                    st.markdown("**Top Batsmen:**")
                    for b in inn["top_batsmen"]:
                        st.write(f"- {b['batsman']}: {b['runs']} runs")

                    st.markdown("**Top Bowlers:**")
                    for bw in inn["top_bowlers"]:
                        st.write(f"- {bw['bowler']}: {bw['wickets']} wkts ({bw['runs']} runs)")

        # Worm Chart
        if "worm_progression" in scorecard and scorecard["worm_progression"]:
            st.markdown("---")
            st.plotly_chart(plot_innings_worm_chart(scorecard["worm_progression"]), use_container_width=True)

# =============================================================================
# PAGE 6: VENUE ANALYSIS
# =============================================================================
elif selected_page == "📍 Venue Analysis":
    st.markdown('<div class="main-header">📍 Venue & Stadium Analytics</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Stadium scoring profiles, chasing vs defending advantages, and venue records</div>', unsafe_allow_html=True)

    df_venues = venue_engine.get_all_venues_summary()
    st.plotly_chart(plot_venue_scoring_bar(df_venues, top_n=10), use_container_width=True)

    st.subheader("Stadium Drilldown")
    selected_venue = st.selectbox("Select Venue", df_venues["Venue"].tolist())
    v_profile = venue_engine.get_venue_profile(selected_venue)

    if "error" not in v_profile:
        vk1, vk2, vk3, vk4 = st.columns(4)
        vk1.metric("Matches Hosted", v_profile.get("Matches", 0))
        vk2.metric("Avg Innings Score", v_profile.get("Avg Innings Score", 0.0))
        vk3.metric("Defending Win %", f"{v_profile.get('Batting 1st Win %', 0):.1f}%")
        vk4.metric("Chasing Win %", f"{v_profile.get('Batting 2nd Win %', 0):.1f}%")

        if "team_records" in v_profile and v_profile["team_records"]:
            st.markdown(f"#### 🛡️ Most Successful Teams at {selected_venue}")
            st.dataframe(pd.DataFrame(v_profile["team_records"]), use_container_width=True)

    with st.expander("📋 View Complete Venues Summary Table"):
        st.dataframe(df_venues, use_container_width=True)

# =============================================================================
# PAGE 7: TOSS ANALYSIS
# =============================================================================
elif selected_page == "🪙 Toss Analysis":
    st.markdown('<div class="main-header">🪙 Toss Impact & Strategy Analysis</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Historical toss decisions and empirical match outcome associations</div>', unsafe_allow_html=True)

    st.markdown("""
    <div class="disclaimer-box">
        <b>Statistical Disclaimer:</b> Historical data reflects an empirical association between toss decisions and match outcomes.
        Correlation does not imply causation. Match outcomes are influenced by team form, player contributions, and in-game situations.
    </div>
    """, unsafe_allow_html=True)

    toss_dist = toss_engine.get_toss_decision_distribution(season=active_season)
    toss_assoc = toss_engine.get_toss_winner_match_winner_association(season=active_season)

    c_t1, c_t2, c_t3 = st.columns(3)
    c_t1.metric("Field First %", f"{toss_dist.get('field_pct', 0):.1f}%")
    c_t2.metric("Bat First %", f"{toss_dist.get('bat_pct', 0):.1f}%")
    c_t3.metric("Toss Winner Match Win %", f"{toss_assoc.get('association_percentage', 0):.1f}%")

    col_t_l, col_t_r = st.columns(2)
    with col_t_l:
        st.plotly_chart(plot_toss_distribution_donut(toss_dist), use_container_width=True)
    with col_t_r:
        trend_df = toss_engine.get_season_wise_toss_trend()
        if not trend_df.empty:
            fig_tt = px.line(
                trend_df, x="Season", y=["Field %", "Toss & Match Win %"],
                markers=True, title="Toss Decision & Match Win % Evolution"
            )
            fig_tt.update_layout(height=360)
            st.plotly_chart(fig_tt, use_container_width=True)

# =============================================================================
# PAGE 8: PLAYER COMPARISON
# =============================================================================
elif selected_page == "👥 Player Comparison":
    st.markdown('<div class="main-header">👥 Player Head-to-Head Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Side-by-side analytical benchmarking across batting and bowling disciplines</div>', unsafe_allow_html=True)

    comp_engine = PlayerComparison(filtered_deliveries, filtered_matches)
    role = st.radio("Comparison Discipline", ["Batting", "Bowling"], horizontal=True)

    if role == "Batting":
        all_batsmen = sorted(filtered_deliveries["batsman"].dropna().unique().tolist())
        selected_players = st.multiselect("Select Batsmen to Compare (2 to 5 recommended)", all_batsmen, default=all_batsmen[:3] if len(all_batsmen) >= 3 else all_batsmen)

        if len(selected_players) >= 2:
            df_comp = comp_engine.compare_batsmen(selected_players)
            st.dataframe(df_comp, use_container_width=True)

            metrics = ["Runs", "Average", "Strike Rate", "Fours", "Sixes"]
            st.plotly_chart(plot_player_comparison_grouped_bar(df_comp, metrics, role="batting"), use_container_width=True)
        else:
            st.info("Please select at least 2 batsmen to generate comparative charts.")

    else:
        all_bowlers = sorted(filtered_deliveries["bowler"].dropna().unique().tolist())
        selected_bowlers = st.multiselect("Select Bowlers to Compare (2 to 5 recommended)", all_bowlers, default=all_bowlers[:3] if len(all_bowlers) >= 3 else all_bowlers)

        if len(selected_bowlers) >= 2:
            df_bowl_comp = comp_engine.compare_bowlers(selected_bowlers)
            st.dataframe(df_bowl_comp, use_container_width=True)

            metrics = ["Wickets", "Economy", "Dot %"]
            st.plotly_chart(plot_player_comparison_grouped_bar(df_bowl_comp, metrics, role="bowling"), use_container_width=True)
        else:
            st.info("Please select at least 2 bowlers to generate comparative charts.")

# =============================================================================
# PAGE 9: TEAM COMPARISON
# =============================================================================
elif selected_page == "⚔️ Team Comparison":
    st.markdown('<div class="main-header">⚔️ Team Head-to-Head Comparison</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Historical rivalry analysis, head-to-head win counts, and scoring distributions</div>', unsafe_allow_html=True)

    team_comp_engine = TeamComparison(df_matches, df_deliveries)
    teams_list = sorted(list(set(df_matches["team1"].dropna().unique()).union(set(df_matches["team2"].dropna().unique()))))

    col_t1, col_t2 = st.columns(2)
    with col_t1:
        team_a = st.selectbox("Select Team A", teams_list, index=0)
    with col_t2:
        team_b = st.selectbox("Select Team B", teams_list, index=1 if len(teams_list) > 1 else 0)

    if team_a == team_b:
        st.warning("Please select two distinct teams to view head-to-head records.")
    else:
        h2h = team_comp_engine.get_head_to_head(team_a, team_b)
        if "error" in h2h:
            st.info(h2h["error"])
        else:
            hk1, hk2, hk3, hk4 = st.columns(4)
            hk1.metric("Total Encounters", h2h["total_matches"])
            hk2.metric(f"{team_a} Wins", f"{h2h['team1_wins']} ({h2h['team1_win_pct']:.1f}%)")
            hk3.metric(f"{team_b} Wins", f"{h2h['team2_wins']} ({h2h['team2_win_pct']:.1f}%)")
            hk4.metric("Ties / No Result", h2h["ties_or_no_result"])

            col_pie, col_stats = st.columns([1, 1])
            with col_pie:
                st.plotly_chart(plot_head_to_head_comparison(h2h), use_container_width=True)
            with col_stats:
                st.markdown("#### 📊 Average & Highest Totals")
                st.write(f"- **{team_a} Average Score:** {h2h['team1_avg_score']} runs (High: {h2h['team1_high_score']})")
                st.write(f"- **{team_b} Average Score:** {h2h['team2_avg_score']} runs (High: {h2h['team2_high_score']})")

            if "recent_matches" in h2h and h2h["recent_matches"]:
                st.markdown("#### 📜 Recent Match Encounters")
                st.dataframe(pd.DataFrame(h2h["recent_matches"]), use_container_width=True)

# =============================================================================
# PAGE 10: PERFORMANCE RANKINGS
# =============================================================================
elif selected_page == "🏆 Performance Rankings":
    st.markdown('<div class="main-header">🏆 Official Performance Rankings</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Leaderboards ranked by transparent statistical metrics and qualification thresholds</div>', unsafe_allow_html=True)

    ranking_category = st.selectbox("Select Ranking Category", [
        "🟠 Orange Cap (Top Run Scorers)",
        "🟣 Purple Cap (Top Wicket Takers)",
        "⚡ Highest Strike Rates (Min 50 Balls)",
        "🎯 Best Bowling Economy (Min 10 Overs)",
        "🛡️ Franchise Team Standings (Win %)"
    ])

    if "Orange Cap" in ranking_category:
        st.markdown("### 🟠 Orange Cap Leaderboard (Most Runs)")
        st.caption("Ranking Metric: Total batsman runs in completed innings. Tie-breaker: Higher Batting Average.")
        df_orange = rankings_engine.get_top_run_scorers(top_n=15, season=active_season)
        st.dataframe(df_orange, use_container_width=True)

    elif "Purple Cap" in ranking_category:
        st.markdown("### 🟣 Purple Cap Leaderboard (Most Wickets)")
        st.caption("Ranking Metric: Total bowler-credited wickets. Tie-breaker: Lower Bowling Economy.")
        df_purple = rankings_engine.get_top_wicket_takers(top_n=15, season=active_season)
        st.dataframe(df_purple, use_container_width=True)

    elif "Strike Rates" in ranking_category:
        st.markdown("### ⚡ Highest Strike Rates")
        st.caption("Ranking Metric: (Runs / Balls) * 100. Minimum Qualification: 50 legal balls faced.")
        df_sr = rankings_engine.get_highest_strike_rates(min_balls=50, top_n=15, season=active_season)
        st.dataframe(df_sr, use_container_width=True)

    elif "Economy" in ranking_category:
        st.markdown("### 🎯 Best Bowling Economy Rates")
        st.caption("Ranking Metric: Runs conceded per legal over. Minimum Qualification: 10 overs bowled.")
        df_econ = rankings_engine.get_best_bowling_economies(min_overs=10, top_n=15, season=active_season)
        st.dataframe(df_econ, use_container_width=True)

    else:
        st.markdown("### 🛡️ Team Performance Rankings")
        st.caption("Ranking Metric: Win Percentage (Wins / Matches). Tie-breaker: Total Wins, then Average Score.")
        df_tr = rankings_engine.get_team_rankings(season=active_season)
        st.dataframe(df_tr, use_container_width=True)

# =============================================================================
# PAGE 11: DATA-DRIVEN INSIGHTS
# =============================================================================
elif selected_page == "💡 Data-Driven Insights":
    st.markdown('<div class="main-header">💡 Descriptive Data-Driven Insights</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Objective narrative observations derived directly from computed analytical records</div>', unsafe_allow_html=True)

    all_insights = insight_engine.generate_all_insights(season=active_season)

    c_ins1, c_ins2 = st.columns(2)
    with c_ins1:
        st.subheader("🏟️ Tournament & Match Margins")
        for item in all_insights["tournament"]:
            st.markdown(f'<div class="insight-card">{item}</div>', unsafe_allow_html=True)

        st.subheader("🏏 Batting Standouts")
        for item in all_insights["batting"]:
            st.markdown(f'<div class="insight-card">{item}</div>', unsafe_allow_html=True)

    with c_ins2:
        st.subheader("🎯 Bowling Leaders")
        for item in all_insights["bowling"]:
            st.markdown(f'<div class="insight-card">{item}</div>', unsafe_allow_html=True)

        st.subheader("🛡️ Team Performance")
        for item in all_insights["teams"]:
            st.markdown(f'<div class="insight-card">{item}</div>', unsafe_allow_html=True)

    st.subheader("🪙 Toss Dynamics & Stadium Insights")
    for item in all_insights["toss_and_venues"]:
        st.markdown(f'<div class="insight-card">{item}</div>', unsafe_allow_html=True)

# =============================================================================
# PAGE 12: DATA QUALITY & EVALUATION
# =============================================================================
elif selected_page == "📊 Data Quality & Evaluation":
    st.markdown('<div class="main-header">📊 Data Quality & Model Verification</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Verification of dataset integrity, mathematical consistency, and engine latency</div>', unsafe_allow_html=True)

    from evaluation.evaluate_data_quality import run_data_quality_evaluation
    from evaluation.evaluate_statistics import run_statistics_evaluation
    from evaluation.evaluate_dashboard import run_dashboard_evaluation

    col_btn, _ = st.columns([1, 3])
    with col_btn:
        run_checks = st.button("🔄 Run Full Evaluation Suite Now")

    if run_checks:
        with st.spinner("Executing rigorous evaluation tests..."):
            dq_res = run_data_quality_evaluation()
            st_res = run_statistics_evaluation()
            dash_res = run_dashboard_evaluation()
            st.success("All evaluation suites executed successfully!")

    # Display saved evaluation reports if available
    eq_path = os.path.join(BASE_DIR, "outputs", "evaluation_results", "data_quality_report.json")
    st_path = os.path.join(BASE_DIR, "outputs", "evaluation_results", "statistics_validation_report.json")
    db_path = os.path.join(BASE_DIR, "outputs", "evaluation_results", "dashboard_evaluation_report.json")

    tab_dq, tab_stats, tab_dash = st.tabs(["📋 Data Quality", "🧮 Statistical Verification", "⚡ Dashboard Integrity"])

    with tab_dq:
        if os.path.exists(eq_path):
            import json
            with open(eq_path, "r", encoding="utf-8") as f:
                dq_data = json.load(f)
            st.json(dq_data)
        else:
            st.info("Run the evaluation suite to view data quality report.")

    with tab_stats:
        if os.path.exists(st_path):
            import json
            with open(st_path, "r", encoding="utf-8") as f:
                st_data = json.load(f)
            st.json(st_data)
        else:
            st.info("Run the evaluation suite to view statistics validation report.")

    with tab_dash:
        if os.path.exists(db_path):
            import json
            with open(db_path, "r", encoding="utf-8") as f:
                dash_data = json.load(f)
            st.json(dash_data)
        else:
            st.info("Run the evaluation suite to view dashboard evaluation report.")

# -----------------------------------------------------------------------------
# Footer
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption(
    "IPL Performance Analytics Using Data Science and Analytics • "
    "Designed and developed for TY B.Sc. Data Science College Project • "
    "All statistics dynamically computed from official historical match records."
)
