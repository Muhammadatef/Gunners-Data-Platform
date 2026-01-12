"""
Arsenal FC Analytics Dashboard - Complete with All Visualizations
Modern clean design with advanced football analytics
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

def create_pitch():
    """Create a football pitch background"""
    fig = go.Figure()
    
    # Pitch dimensions (normalized 0-1)
    fig.add_shape(type="rect", x0=0, y0=0, x1=1, y1=1,
                  line=dict(color="#E5E7EB", width=2), fillcolor="white")
    
    # Center line
    fig.add_shape(type="line", x0=0.5, y0=0, x1=0.5, y1=1,
                  line=dict(color="#E5E7EB", width=2))
    
    # Center circle
    fig.add_shape(type="circle", xref="x", yref="y",
                  x0=0.45, y0=0.35, x1=0.55, y1=0.65,
                  line=dict(color="#E5E7EB", width=2))
    
    # Penalty boxes
    fig.add_shape(type="rect", x0=0, y0=0.22, x1=0.17, y1=0.78,
                  line=dict(color="#E5E7EB", width=2))
    fig.add_shape(type="rect", x0=0.83, y0=0.22, x1=1, y1=0.78,
                  line=dict(color="#E5E7EB", width=2))
    
    fig.update_xaxes(range=[0, 1], showgrid=False, zeroline=False, showticklabels=False)
    fig.update_yaxes(range=[0, 1], showgrid=False, zeroline=False, showticklabels=False)
    fig.update_layout(
        plot_bgcolor='#F0FDF4',
        paper_bgcolor='white',
        height=400,
        margin=dict(l=0, r=0, t=0, b=0),
        xaxis=dict(scaleanchor="y", scaleratio=1)
    )
    return fig

# Page config
st.set_page_config(
    page_title="Arsenal FC Analytics",
    page_icon="🎯",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Modern CSS
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');
    * { font-family: 'Inter', system-ui, -apple-system, sans-serif; }
    .stApp { background: #F9FAFB; }
    [data-testid="stSidebar"] { display: none; }
    div[data-testid="stMetric"] {
        background: white;
        border-radius: 12px;
        padding: 1.5rem;
        border: 1px solid #E5E7EB;
        box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.1);
    }
    .stTabs [aria-selected="true"] {
        background: transparent;
        color: #EF0107;
        border-bottom: 2px solid #EF0107;
    }
    .top-nav {
        background: white;
        padding: 1.5rem 2rem;
        border-bottom: 1px solid #E5E7EB;
        margin-bottom: 2rem;
    }
    .badge {
        background: #FEE2E2;
        color: #991B1B;
        padding: 0.25rem 0.75rem;
        border-radius: 999px;
        font-size: 0.875rem;
        font-weight: 500;
    }
    </style>
""", unsafe_allow_html=True)

# Top navigation
st.markdown("""
    <div class="top-nav">
        <div style="display: flex; align-items: center; justify-content: space-between;">
            <div style="display: flex; align-items: center; gap: 1rem;">
                <span style="font-size: 1.5rem;">🎯</span>
                <h1 style="margin: 0 !important; font-size: 1.25rem !important;">Arsenal FC Analytics</h1>
            </div>
        </div>
    </div>
""", unsafe_allow_html=True)

# GLOBAL SEASON FILTER
seasons_query = "SELECT DISTINCT season FROM metrics.match_list ORDER BY season DESC"
seasons_df = query_to_df(seasons_query)
available_seasons = seasons_df['season'].tolist() if len(seasons_df) > 0 else ['2024-25']

selected_season = st.selectbox(
    "**🗓️ Select Season** (applies to all tabs)",
    available_seasons,
    index=0
)

st.markdown("<br>", unsafe_allow_html=True)

# Create tabs
tab1, tab2, tab3, tab4, tab5, tab6 = st.tabs([
    "📊 Season Overview",
    "⚽ Match Detail",
    "👤 Player Stats",
    "📈 Tactical Analysis",
    "🔗 Shot Networks",
    "📍 Expected Threat"
])

