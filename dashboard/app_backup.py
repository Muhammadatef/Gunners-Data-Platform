"""
Arsenal FC Analytics Dashboard - Comprehensive Version
Uses metrics layer for Arsenal-specific insights with all KPIs
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import psycopg2
import os
from datetime import datetime
import networkx as nx
import numpy as np

# Database connection using psycopg2 directly (avoids SQLAlchemy immutabledict issues)
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("ANALYTICS_DB_NAME", "arsenalfc_analytics")
DB_USER = os.getenv("ANALYTICS_DB_USER", "analytics_user")
DB_PASSWORD = os.getenv("ANALYTICS_DB_PASSWORD", "analytics_pass")

def get_db_connection():
    """Get PostgreSQL connection"""
    return psycopg2.connect(
        host=DB_HOST,
        port=DB_PORT,
        dbname=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD
    )

def query_to_df(query):
    """Execute query and return DataFrame"""
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()

def apply_arsenal_theme(fig):
    """Apply Arsenal FC color theme to Plotly charts"""
    fig.update_layout(
        plot_bgcolor='rgba(0,0,0,0)',
        paper_bgcolor='rgba(0,0,0,0)',
        font=dict(color='white', family='Roboto'),
        title_font=dict(color='#FDB913', size=18, family='Roboto'),
        xaxis=dict(gridcolor='rgba(255,255,255,0.1)', color='white'),
        yaxis=dict(gridcolor='rgba(255,255,255,0.1)', color='white'),
        legend=dict(bgcolor='rgba(0,0,0,0.3)', bordercolor='#FDB913', font=dict(color='white'))
    )
    return fig

# Arsenal color palette for charts
ARSENAL_COLORS = ['#EF0107', '#FDB913', '#023474', '#90EE90', '#FF6B6B', '#87CEEB']
ARSENAL_RED_SCALE = ['#8B0000', '#EF0107', '#FF4444', '#FF6B6B', '#FDB913']

# Page config
st.set_page_config(
    page_title="Arsenal FC Analytics | The Gunners",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Modern Arsenal-themed CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Roboto:wght@300;400;700&display=swap');

    /* Arsenal Color Palette */
    :root {
        --arsenal-red: #EF0107;
        --arsenal-gold: #FDB913;
        --arsenal-white: #FFFFFF;
        --arsenal-navy: #023474;
        --arsenal-dark: #1A1A1A;
    }

    /* Global Styling */
    * {
        font-family: 'Roboto', sans-serif;
    }

    /* Main App Background - Clean White */
    .stApp {
        background: #FFFFFF;
    }

    /* Sidebar Styling - Arsenal Red */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #EF0107 0%, #DB0007 100%);
        box-shadow: 4px 0 15px rgba(239,1,7,0.15);
    }

    [data-testid="stSidebar"] .stMarkdown {
        color: white !important;
    }

    [data-testid="stSidebar"] h2, [data-testid="stSidebar"] h3 {
        color: #FDB913 !important;
        text-shadow: none;
    }

    /* Navigation Radio Buttons */
    [data-testid="stSidebar"] .stRadio > label {
        background: rgba(255,255,255,0.1);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        padding: 12px 15px;
        margin: 5px 0;
        transition: all 0.3s ease;
        border: 1px solid rgba(255,255,255,0.2);
    }

    [data-testid="stSidebar"] .stRadio > label:hover {
        background: rgba(253,185,19,0.2);
        border-color: #FDB913;
        transform: translateX(5px);
    }

    /* Header Styling */
    h1 {
        color: #FDB913 !important;
        text-shadow: 3px 3px 6px rgba(0,0,0,0.7);
        font-weight: 700 !important;
        font-size: 3rem !important;
        margin-bottom: 0 !important;
    }

    h2 {
        color: #EF0107 !important;
        font-weight: 600 !important;
        margin-top: 2rem !important;
    }

    h3 {
        color: #FDB913 !important;
        font-weight: 500 !important;
    }

    /* Metric Cards - Glassmorphism */
    [data-testid="stMetricValue"] {
        font-size: 36px !important;
        font-weight: 700 !important;
        color: #FDB913 !important;
        text-shadow: 2px 2px 4px rgba(0,0,0,0.5);
    }

    [data-testid="stMetricLabel"] {
        color: white !important;
        font-weight: 500 !important;
        font-size: 14px !important;
    }

    [data-testid="stMetricDelta"] {
        color: #90EE90 !important;
    }

    div[data-testid="stMetric"] {
        background: linear-gradient(135deg, rgba(239,1,7,0.2), rgba(2,52,116,0.2));
        backdrop-filter: blur(10px);
        border-radius: 15px;
        padding: 20px;
        border: 1px solid rgba(253,185,19,0.3);
        box-shadow: 0 8px 32px rgba(0,0,0,0.3);
        transition: all 0.3s ease;
    }

    div[data-testid="stMetric"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 12px 40px rgba(239,1,7,0.4);
        border-color: #FDB913;
    }

    /* Tables */
    [data-testid="stDataFrame"] {
        background: rgba(255,255,255,0.05);
        backdrop-filter: blur(10px);
        border-radius: 10px;
        border: 1px solid rgba(253,185,19,0.2);
    }

    /* Plotly Charts - Dark Theme */
    .js-plotly-plot {
        background: transparent !important;
    }

    /* Buttons */
    .stButton>button {
        background: linear-gradient(135deg, #EF0107, #023474);
        color: white;
        border: none;
        border-radius: 25px;
        padding: 10px 30px;
        font-weight: 600;
        transition: all 0.3s ease;
        box-shadow: 0 4px 15px rgba(239,1,7,0.4);
    }

    .stButton>button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(239,1,7,0.6);
    }

    /* Select Boxes */
    .stSelectbox > div > div {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        border: 1px solid rgba(253,185,19,0.3);
        color: white;
    }

    /* Multiselect */
    .stMultiSelect > div > div {
        background: rgba(255,255,255,0.1);
        border-radius: 10px;
        border: 1px solid rgba(253,185,19,0.3);
    }

    /* Dividers */
    hr {
        border-color: rgba(253,185,19,0.3);
        margin: 2rem 0;
    }

    /* Custom Arsenal Badge */
    .arsenal-badge {
        display: inline-block;
        background: linear-gradient(135deg, #EF0107, #023474);
        color: #FDB913;
        padding: 5px 15px;
        border-radius: 20px;
        font-weight: 700;
        text-transform: uppercase;
        font-size: 0.8rem;
        box-shadow: 0 2px 10px rgba(239,1,7,0.5);
        margin: 5px;
    }

    /* Arsenal Header Banner */
    .arsenal-header {
        background: linear-gradient(135deg, #EF0107 0%, #023474 100%);
        padding: 30px;
        border-radius: 15px;
        text-align: center;
        box-shadow: 0 10px 40px rgba(239,1,7,0.5);
        margin-bottom: 30px;
        border: 2px solid #FDB913;
    }

    /* Cannon and Scarf Elements */
    .cannon-icon {
        font-size: 3rem;
        display: inline-block;
        animation: bounce 2s infinite;
    }

    @keyframes bounce {
        0%, 100% { transform: translateY(0); }
        50% { transform: translateY(-10px); }
    }

    /* Footer Styling */
    .arsenal-footer {
        background: linear-gradient(135deg, #023474, #EF0107);
        padding: 20px;
        border-radius: 10px;
        text-align: center;
        margin-top: 50px;
        border: 1px solid #FDB913;
    }

    .arsenal-footer p {
        color: white;
        margin: 5px 0;
    }

    /* Scrollbar */
    ::-webkit-scrollbar {
        width: 10px;
        height: 10px;
    }

    ::-webkit-scrollbar-track {
        background: #1A1A1A;
    }

    ::-webkit-scrollbar-thumb {
        background: linear-gradient(135deg, #EF0107, #FDB913);
        border-radius: 5px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: #EF0107;
    }
    </style>
""", unsafe_allow_html=True)

