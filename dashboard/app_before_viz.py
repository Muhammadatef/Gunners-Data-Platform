"""
Arsenal FC Analytics Dashboard - Modern Professional Design
Clean, minimal aesthetic inspired by modern web applications
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

# Database connection
DB_HOST = os.getenv("POSTGRES_HOST", "postgres")
DB_PORT = os.getenv("POSTGRES_PORT", "5432")
DB_NAME = os.getenv("ANALYTICS_DB_NAME", "arsenalfc_analytics")
DB_USER = os.getenv("ANALYTICS_DB_USER", "analytics_user")
DB_PASSWORD = os.getenv("ANALYTICS_DB_PASSWORD", "analytics_pass")

def get_db_connection():
    return psycopg2.connect(
        host=DB_HOST, port=DB_PORT, dbname=DB_NAME,
        user=DB_USER, password=DB_PASSWORD
    )

def query_to_df(query):
    conn = get_db_connection()
    try:
        df = pd.read_sql_query(query, conn)
        return df
    finally:
        conn.close()

def apply_modern_theme(fig):
    """Apply clean, modern theme to charts"""
    fig.update_layout(
        plot_bgcolor='white',
        paper_bgcolor='white',
        font=dict(family='system-ui, -apple-system, sans-serif', color='#1F2937', size=12),
        title_font=dict(size=16, color='#111827'),
        xaxis=dict(showgrid=False, linecolor='#E5E7EB', color='#6B7280'),
        yaxis=dict(gridcolor='#F3F4F6', linecolor='#E5E7EB', color='#6B7280'),
        legend=dict(bgcolor='white', bordercolor='#E5E7EB', font=dict(color='#6B7280')),
        margin=dict(t=40, l=40, r=20, b=40),
        hoverlabel=dict(bgcolor='white', bordercolor='#E5E7EB', font=dict(color='#1F2937'))
    )
    return fig

# Page config
st.set_page_config(
    page_title="Arsenal FC Analytics",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"  # Hide sidebar
)

# Modern, Clean CSS
st.markdown("""
    <style>
    /* Import modern font */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    * {
        font-family: 'Inter', system-ui, -apple-system, sans-serif;
    }

    /* Clean white background */
    .stApp {
        background: #F9FAFB;
    }

    /* Hide sidebar by default */
    [data-testid="stSidebar"] {
        display: none;
    }

    /* Modern headers */
    h1 {
        color: #111827 !important;
        font-weight: 700 !important;
        font-size: 2rem !important;
        margin-bottom: 0.5rem !important;
    }

    h2 {
        color: #374151 !important;
        font-weight: 600 !important;
        font-size: 1.5rem !important;
        margin-top: 2rem !important;
        margin-bottom: 1rem !important;
    }

    h3 {
        color: #4B5563 !important;
        font-weight: 600 !important;
        font-size: 1.125rem !important;
    }

    /* Clean metric cards */
    [data-testid="stMetricValue"] {
        font-size: 2.25rem !important;
        font-weight: 700 !important;
        color: #111827 !important;
    }

    [data-testid="stMetricLabel"] {
        color: #6B7280 !important;
        font-weight: 500 !important;
        font-size: 0.875rem !important;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    [data-testid="stMetricDelta"] {
        color: #059669 !important;
        font-weight: 500 !important;
    }

    div[data-testid="stMetric"] {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        transition: all 0.2s ease;
    }

    div[data-testid="stMetric"]:hover {
        box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
        border-color: #D1D5DB;
    }

    /* Tables */
    [data-testid="stDataFrame"] {
        background: white;
        border-radius: 8px;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    /* Buttons */
    .stButton>button {
        background: white;
        color: #374151;
        border: 1px solid #D1D5DB;
        border-radius: 6px;
        padding: 0.5rem 1rem;
        font-weight: 500;
        transition: all 0.2s ease;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    .stButton>button:hover {
        background: #F9FAFB;
        border-color: #9CA3AF;
    }

    /* Select boxes */
    .stSelectbox > div > div {
        background: white;
        border: 1px solid #D1D5DB;
        border-radius: 6px;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 8px;
        background: transparent;
        border-bottom: 1px solid #E5E7EB;
    }

    .stTabs [data-baseweb="tab"] {
        background: transparent;
        border: none;
        color: #6B7280;
        font-weight: 500;
        padding: 0.75rem 1rem;
    }

    .stTabs [aria-selected="true"] {
        background: transparent;
        color: #EF0107;
        border-bottom: 2px solid #EF0107;
    }

    /* Arsenal accent color */
    .arsenal-accent {
        color: #EF0107;
        font-weight: 600;
    }

    /* Card container */
    .card {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
        margin-bottom: 1rem;
    }

    /* Top nav style */
    .top-nav {
        background: white;
        padding: 1rem 2rem;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 2rem;
        box-shadow: 0 1px 2px 0 rgba(0, 0, 0, 0.05);
    }

    /* Badge */
    .badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.75rem;
        font-weight: 600;
        background: #FEF2F2;
        color: #991B1B;
    }
    </style>
""", unsafe_allow_html=True)

# Top Navigation
st.markdown("""
    <div class="top-nav">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 1.5rem;">🎯</span>
                <h1 style="margin: 0 !important; font-size: 1.25rem !important;">Arsenal FC Analytics</h1>
                <span class="badge">2024-25 Season</span>
            </div>
            <div style="color: #6B7280; font-size: 0.875rem;">
                Last updated: """ + datetime.now().strftime('%H:%M') + """
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# Get season data
seasons_df = query_to_df("SELECT DISTINCT season FROM metrics.arsenal_matches ORDER BY season DESC")
seasons = seasons_df['season'].tolist() if len(seasons_df) > 0 else []

# Page tabs for navigation
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Season Overview",
    "⚽ Match Detail",
    "👤 Player Stats",
    "📈 Tactical Analysis",
    "🔗 Shot Networks",
    "📍 Expected Threat"
])