with tab1:
    st.markdown(f"## Season Overview: {selected_season}")
    
    summary_query = f"SELECT * FROM metrics.season_summary WHERE season = '{selected_season}'"
    matches_query = f"SELECT * FROM metrics.arsenal_matches WHERE season = '{selected_season}' ORDER BY match_date DESC"
    
    summary_df = query_to_df(summary_query)
    matches_df = query_to_df(matches_query)
    
    if len(summary_df) > 0:
        summary_row = summary_df.iloc[0]
        
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
        
        if len(matches_df) > 0:
            col1, col2 = st.columns(2)
            
            with col1:
                st.markdown("### Form (Last 10)")
                recent_form = matches_df.head(10)
                fig = go.Figure()
                colors = {'W': '#10B981', 'D': '#F59E0B', 'L': '#EF4444'}
                fig.add_trace(go.Bar(
                    x=recent_form['match_date'],
                    y=[3 if r=='W' else 1 if r=='D' else 0 for r in recent_form['result']],
                    marker_color=[colors[r] for r in recent_form['result']],
                    hovertemplate='%{x}<br>Result: %{text}<extra></extra>',
                    text=recent_form['result']
                ))
                fig = apply_modern_theme(fig)
                st.plotly_chart(fig, use_container_width=True)
            
            with col2:
                st.markdown("### xG Performance")
                recent_xg = matches_df.head(10)
                fig = go.Figure()
                fig.add_trace(go.Scatter(
                    x=recent_xg['match_date'], y=recent_xg['arsenal_xg'],
                    name='Arsenal xG', mode='lines+markers',
                    line=dict(color='#EF0107', width=2), marker=dict(size=8)
                ))
                fig.add_trace(go.Scatter(
                    x=recent_xg['match_date'], y=recent_xg['opponent_xg'],
                    name='Opponent xG', mode='lines+markers',
                    line=dict(color='#9CA3AF', width=2), marker=dict(size=8)
                ))
                fig = apply_modern_theme(fig)
                st.plotly_chart(fig, use_container_width=True)
        
            st.markdown("### Recent Matches")
            matches_display = matches_df[['match_date', 'opponent', 'venue', 'result', 'arsenal_goals', 'opponent_goals', 'arsenal_xg', 'opponent_xg']].head(10)
            matches_display.columns = ['Date', 'Opponent', 'Venue', 'Result', 'GF', 'GA', 'xGF', 'xGA']
            st.dataframe(matches_display, use_container_width=True, hide_index=True)

with tab2:
    st.markdown(f"## Match Detail: {selected_season}")

    matches_list_query = f"SELECT match_id, match_name, match_date FROM metrics.match_list WHERE season = '{selected_season}' ORDER BY match_date DESC"
    matches_list_df = query_to_df(matches_list_query)

    if len(matches_list_df) > 0:
        selected_match = st.selectbox(
            "Select Match",
            matches_list_df['match_id'].tolist(),
            format_func=lambda x: matches_list_df[matches_list_df['match_id']==x]['match_name'].iloc[0]
        )
        
        shots_query = f"SELECT * FROM metrics.match_shots_detail WHERE match_id = '{selected_match}'"
        shots_df = query_to_df(shots_query)
        
        if len(shots_df) > 0:
            match_info = shots_df.iloc[0]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Home", f"{match_info['home_team']}", f"{int(match_info['home_goals'])} goals")
            with col2:
                st.metric("xG", f"{float(match_info['home_xg']):.2f} - {float(match_info['away_xg']):.2f}")
            with col3:
                st.metric("Away", f"{match_info['away_team']}", f"{int(match_info['away_goals'])} goals")
            
            st.markdown("<br>", unsafe_allow_html=True)
            
            # Shot map
            st.markdown("### Shot Map")
            # Filter Arsenal shots (team field may be empty)
            arsenal_players = ['Bukayo Saka', 'Leandro Trossard', 'Gabriel Martinelli', 'Kai Havertz', 'Martin Odegaard',
                              'Declan Rice', 'Mikel Merino', 'Thomas Partey', 'Gabriel', 'Ben White', 'Jurrien Timber',
                              'William Saliba', 'Gabriel Jesus', 'Ethan Nwaneri', 'Jorginho', 'Fabio Vieira']
            arsenal_shots = shots_df[shots_df['player_name'].isin(arsenal_players) | (shots_df['home_team'] == 'Arsenal')]
            
            fig = create_pitch()
            
            # Plot shots by result
            for result, color, symbol in [
                ('Goal', '#10B981', 'star'),
                ('SavedShot', '#F59E0B', 'circle'),
                ('BlockedShot', '#EF4444', 'x'),
                ('MissedShots', '#9CA3AF', 'circle-open')
            ]:
                result_shots = arsenal_shots[arsenal_shots['result'] == result]
                if len(result_shots) > 0:
                    fig.add_trace(go.Scatter(
                        x=result_shots['x'], y=result_shots['y'],
                        mode='markers', name=result,
                        marker=dict(size=result_shots['xg']*100+20, color=color, symbol=symbol, line=dict(width=2, color='white')),
                        hovertemplate='<b>%{text}</b><br>xG: %{customdata:.2f}<extra></extra>',
                        text=result_shots['player_name'],
                        customdata=result_shots['xg']
                    ))
            
            fig = apply_modern_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