# Arsenal Header Banner with Cannon and Scarf
st.markdown("""
    <div class="arsenal-header">
        <span class="cannon-icon">🎯</span>
        <h1 style="display: inline; margin: 0 20px;">ARSENAL FC ANALYTICS</h1>
        <span class="cannon-icon">🧣</span>
        <p style="color: #FDB913; font-size: 1.2rem; margin-top: 10px; font-weight: 600;">
            ⚡ THE GUNNERS PERFORMANCE DASHBOARD ⚡
        </p>
        <p style="color: white; font-size: 0.9rem; margin-top: 5px;">
            Victoria Concordia Crescit • Victory Through Harmony
        </p>
    </div>
""", unsafe_allow_html=True)

# Sidebar with Arsenal Branding
st.sidebar.markdown("""
    <div style="text-align: center; padding: 20px 0;">
        <h1 style="color: #FDB913; font-size: 4rem; margin: 0;">🎯</h1>
        <h2 style="color: white; margin: 5px 0;">THE GUNNERS</h2>
        <p style="color: #FDB913; font-size: 0.8rem; margin: 0;">Since 1886 🧣</p>
    </div>
""", unsafe_allow_html=True)

st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color: #FDB913;'>📊 NAVIGATION</h3>", unsafe_allow_html=True)

page = st.sidebar.radio("", ["Season Overview", "Match Detail", "Player Performance", "Tactical Analysis", "Shot Involvement Networks", "Expected Threat (xT)"], label_visibility="collapsed")

st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color: #FDB913;'>🗓️ SEASON</h3>", unsafe_allow_html=True)

# Season selector
seasons_df = query_to_df("SELECT DISTINCT season FROM metrics.arsenal_matches ORDER BY season DESC")
seasons = seasons_df['season'].tolist() if len(seasons_df) > 0 else []
selected_season = st.sidebar.selectbox("", ["All Seasons"] + seasons, label_visibility="collapsed")

# Additional filters
st.sidebar.markdown("---")
st.sidebar.markdown("<h3 style='color: #FDB913;'>🎚️ FILTERS</h3>", unsafe_allow_html=True)
venue_filter = st.sidebar.multiselect("Venue", ["H", "A"], default=["H", "A"])
result_filter = st.sidebar.multiselect("Result", ["W", "D", "L"], default=["W", "D", "L"])

# Stats preview in sidebar
st.sidebar.markdown("---")
try:
    quick_stats = query_to_df(f"""
        SELECT COUNT(*) as matches, SUM(arsenal_goals) as goals,
               ROUND(AVG(arsenal_xg), 2) as avg_xg
        FROM metrics.arsenal_matches
        WHERE season = '{seasons[0] if len(seasons) > 0 else "2025-26"}'
    """)
    if len(quick_stats) > 0:
        st.sidebar.markdown(f"""
            <div style="background: rgba(255,255,255,0.1); padding: 15px; border-radius: 10px; border: 1px solid #FDB913;">
                <p style="color: #FDB913; font-weight: 600; margin: 0;">SEASON SNAPSHOT</p>
                <p style="color: white; font-size: 2rem; margin: 10px 0;">{int(quick_stats['matches'][0])}</p>
                <p style="color: white; font-size: 0.8rem; margin: 0;">MATCHES</p>
                <hr style="border-color: rgba(253,185,19,0.3); margin: 10px 0;">
                <p style="color: white; font-size: 1.5rem; margin: 5px 0;">{int(quick_stats['goals'][0])} ⚽</p>
                <p style="color: white; font-size: 0.8rem; margin: 0;">GOALS SCORED</p>
            </div>
        """, unsafe_allow_html=True)