with tab1:
    st.markdown("## Season Overview")

    # Season selector
    col1, col2, col3 = st.columns([2, 2, 6])
    with col1:
        selected_season = st.selectbox("Season", ["All Seasons"] + seasons, key="season_select", label_visibility="collapsed")

    if selected_season == "All Seasons":
        summary_query = "SELECT * FROM metrics.season_summary ORDER BY season DESC"
        matches_query = "SELECT * FROM metrics.arsenal_matches ORDER BY match_date DESC"
    else:
        summary_query = f"SELECT * FROM metrics.season_summary WHERE season = '{selected_season}'"
        matches_query = f"SELECT * FROM metrics.arsenal_matches WHERE season = '{selected_season}' ORDER BY match_date DESC"

    summary_df = query_to_df(summary_query)
    matches_df = query_to_df(matches_query)

    if len(summary_df) > 0:
        summary_row = summary_df.iloc[0]

        # Key metrics
        col1, col2, col3, col4, col5 = st.columns(5)

        with col1:
            st.metric("Matches", int(summary_row.get('matches_played') or 0))
        with col2:
            st.metric("Wins", int(summary_row.get('wins') or 0))
        with col3:
            matches = int(summary_row.get('matches_played') or 0)
            wins = int(summary_row.get('wins') or 0)
            win_rate = (wins / matches * 100) if matches > 0 else 0
            st.metric("Win Rate", f"{win_rate:.1f}%")
        with col4:
            st.metric("Goals For", int(summary_row.get('goals_for') or 0))
        with col5:
            st.metric("xG For", f"{float(summary_row.get('xg_for') or 0):.1f}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Charts
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Recent Form")
            recent = matches_df.head(10)
            result_colors = {'W': '#059669', 'D': '#F59E0B', 'L': '#DC2626'}

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
                xaxis_title="",
                yaxis_title="Points",
                height=300,
                yaxis=dict(tickvals=[0, 1, 3], ticktext=['Loss', 'Draw', 'Win'])
            )
            fig = apply_modern_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### xG Performance")
            recent_xg = matches_df.head(10)

            fig = go.Figure()
            fig.add_trace(go.Scatter(
                x=recent_xg['match_date'],
                y=recent_xg['arsenal_xg'],
                name='Arsenal xG',
                mode='lines+markers',
                line=dict(color='#EF0107', width=2),
                marker=dict(size=8)
            ))
            fig.add_trace(go.Scatter(
                x=recent_xg['match_date'],
                y=recent_xg['opponent_xg'],
                name='Opponent xG',
                mode='lines+markers',
                line=dict(color='#D1D5DB', width=2),
                marker=dict(size=8)
            ))
            fig.update_layout(xaxis_title="", yaxis_title="Expected Goals", height=300)
            fig = apply_modern_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

        # Recent matches table
        st.markdown("### Recent Matches")
        matches_display = matches_df[['match_date', 'opponent', 'venue', 'result', 'arsenal_goals', 'opponent_goals', 'arsenal_xg', 'opponent_xg']].head(10)
        matches_display.columns = ['Date', 'Opponent', 'Venue', 'Result', 'GF', 'GA', 'xGF', 'xGA']
        st.dataframe(matches_display, use_container_width=True, hide_index=True)
    else:
        st.markdown("""
            <div style="text-align: center; padding: 3rem 2rem; background: white; border-radius: 12px; border: 1px solid #E5E7EB;">
                <h2 style="color: #EF0107; margin-bottom: 1rem;">Welcome to Arsenal FC Analytics</h2>
                <p style="color: #6B7280; font-size: 1.1rem; margin-bottom: 2rem;">
                    No data available yet. The database views need to be created.
                </p>
                <p style="color: #9CA3AF; font-size: 0.9rem;">
                    Raw match data is available but metrics views are not created yet.<br>
                    Contact the admin to set up the analytics views.
                </p>
            </div>
        """, unsafe_allow_html=True)