with tab3:
    st.markdown(f"## Player Statistics: {selected_season}")

    player_query = f"SELECT * FROM metrics.player_advanced_stats WHERE season = '{selected_season}' ORDER BY total_xg DESC LIMIT 20"
    player_df = query_to_df(player_query)

    if len(player_df) > 0:
        col1, col2, col3 = st.columns(3)

        top_scorer = player_df.iloc[0]
        with col1:
            st.metric("Top Scorer", top_scorer['player_name'], f"{int(top_scorer['goals'])} goals")

        with col2:
            st.metric("Highest xG", top_scorer['player_name'], f"{top_scorer['total_xg']:.1f} xG")

        with col3:
            st.metric("Most Shots", top_scorer['player_name'], f"{int(top_scorer['total_shots'])} shots")

        st.markdown("<br>", unsafe_allow_html=True)

        # Top scorers bar chart
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Top Scorers")
            fig = go.Figure(go.Bar(
                x=player_df['goals'].head(10),
                y=player_df['player_name'].head(10),
                orientation='h',
                marker=dict(color='#EF0107'),
                text=player_df['goals'].head(10),
                textposition='outside'
            ))
            fig.update_layout(yaxis={'categoryorder':'total ascending'}, height=400)
            fig = apply_modern_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### xG vs Goals")
            top10 = player_df.head(10)
            fig = go.Figure()
            fig.add_trace(go.Bar(name='Goals', x=top10['player_name'], y=top10['goals'], marker_color='#10B981'))
            fig.add_trace(go.Bar(name='xG', x=top10['player_name'], y=top10['total_xg'], marker_color='#9CA3AF'))
            fig.update_layout(barmode='group', height=400)
            fig = apply_modern_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

        # Player heat map selector
        st.markdown("### Player Shot Heatmap")
        selected_player = st.selectbox("Select Player", player_df['player_name'].unique())

        player_shots_query = f"""
        SELECT * FROM metrics.match_shots_detail
        WHERE season = '{selected_season}' AND team = 'Arsenal' AND player_name = '{selected_player}'
        """
        player_shots_df = query_to_df(player_shots_query)

        if len(player_shots_df) > 0:
            col1, col2 = st.columns([2, 1])

            with col1:
                fig = create_pitch()

                # Add shot markers by result type
                for result, color, symbol in [
                    ('Goal', '#10B981', 'star'),
                    ('SavedShot', '#F59E0B', 'circle'),
                    ('BlockedShot', '#EF4444', 'x'),
                    ('MissedShots', '#9CA3AF', 'circle-open')
                ]:
                    result_shots = player_shots_df[player_shots_df['result'] == result]
                    if len(result_shots) > 0:
                        fig.add_trace(go.Scatter(
                            x=result_shots['x'], y=result_shots['y'],
                            mode='markers', name=result,
                            marker=dict(size=result_shots['xg']*100+20, color=color, symbol=symbol, line=dict(width=2, color='white')),
                            hovertemplate='<b>%{text}</b><br>xG: %{customdata:.2f}<extra></extra>',
                            text=[result] * len(result_shots),
                            customdata=result_shots['xg']
                        ))

                fig.update_layout(height=500)
                fig = apply_modern_theme(fig)
                st.plotly_chart(fig, use_container_width=True)

            with col2:
                st.markdown(f"#### {selected_player} Stats")
                player_stats = player_df[player_df['player_name'] == selected_player].iloc[0]
                st.metric("Total Shots", int(player_stats['total_shots']))
                st.metric("Goals", int(player_stats['goals']))
                st.metric("Total xG", f"{player_stats['total_xg']:.2f}")
                st.metric("Avg xG/Shot", f"{player_stats['avg_xg_per_shot']:.3f}")

                # Shot outcome breakdown
                outcome_counts = player_shots_df['result'].value_counts()
                fig = go.Figure(data=[go.Pie(
                    labels=outcome_counts.index,
                    values=outcome_counts.values,
                    hole=0.5,
                    marker=dict(colors=['#10B981', '#F59E0B', '#EF4444', '#9CA3AF'])
                )])
                fig.update_layout(height=250, showlegend=False, margin=dict(t=0, l=0, r=0, b=0))
                st.plotly_chart(fig, use_container_width=True)

        st.markdown("### Player Performance Table")
        player_display = player_df[['player_name', 'total_shots', 'goals', 'total_xg', 'avg_xg_per_shot']].head(15)
        player_display.columns = ['Player', 'Shots', 'Goals', 'Total xG', 'Avg xG']
        st.dataframe(player_display, use_container_width=True, hide_index=True)