except:
    pass

# ==============================================================================
# SEASON OVERVIEW PAGE
# ==============================================================================

if page == "Season Overview":
    st.header("📊 Season Overview")

    # Get season summary
    if selected_season == "All Seasons":
        summary_query = "SELECT * FROM metrics.season_summary ORDER BY season DESC"
        matches_query = "SELECT * FROM metrics.arsenal_matches ORDER BY match_date DESC"
    else:
        summary_query = f"SELECT * FROM metrics.season_summary WHERE season = '{selected_season}'"
        matches_query = f"SELECT * FROM metrics.arsenal_matches WHERE season = '{selected_season}' ORDER BY match_date DESC"

    summary_df = query_to_df(summary_query)
    matches_df = query_to_df(matches_query)

    if len(summary_df) == 0:
        st.warning("No season data available. Run scraper to collect data.")
    else:
        # Aggregate if showing all seasons
        if selected_season == "All Seasons":
            total_matches = summary_df['matches_played'].sum()
            total_wins = summary_df['wins'].sum()
            total_draws = summary_df['draws'].sum()
            total_losses = summary_df['losses'].sum()
            total_gf = summary_df['goals_for'].sum()
            total_ga = summary_df['goals_against'].sum()
            total_xgf = summary_df['total_xg_for'].sum()
            total_xga = summary_df['total_xg_against'].sum()
            total_points = summary_df['points'].sum()
        else:
            row = summary_df.iloc[0]
            total_matches = row['matches_played']
            total_wins = row['wins']
            total_draws = row['draws']
            total_losses = row['losses']
            total_gf = row['goals_for']
            total_ga = row['goals_against']
            total_xgf = row['total_xg_for']
            total_xga = row['total_xg_against']
            total_points = row['points']

        # Top KPIs
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Matches", total_matches)
            win_rate = (total_wins / total_matches * 100) if total_matches > 0 else 0
            st.metric("Win Rate", f"{win_rate:.1f}%")

        with col2:
            st.metric("Wins", total_wins)
            st.metric("Draws", total_draws)

        with col3:
            st.metric("Losses", total_losses)
            st.metric("Points", total_points)

        with col4:
            st.metric("Goals For", int(total_gf))
            st.metric("Goals Against", int(total_ga))

        with col5:
            st.metric("Goal Diff", f"{int(total_gf - total_ga):+d}")
            st.metric("xG Diff", f"{(total_xgf - total_xga):+.1f}")

        st.markdown("---")

        # Two columns: Form chart and xG performance
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Recent Form (Last 10)")
            recent = matches_df.head(10)

            # Create form visualization with Arsenal colors
            result_colors = {'W': '#90EE90', 'D': '#FDB913', 'L': '#EF0107'}
            fig = go.Figure()

            fig.add_trace(go.Bar(
                x=recent['match_date'],
                y=[3 if r == 'W' else 1 if r == 'D' else 0 for r in recent['result']],
                marker_color=[result_colors[r] for r in recent['result']],
                text=recent['opponent'],
                hovertemplate='<b>%{text}</b><br>%{x}<extra></extra>'
            ))

            fig.update_layout(
                showlegend=False,
                xaxis_title="Match Date",
                yaxis_title="Points",
                height=300,
                yaxis=dict(tickvals=[0, 1, 3], ticktext=['Loss', 'Draw', 'Win'])
            )

            fig = apply_arsenal_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("xG Performance Trend")

            # xG trend over last 10 matches
            recent = matches_df.head(10)

            fig = go.Figure()

            fig.add_trace(go.Scatter(
                x=recent['match_date'],
                y=recent['arsenal_xg'],
                mode='lines+markers',
                name='Arsenal xG',
                line=dict(color='red', width=3)
            ))

            fig.add_trace(go.Scatter(
                x=recent['match_date'],
                y=recent['opponent_xg'],
                mode='lines+markers',
                name='Opponent xG',
                line=dict(color='blue', width=3)
            ))

            fig.update_layout(
                xaxis_title="Match Date",
                yaxis_title="Expected Goals (xG)",
                height=300,
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Match results table
        st.subheader("Match Results")

        display_df = matches_df[['match_date', 'opponent', 'venue', 'result', 'arsenal_goals', 'opponent_goals', 'arsenal_xg', 'opponent_xg', 'xg_overperformance']].copy()
        display_df.columns = ['Date', 'Opponent', 'Venue', 'Result', 'GF', 'GA', 'xGF', 'xGA', 'xG Diff']
        display_df['Date'] = pd.to_datetime(display_df['Date']).dt.strftime('%Y-%m-%d')
        display_df['xGF'] = display_df['xGF'].round(2)
        display_df['xGA'] = display_df['xGA'].round(2)
        display_df['xG Diff'] = display_df['xG Diff'].round(2)

        st.dataframe(display_df, use_container_width=True, height=400)

# ==============================================================================
# MATCH DETAIL PAGE
# ==============================================================================

elif page == "Match Detail":
    st.header("⚽ Match Detail Analysis")

    # Get matches
    if selected_season == "All Seasons":
        matches_df = query_to_df("SELECT * FROM metrics.arsenal_matches ORDER BY match_date DESC LIMIT 50")
    else:
        matches_df = query_to_df(f"SELECT * FROM metrics.arsenal_matches WHERE season = '{selected_season}' ORDER BY match_date DESC")

    if len(matches_df) == 0:
        st.warning("No matches found. Run scraper first.")
    else:
        # Match selector
        match_options = [
            f"{row['match_date']} - Arsenal vs {row['opponent']} ({row['result']})"
            for _, row in matches_df.iterrows()
        ]

        selected_match = st.selectbox("Select Match", match_options)
        match_idx = match_options.index(selected_match)
        match = matches_df.iloc[match_idx]

        # Match header
        col1, col2, col3 = st.columns([1, 2, 1])

        with col1:
            st.markdown(f"### Arsenal")
            st.markdown(f"### {match['arsenal_goals']}")
            st.caption(f"xG: {match['arsenal_xg']:.2f}")

        with col2:
            result_color = {'W': '🟢', 'D': '🟡', 'L': '🔴'}[match['result']]
            st.markdown(f"<h2 style='text-align: center'>{result_color} {match['arsenal_goals']} - {match['opponent_goals']} {result_color}</h2>", unsafe_allow_html=True)
            st.markdown(f"<p style='text-align: center'>{match['match_date']} | {'Home' if match['venue'] == 'H' else 'Away'}</p>", unsafe_allow_html=True)

        with col3:
            st.markdown(f"### {match['opponent']}")
            st.markdown(f"### {match['opponent_goals']}")
            st.caption(f"xG: {match['opponent_xg']:.2f}")

        st.markdown("---")

        # Get shot-level data
        shots_query = f"""
        SELECT *
        FROM silver.shot_events
        WHERE match_url = '{match['match_url']}'
        ORDER BY minute
        """
        shots_df = query_to_df(shots_query)

        if len(shots_df) > 0:
            # Shot map
            st.subheader("Shot Map")

            fig = go.Figure()

            # Arsenal shots
            arsenal_shots = shots_df[shots_df['team'] == 'Arsenal']
            opponent_shots = shots_df[shots_df['team'] != 'Arsenal']

            # Add Arsenal goals
            arsenal_goals = arsenal_shots[arsenal_shots['result'] == 'Goal']
            if len(arsenal_goals) > 0:
                fig.add_trace(go.Scatter(
                    x=arsenal_goals['x_coord'],
                    y=arsenal_goals['y_coord'],
                    mode='markers',
                    name='Arsenal Goal',
                    marker=dict(size=arsenal_goals['xg'] * 200, color='#EF0107', symbol='star', line=dict(width=2, color='white')),
                    text=[f"{row['player_name']}<br>{row['minute']}' - xG: {row['xg']:.2f}" for _, row in arsenal_goals.iterrows()],
                    hovertemplate='%{text}<extra></extra>'
                ))

            # Add Arsenal shots (no goal)
            arsenal_no_goal = arsenal_shots[arsenal_shots['result'] != 'Goal']
            if len(arsenal_no_goal) > 0:
                fig.add_trace(go.Scatter(
                    x=arsenal_no_goal['x_coord'],
                    y=arsenal_no_goal['y_coord'],
                    mode='markers',
                    name='Arsenal Shot',
                    marker=dict(size=arsenal_no_goal['xg'] * 200, color='#FDB913', opacity=0.6),
                    text=[f"{row['player_name']}<br>{row['minute']}' - xG: {row['xg']:.2f}" for _, row in arsenal_no_goal.iterrows()],
                    hovertemplate='%{text}<extra></extra>'
                ))

            # Add opponent shots
            if len(opponent_shots) > 0:
                opponent_goals = opponent_shots[opponent_shots['result'] == 'Goal']
                if len(opponent_goals) > 0:
                    fig.add_trace(go.Scatter(
                        x=opponent_goals['x_coord'],
                        y=opponent_goals['y_coord'],
                        mode='markers',
                        name='Opponent Goal',
                        marker=dict(size=opponent_goals['xg'] * 200, color='blue', symbol='star', line=dict(width=2, color='white')),
                        text=[f"{row['player_name']}<br>{row['minute']}' - xG: {row['xg']:.2f}" for _, row in opponent_goals.iterrows()],
                        hovertemplate='%{text}<extra></extra>'
                    ))

                opponent_no_goal = opponent_shots[opponent_shots['result'] != 'Goal']
                if len(opponent_no_goal) > 0:
                    fig.add_trace(go.Scatter(
                        x=opponent_no_goal['x_coord'],
                        y=opponent_no_goal['y_coord'],
                        mode='markers',
                        name='Opponent Shot',
                        marker=dict(size=opponent_no_goal['xg'] * 200, color='lightblue', opacity=0.6),
                        text=[f"{row['player_name']}<br>{row['minute']}' - xG: {row['xg']:.2f}" for _, row in opponent_no_goal.iterrows()],
                        hovertemplate='%{text}<extra></extra>'
                    ))

            fig.update_layout(
                xaxis_title="Field Position (X)",
                yaxis_title="Field Position (Y)",
                height=500,
                xaxis=dict(range=[0, 1]),
                yaxis=dict(range=[0, 1]),
                showlegend=True
            )

            st.plotly_chart(fig, use_container_width=True)

            # xG timeline
            st.subheader("xG Timeline")

            # Cumulative xG by minute
            arsenal_cumxg = arsenal_shots.sort_values('minute').copy()
            arsenal_cumxg['cumulative_xg'] = arsenal_cumxg['xg'].cumsum()

            opponent_cumxg = opponent_shots.sort_values('minute').copy()
            opponent_cumxg['cumulative_xg'] = opponent_cumxg['xg'].cumsum()

            fig = go.Figure()

            if len(arsenal_cumxg) > 0:
                fig.add_trace(go.Scatter(
                    x=arsenal_cumxg['minute'],
                    y=arsenal_cumxg['cumulative_xg'],
                    mode='lines',
                    name='Arsenal',
                    line=dict(color='#EF0107', width=3),
                    fill='tozeroy'
                ))

            if len(opponent_cumxg) > 0:
                fig.add_trace(go.Scatter(
                    x=opponent_cumxg['minute'],
                    y=opponent_cumxg['cumulative_xg'],
                    mode='lines',
                    name='Opponent',
                    line=dict(color='blue', width=3),
                    fill='tozeroy'
                ))

            fig.update_layout(
                xaxis_title="Minute",
                yaxis_title="Cumulative xG",
                height=300,
                hovermode='x unified'
            )

            st.plotly_chart(fig, use_container_width=True)

            # Shot quality distribution
            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Shot Quality Distribution")

                fig = go.Figure()
                if len(arsenal_shots) > 0:
                    fig.add_trace(go.Histogram(x=arsenal_shots['xg'], nbinsx=10, name='Arsenal', marker_color='#EF0107'))
                if len(opponent_shots) > 0:
                    fig.add_trace(go.Histogram(x=opponent_shots['xg'], nbinsx=10, name='Opponent', marker_color='blue'))
                fig.update_layout(barmode='overlay', xaxis_title='xG', yaxis_title='Shot Count', height=300)
                fig.update_traces(opacity=0.6)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.subheader("Shot Type Breakdown")

                arsenal_shot_types = arsenal_shots['shot_type'].value_counts()
                fig = px.pie(values=arsenal_shot_types.values, names=arsenal_shot_types.index, title='Arsenal Shots by Type', color_discrete_sequence=px.colors.sequential.Reds)
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)

            # Detailed shots table
            st.subheader("All Shots")
            display_shots = shots_df[['minute', 'team', 'player_name', 'result', 'xg', 'shot_type', 'situation']].copy()
            display_shots.columns = ['Min', 'Team', 'Player', 'Result', 'xG', 'Type', 'Situation']
            display_shots['xG'] = display_shots['xG'].round(3)
            st.dataframe(display_shots, use_container_width=True, height=400)