with tab2:
    st.markdown("## Match Detail")
    st.info("Match analysis feature - Select a match to view detailed statistics")

with tab3:
    st.markdown("## Player Statistics")

    player_query = "SELECT * FROM metrics.player_advanced_stats ORDER BY season DESC, total_xg DESC LIMIT 20"
    player_df = query_to_df(player_query)

    if len(player_df) > 0:
        # Top performers
        col1, col2, col3 = st.columns(3)

        top_scorer = player_df.iloc[0]
        with col1:
            st.metric("Top Scorer", top_scorer['player_name'], f"{int(top_scorer['goals'])} goals")

        top_xg = player_df.nlargest(1, 'total_xg').iloc[0]
        with col2:
            st.metric("Highest xG", top_xg['player_name'], f"{top_xg['total_xg']:.1f} xG")

        top_shots = player_df.nlargest(1, 'total_shots').iloc[0]
        with col3:
            st.metric("Most Shots", top_shots['player_name'], f"{int(top_shots['total_shots'])} shots")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### Player Performance")

        player_display = player_df[['player_name', 'total_shots', 'goals', 'total_xg']].head(15)
        player_display.columns = ['Player', 'Shots', 'Goals', 'xG']
        st.dataframe(player_display, use_container_width=True, hide_index=True)

with tab4:
    st.markdown("## Tactical Analysis")
    st.info("Tactical insights and patterns")

with tab5:
    st.markdown("## Shot Involvement Networks")
    st.info("Player connection analysis")

with tab6:
    st.markdown("## Expected Threat (xT)")

    xt_query = "SELECT * FROM metrics.player_xt_stats ORDER BY total_xt DESC LIMIT 15"
    xt_df = query_to_df(xt_query)

    if len(xt_df) > 0:
        col1, col2, col3 = st.columns(3)

        with col1:
            top1 = xt_df.iloc[0]
            st.metric(f"🥇 {top1['player_name']}", f"{top1['total_xt']:.1f} xT", f"{int(top1['total_shots'])} shots")

        with col2:
            if len(xt_df) > 1:
                top2 = xt_df.iloc[1]
                st.metric(f"🥈 {top2['player_name']}", f"{top2['total_xt']:.1f} xT", f"{int(top2['total_shots'])} shots")

        with col3:
            if len(xt_df) > 2:
                top3 = xt_df.iloc[2]
                st.metric(f"🥉 {top3['player_name']}", f"{top3['total_xt']:.1f} xT", f"{int(top3['total_shots'])} shots")

        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown("### xT Leaders")

        xt_display = xt_df[['player_name', 'position_category', 'total_shots', 'goals', 'total_xt', 'avg_xt_per_shot', 'high_threat_pct']]
        xt_display.columns = ['Player', 'Position', 'Shots', 'Goals', 'Total xT', 'Avg xT', 'High Threat %']
        st.dataframe(xt_display, use_container_width=True, hide_index=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; color: #9CA3AF; font-size: 0.875rem; padding: 2rem 0; border-top: 1px solid #E5E7EB;">
        <p>Powered by Understat & FBref • Built with ❤️ for Arsenal FC</p>
    </div>
""", unsafe_allow_html=True)