with tab4:
    st.markdown(f"## Tactical Analysis: {selected_season}")

    all_shots_query = f"""
    SELECT * FROM metrics.match_shots_detail
    WHERE season = '{selected_season}'
    """
    all_shots_df = query_to_df(all_shots_query)

    if len(all_shots_df) > 0:
        # Top metrics
        arsenal_shots = all_shots_df[all_shots_df['home_team'] == 'Arsenal']
        opponent_shots = all_shots_df[all_shots_df['away_team'] == 'Arsenal']

        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Shots", len(arsenal_shots))
        with col2:
            goals = len(arsenal_shots[arsenal_shots['result'] == 'Goal'])
            st.metric("Goals", goals)
        with col3:
            conversion = (goals / len(arsenal_shots) * 100) if len(arsenal_shots) > 0 else 0
            st.metric("Conversion %", f"{conversion:.1f}%")
        with col4:
            avg_xg = arsenal_shots['xg'].mean() if len(arsenal_shots) > 0 else 0
            st.metric("Avg xG/Shot", f"{avg_xg:.3f}")

        st.markdown("<br>", unsafe_allow_html=True)

        # Row 1: Shot zones and outcomes
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Shot Zones Heatmap")
            fig = create_pitch()
            fig.add_trace(go.Histogram2d(
                x=arsenal_shots['x'], y=arsenal_shots['y'],
                colorscale='Reds', showscale=True,
                colorbar=dict(title="Shots")
            ))
            fig.update_layout(height=400)
            fig = apply_modern_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Shot Outcomes")
            outcome_counts = arsenal_shots['result'].value_counts()
            fig = go.Figure(data=[go.Pie(
                labels=outcome_counts.index,
                values=outcome_counts.values,
                hole=0.4,
                marker=dict(colors=['#10B981', '#F59E0B', '#EF4444', '#9CA3AF']),
                textinfo='label+percent',
                textposition='outside'
            )])
            fig.update_layout(height=400, showlegend=False)
            fig = apply_modern_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

        # Row 2: xG distribution and shot distance
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### xG Distribution")
            fig = go.Figure()
            fig.add_trace(go.Histogram(
                x=arsenal_shots['xg'],
                nbinsx=20,
                marker_color='#EF0107',
                name='xG'
            ))
            fig.update_layout(
                xaxis_title="xG Value",
                yaxis_title="Number of Shots",
                height=350
            )
            fig = apply_modern_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Shot Distance from Goal")
            # Calculate distance from goal (assuming goal is at x=1, y=0.5)
            arsenal_shots_copy = arsenal_shots.copy()
            arsenal_shots_copy['distance'] = ((1 - arsenal_shots_copy['x'])**2 + (0.5 - arsenal_shots_copy['y'])**2)**0.5

            fig = go.Figure()
            fig.add_trace(go.Box(
                y=arsenal_shots_copy['distance'],
                x=arsenal_shots_copy['result'],
                marker_color='#EF0107',
                boxmean='sd'
            ))
            fig.update_layout(
                xaxis_title="Shot Outcome",
                yaxis_title="Distance (normalized)",
                height=350
            )
            fig = apply_modern_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