# ==============================================================================
# PLAYER PERFORMANCE PAGE
# ==============================================================================

elif page == "Player Performance":
    st.header("👤 Arsenal Player Performance Analysis")

    # Get player stats
    if selected_season == "All Seasons":
        players_query = """
        SELECT * FROM metrics.arsenal_player_stats
        ORDER BY season DESC, goals DESC, total_xg DESC
        LIMIT 50
        """
    else:
        players_query = f"""
        SELECT * FROM metrics.arsenal_player_stats
        WHERE season = '{selected_season}'
        ORDER BY goals DESC, total_xg DESC
        """

    players_df = query_to_df(players_query)

    if len(players_df) == 0:
        st.warning("No player data found. Run scraper first.")
    else:
        # Top scorers
        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Top Scorers")
            top_scorers = players_df.nlargest(10, 'goals')

            fig = go.Figure()
            fig.add_trace(go.Bar(
                y=top_scorers['player_name'],
                x=top_scorers['goals'],
                orientation='h',
                marker_color='#EF0107',
                text=top_scorers['goals'],
                textposition='auto'
            ))
            fig.update_layout(xaxis_title='Goals', yaxis_title='', height=400)
            fig.update_yaxes(autorange="reversed")
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.subheader("Goals vs xG")

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=players_df['total_xg'],
                y=players_df['goals'],
                mode='markers+text',
                marker=dict(size=players_df['shots'] / 3, color='#EF0107', opacity=0.6),
                text=players_df['player_name'],
                textposition='top center',
                hovertemplate='<b>%{text}</b><br>xG: %{x:.2f}<br>Goals: %{y}<extra></extra>'
            ))

            # Add diagonal line (perfect xG match)
            max_val = max(players_df['total_xg'].max(), players_df['goals'].max())
            fig.add_trace(go.Scatter(
                x=[0, max_val],
                y=[0, max_val],
                mode='lines',
                line=dict(dash='dash', color='gray'),
                showlegend=False,
                hoverinfo='skip'
            ))

            fig.update_layout(
                xaxis_title='Total xG',
                yaxis_title='Actual Goals',
                height=400,
                showlegend=False
            )
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Player stats table
        st.subheader("Player Statistics")

        display_players = players_df[['player_name', 'season', 'matches_played', 'shots', 'goals', 'total_xg', 'conversion_rate', 'xg_overperformance']].copy()
        display_players.columns = ['Player', 'Season', 'Matches', 'Shots', 'Goals', 'Total xG', 'Conv %', 'xG+/-']
        display_players['Total xG'] = display_players['Total xG'].round(2)
        display_players['Conv %'] = (display_players['Conv %'] * 100).round(1)
        display_players['xG+/-'] = display_players['xG+/-'].round(2)

        st.dataframe(display_players, use_container_width=True, height=500)

# ==============================================================================
# TACTICAL ANALYSIS PAGE
# ==============================================================================

elif page == "Tactical Analysis":
    st.header("🎯 Tactical Analysis")

    # Get tactical data
    if selected_season == "All Seasons":
        tactical_query = "SELECT * FROM metrics.tactical_analysis ORDER BY season DESC"
    else:
        tactical_query = f"SELECT * FROM metrics.tactical_analysis WHERE season = '{selected_season}'"

    tactical_df = query_to_df(tactical_query)

    if len(tactical_df) == 0:
        st.warning("No tactical data available.")
    else:
        # Aggregate if all seasons
        if selected_season == "All Seasons":
            tactical_row = {
                'arsenal_shots_0_15': tactical_df['arsenal_shots_0_15'].sum(),
                'arsenal_shots_16_30': tactical_df['arsenal_shots_16_30'].sum(),
                'arsenal_shots_31_45': tactical_df['arsenal_shots_31_45'].sum(),
                'arsenal_shots_46_60': tactical_df['arsenal_shots_46_60'].sum(),
                'arsenal_shots_61_75': tactical_df['arsenal_shots_61_75'].sum(),
                'arsenal_shots_76_90': tactical_df['arsenal_shots_76_90'].sum(),
                'arsenal_goals_0_15': tactical_df['arsenal_goals_0_15'].sum(),
                'arsenal_goals_16_30': tactical_df['arsenal_goals_16_30'].sum(),
                'arsenal_goals_31_45': tactical_df['arsenal_goals_31_45'].sum(),
                'arsenal_goals_46_60': tactical_df['arsenal_goals_46_60'].sum(),
                'arsenal_goals_61_75': tactical_df['arsenal_goals_61_75'].sum(),
                'arsenal_goals_76_90': tactical_df['arsenal_goals_76_90'].sum(),
                'open_play_total': tactical_df['open_play_total'].sum(),
                'open_play_goals': tactical_df['open_play_goals'].sum(),
                'corner_total': tactical_df['corner_total'].sum(),
                'corner_goals': tactical_df['corner_goals'].sum(),
                'set_piece_total': tactical_df['set_piece_total'].sum(),
                'set_piece_goals': tactical_df['set_piece_goals'].sum(),
                'penalty_total': tactical_df['penalty_total'].sum(),
                'penalty_goals': tactical_df['penalty_goals'].sum(),
                'big_chances_created': tactical_df['big_chances_created'].sum(),
                'big_chances_converted': tactical_df['big_chances_converted'].sum(),
            }
        else:
            tactical_row = tactical_df.iloc[0].to_dict()

        # Shot timing analysis
        st.subheader("⏱️ Shot Timing by Period")

        col1, col2 = st.columns(2)

        with col1:
            periods = ['0-15', '16-30', '31-45', '46-60', '61-75', '76-90']
            shots = [
                tactical_row['arsenal_shots_0_15'],
                tactical_row['arsenal_shots_16_30'],
                tactical_row['arsenal_shots_31_45'],
                tactical_row['arsenal_shots_46_60'],
                tactical_row['arsenal_shots_61_75'],
                tactical_row['arsenal_shots_76_90']
            ]

            fig = go.Figure()
            fig.add_trace(go.Bar(x=periods, y=shots, marker_color='#EF0107', name='Shots'))
            fig.update_layout(title="Shots by 15-Minute Period", xaxis_title="Period (mins)", yaxis_title="Shots", height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            goals = [
                tactical_row['arsenal_goals_0_15'],
                tactical_row['arsenal_goals_16_30'],
                tactical_row['arsenal_goals_31_45'],
                tactical_row['arsenal_goals_46_60'],
                tactical_row['arsenal_goals_61_75'],
                tactical_row['arsenal_goals_76_90']
            ]

            fig = go.Figure()
            fig.add_trace(go.Bar(x=periods, y=goals, marker_color='#FDB913', name='Goals'))
            fig.update_layout(title="Goals by 15-Minute Period", xaxis_title="Period (mins)", yaxis_title="Goals", height=350)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Shot situations
        st.subheader("⚽ Shot Situations Effectiveness")

        situations = ['Open Play', 'Corners', 'Set Pieces', 'Penalties']
        situation_shots = [
            tactical_row['open_play_total'],
            tactical_row['corner_total'],
            tactical_row['set_piece_total'],
            tactical_row['penalty_total']
        ]
        situation_goals = [
            tactical_row['open_play_goals'],
            tactical_row['corner_goals'],
            tactical_row['set_piece_goals'],
            tactical_row['penalty_goals']
        ]
        situation_conv = [
            (tactical_row['open_play_goals'] / tactical_row['open_play_total'] * 100) if tactical_row['open_play_total'] > 0 else 0,
            (tactical_row['corner_goals'] / tactical_row['corner_total'] * 100) if tactical_row['corner_total'] > 0 else 0,
            (tactical_row['set_piece_goals'] / tactical_row['set_piece_total'] * 100) if tactical_row['set_piece_total'] > 0 else 0,
            (tactical_row['penalty_goals'] / tactical_row['penalty_total'] * 100) if tactical_row['penalty_total'] > 0 else 0
        ]

        col1, col2 = st.columns(2)

        with col1:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=situations, y=situation_shots, name='Shots', marker_color='lightcoral'))
            fig.add_trace(go.Bar(x=situations, y=situation_goals, name='Goals', marker_color='#EF0107'))
            fig.update_layout(title="Shots vs Goals by Situation", barmode='group', height=350)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            fig = go.Figure()
            fig.add_trace(go.Bar(x=situations, y=situation_conv, marker_color='#FDB913', text=[f"{v:.1f}%" for v in situation_conv], textposition='auto'))
            fig.update_layout(title="Conversion Rate by Situation (%)", yaxis_title="Conversion %", height=350)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Big chances
        st.subheader("🎯 Big Chances (xG > 0.3)")

        col1, col2, col3 = st.columns(3)

        with col1:
            st.metric("Big Chances Created", tactical_row['big_chances_created'])

        with col2:
            st.metric("Big Chances Converted", tactical_row['big_chances_converted'])

        with col3:
            conv_rate = (tactical_row['big_chances_converted'] / tactical_row['big_chances_created'] * 100) if tactical_row['big_chances_created'] > 0 else 0
            st.metric("Conversion Rate", f"{conv_rate:.1f}%")