with tab5:
    st.markdown(f"## Shot Networks: {selected_season}")

    network_query = f"""
    SELECT * FROM metrics.assist_network
    WHERE season = '{selected_season}'
    ORDER BY assists_count DESC LIMIT 20
    """
    network_df = query_to_df(network_query)

    if len(network_df) > 0:
        # Top metrics
        col1, col2, col3 = st.columns(3)
        with col1:
            total_assists = network_df['assists_count'].sum()
            st.metric("Total Assists", int(total_assists))
        with col2:
            goals_from_assists = network_df['goals_from_assists'].sum()
            st.metric("Goals from Assists", int(goals_from_assists))
        with col3:
            unique_assisters = network_df['assister'].nunique()
            st.metric("Active Assisters", unique_assisters)

        st.markdown("<br>", unsafe_allow_html=True)

        # Row 1: Network graph and top assisters
        col1, col2 = st.columns([2, 1])

        with col1:
            st.markdown("### Assist Network Graph")
            G = nx.DiGraph()
            for _, row in network_df.head(15).iterrows():
                G.add_edge(row['assister'], row['shooter'], weight=row['assists_count'])

            pos = nx.spring_layout(G, k=3, iterations=50, seed=42)

            edge_x, edge_y = [], []
            edge_weights = []
            for edge in G.edges():
                x0, y0 = pos[edge[0]]
                x1, y1 = pos[edge[1]]
                edge_x.extend([x0, x1, None])
                edge_y.extend([y0, y1, None])
                edge_weights.append(G.edges[edge]['weight'])

            fig = go.Figure()

            # Add edges with varying widths
            for i in range(0, len(edge_x), 3):
                weight_idx = i // 3
                if weight_idx < len(edge_weights):
                    fig.add_trace(go.Scatter(
                        x=edge_x[i:i+2], y=edge_y[i:i+2],
                        mode='lines',
                        line=dict(width=edge_weights[weight_idx]*2, color='#E5E7EB'),
                        hoverinfo='none',
                        showlegend=False
                    ))

            # Add nodes
            node_x = [pos[node][0] for node in G.nodes()]
            node_y = [pos[node][1] for node in G.nodes()]
            fig.add_trace(go.Scatter(
                x=node_x, y=node_y, mode='markers+text',
                marker=dict(size=25, color='#EF0107', line=dict(width=2, color='white')),
                text=list(G.nodes()), textposition="top center",
                textfont=dict(size=11, color='#1F2937'),
                hoverinfo='text',
                showlegend=False
            ))

            fig.update_layout(showlegend=False, height=500,
                            xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
                            yaxis=dict(showgrid=False, zeroline=False, showticklabels=False))
            fig = apply_modern_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

        with col2:
            st.markdown("### Top Assisters")
            top_assisters = network_df.groupby('assister').agg({
                'assists_count': 'sum',
                'goals_from_assists': 'sum'
            }).sort_values('assists_count', ascending=False).head(8)

            fig = go.Figure(go.Bar(
                x=top_assisters['assists_count'],
                y=top_assisters.index,
                orientation='h',
                marker=dict(color='#EF0107'),
                text=top_assisters['assists_count'],
                textposition='outside'
            ))
            fig.update_layout(
                yaxis={'categoryorder':'total ascending'},
                height=500,
                xaxis_title="Assists"
            )
            fig = apply_modern_theme(fig)
            st.plotly_chart(fig, use_container_width=True)

        # Detailed table
        st.markdown("### Assist Partnerships Detail")
        network_display = network_df[['assister', 'shooter', 'assists_count', 'goals_from_assists', 'total_xg_assisted']].head(15)
        network_display.columns = ['Assister', 'Shooter', 'Assists', 'Goals', 'xG']
        st.dataframe(network_display, use_container_width=True, hide_index=True)

with tab6:
    st.markdown(f"## Expected Threat (xT): {selected_season}")

    xt_query = f"SELECT * FROM metrics.player_xt_stats WHERE season = '{selected_season}' ORDER BY total_xt DESC LIMIT 20"
    xt_df = query_to_df(xt_query)

    if len(xt_df) > 0:
        # Top 3 medals
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

        # Row 1: xT bar chart and scatter plot
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### xT Leaders")
        
        fig = go.Figure(go.Bar(
            x=xt_df['total_xt'].head(10),
            y=xt_df['player_name'].head(10),
            orientation='h',
            marker=dict(color='#EF0107')
        ))
        fig.update_layout(yaxis={'categoryorder':'total ascending'})
        fig = apply_modern_theme(fig)
        st.plotly_chart(fig, use_container_width=True)
        
        xt_display = xt_df[['player_name', 'total_shots', 'goals', 'total_xt', 'avg_xt_per_shot', 'high_threat_pct']]
        xt_display.columns = ['Player', 'Shots', 'Goals', 'Total xT', 'Avg xT', 'High Threat %']
        st.dataframe(xt_display, use_container_width=True, hide_index=True)

# Footer
st.markdown("<br><br>", unsafe_allow_html=True)
st.markdown("""
    <div style="text-align: center; color: #9CA3AF; font-size: 0.875rem; padding: 2rem 0; border-top: 1px solid #E5E7EB;">
        <p>Powered by Understat & FBref • Built with ❤️ for Arsenal FC</p>
    </div>
""", unsafe_allow_html=True)