# ==============================================================================
# SHOT INVOLVEMENT NETWORKS PAGE
# ==============================================================================

elif page == "Shot Involvement Networks":
    st.header("🔗 Shot Involvement Networks")
    st.markdown("Visualize player combinations: who assists whom")

    # Season filter
    if selected_season == "All Seasons":
        network_query = "SELECT * FROM metrics.involvement_network_stats WHERE season IS NOT NULL ORDER BY total_connections DESC LIMIT 50"
    else:
        network_query = f"SELECT * FROM metrics.involvement_network_stats WHERE season = '{selected_season}' ORDER BY total_connections DESC"

    network_df = query_to_df(network_query)

    if len(network_df) == 0:
        st.warning("No involvement network data available")
    else:
        # Filters
        col1, col2 = st.columns(2)
        with col1:
            min_connections = st.slider("Minimum Connections", 1, 10, 2)
        with col2:
            show_goals_only = st.checkbox("Show Goals Only", value=False)

        # Filter data
        filtered_df = network_df[network_df['total_connections'] >= min_connections]
        if show_goals_only:
            filtered_df = filtered_df[filtered_df['goals_created'] > 0]

        # Build network graph
        G = nx.DiGraph()

        # Position colors
        pos_colors = {'GK': '#90EE90', 'DEF': '#87CEEB', 'MID': '#FFD700', 'FWD': '#FF6B6B', None: '#CCCCCC'}

        # Add edges (connections)
        for _, row in filtered_df.iterrows():
            from_player = row['from_player']
            to_player = row['to_player']
            weight = row['total_connections']
            goals = row['goals_created']

            G.add_edge(from_player, to_player, weight=weight, goals=goals)

            # Add node attributes
            if from_player not in [n for n, d in G.nodes(data=True)]:
                G.nodes[from_player]['position'] = row['from_position']
            if to_player not in [n for n, d in G.nodes(data=True)]:
                G.nodes[to_player]['position'] = row['to_position']

        if len(G.nodes()) == 0:
            st.warning("No connections found with current filters")
        else:
            # Layout
            pos = nx.spring_layout(G, k=2, iterations=50, seed=42)

            # Create edge traces
            edge_traces = []
            for edge in G.edges(data=True):
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                weight = edge[2]['weight']
                goals = edge[2]['goals']

                edge_trace = go.Scatter(
                    x=[x0, x1, None],
                    y=[y0, y1, None],
                    mode='lines',
                    line=dict(width=weight * 2, color='#CCCCCC'),
                    hoverinfo='text',
                    text=f"{edge[0]} → {edge[1]}<br>Connections: {weight}<br>Goals: {goals}",
                    showlegend=False
                )
                edge_traces.append(edge_trace)

            # Create node traces by position
            node_traces_by_pos = {}
            for node, data in G.nodes(data=True):
                position = data.get('position', 'UNKNOWN')
                if position not in node_traces_by_pos:
                    node_traces_by_pos[position] = {'x': [], 'y': [], 'text': [], 'size': []}

                # Node size based on degree
                node_size = (G.in_degree(node) + G.out_degree(node)) * 5 + 10

                node_traces_by_pos[position]['x'].append(pos[node][0])
                node_traces_by_pos[position]['y'].append(pos[node][1])
                node_traces_by_pos[position]['text'].append(f"{node}<br>Position: {position}")
                node_traces_by_pos[position]['size'].append(node_size)

            # Create plotly traces
            fig = go.Figure()

            # Add edges
            for trace in edge_traces:
                fig.add_trace(trace)

            # Add nodes by position
            for position, data in node_traces_by_pos.items():
                fig.add_trace(go.Scatter(
                    x=data['x'],
                    y=data['y'],
                    mode='markers+text',
                    marker=dict(size=data['size'], color=pos_colors.get(position, '#CCCCCC'), line=dict(width=2, color='white')),
                    text=[t.split('<br>')[0] for t in data['text']],
                    textposition='top center',
                    hovertext=data['text'],
                    hoverinfo='text',
                    name=position or 'Unknown'
                ))

            fig.update_layout(
                title="Arsenal Shot Involvement Network",
                showlegend=True,
                hovermode='closest',
                height=700,
                xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                yaxis=dict(showgrid=False, zeroline=False, showticklabels=False)
            )

            st.plotly_chart(fig, use_container_width=True)

            # Top connections table
            st.subheader("📊 Top Involvement Connections")
            st.dataframe(
                filtered_df[['from_player', 'to_player', 'total_connections', 'goals_created', 'total_xg_created', 'conversion_rate_pct']].head(15),
                use_container_width=True
            )


# ==============================================================================
# EXPECTED THREAT (xT) PAGE
# ==============================================================================

elif page == "Expected Threat (xT)":
    st.header("📍 Expected Threat (xT) Analysis")
    st.markdown("Shot location threat values: where players shoot from")

    # Player xT stats
    if selected_season == "All Seasons":
        xt_query = "SELECT * FROM metrics.player_xt_stats ORDER BY total_xt DESC LIMIT 20"
    else:
        xt_query = f"SELECT * FROM metrics.player_xt_stats WHERE season = '{selected_season}' ORDER BY total_xt DESC"

    xt_df = query_to_df(xt_query)

    if len(xt_df) == 0:
        st.warning("No xT data available")
    else:
        # Top xT generators
        st.subheader("🏆 Top xT Generators")

        col1, col2, col3 = st.columns(3)

        with col1:
            top_player = xt_df.iloc[0]
            st.metric(f"🥇 {top_player['player_name']}", f"{top_player['total_xt']:.2f} xT", f"{top_player['total_shots']} shots")

        with col2:
            if len(xt_df) > 1:
                second_player = xt_df.iloc[1]
                st.metric(f"🥈 {second_player['player_name']}", f"{second_player['total_xt']:.2f} xT", f"{second_player['total_shots']} shots")

        with col3:
            if len(xt_df) > 2:
                third_player = xt_df.iloc[2]
                st.metric(f"🥉 {third_player['player_name']}", f"{third_player['total_xt']:.2f} xT", f"{third_player['total_shots']} shots")

        st.markdown("---")

        # xT vs xG scatter
        st.subheader("📈 xT vs xG Comparison")

        fig = px.scatter(
            xt_df,
            x='total_xg',
            y='total_xt',
            size='total_shots',
            color='position_category',
            hover_name='player_name',
            hover_data=['avg_xt_per_shot', 'avg_xg_per_shot', 'goals'],
            title="Player xT vs xG (Size = Shot Volume)",
            labels={'total_xg': 'Total xG', 'total_xt': 'Total xT', 'position_category': 'Position'},
            color_discrete_map={'GK': '#90EE90', 'DEF': '#87CEEB', 'MID': '#FFD700', 'FWD': '#FF6B6B'}
        )
        fig.update_layout(height=500)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # xT efficiency rankings
        st.subheader("⚡ xT Efficiency Rankings")
        st.markdown("*Goals per unit of xT generated (higher = better conversion from dangerous areas)*")

        xt_efficiency_df = xt_df[xt_df['xt_efficiency'].notna()].sort_values('xt_efficiency', ascending=False).head(10)

        fig = px.bar(
            xt_efficiency_df,
            x='player_name',
            y='xt_efficiency',
            color='position_category',
            title="Top 10 Players by xT Efficiency",
            labels={'xt_efficiency': 'xT Efficiency (Goals per xT)', 'player_name': 'Player'},
            color_discrete_map={'GK': '#90EE90', 'DEF': '#87CEEB', 'MID': '#FFD700', 'FWD': '#FF6B6B'}
        )
        fig.update_layout(xaxis_tickangle=-45, height=450)
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Dangerous shot selection
        st.subheader("🎯 Dangerous Shot Selection")

        col1, col2 = st.columns(2)

        with col1:
            # High threat shots percentage
            fig = px.bar(
                xt_df.head(10),
                x='player_name',
                y='high_threat_pct',
                title="% of Shots from High-Threat Zones (xT > 0.30)",
                labels={'high_threat_pct': 'High Threat %', 'player_name': 'Player'},
                color='high_threat_pct',
                color_continuous_scale='Reds'
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            # Average xT per shot
            fig = px.bar(
                xt_df.head(10),
                x='player_name',
                y='avg_xt_per_shot',
                title="Average xT per Shot",
                labels={'avg_xt_per_shot': 'Avg xT/Shot', 'player_name': 'Player'},
                color='avg_xt_per_shot',
                color_continuous_scale='Blues'
            )
            fig.update_layout(xaxis_tickangle=-45, height=400)
            st.plotly_chart(fig, use_container_width=True)

        st.markdown("---")

        # Full stats table
        st.subheader("📋 Complete xT Statistics")
        st.dataframe(
            xt_df[['player_name', 'position_category', 'total_shots', 'goals', 'total_xt', 'avg_xt_per_shot',
                   'total_xg', 'avg_xg_per_shot', 'high_threat_shots', 'high_threat_pct', 'xt_efficiency']],
            use_container_width=True
        )


# ==============================================================================
# ARSENAL FC FOOTER
# ==============================================================================

st.markdown("""
    <div class="arsenal-footer">
        <h2 style="color: #FDB913; margin: 10px 0;">🎯 COME ON YOU GUNNERS 🧣</h2>
        <p style="font-size: 1.1rem; font-weight: 600;">Victoria Concordia Crescit</p>
        <p style="font-size: 0.9rem; margin-top: 15px;">
            ⚡ Powered by Understat & FBref | Built with ❤️ for The Arsenal Family
        </p>
        <p style="font-size: 0.8rem; color: rgba(255,255,255,0.7);">
            Last Updated: """ + datetime.now().strftime('%Y-%m-%d %H:%M:%S') + """
        </p>
        <div style="margin-top: 15px;">
            <span class="arsenal-badge">Est. 1886</span>
            <span class="arsenal-badge">13× Champions</span>
            <span class="arsenal-badge">The Invincibles</span>
            <span class="arsenal-badge">North London</span>
        </div>
    </div>
""", unsafe_allow_html=True)
