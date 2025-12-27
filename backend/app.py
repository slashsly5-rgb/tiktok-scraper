"""
Project S - TikTok Political Sentiment Dashboard
Digital briefing board for Sarawak political sentiment analysis
Follows Project S UI/UX design principles: single-screen comprehension, minimal interaction, tablet-first
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from database import SupabaseClient
from config import Config
import logging
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Page configuration - optimized for tablet (16:9)
st.set_page_config(
    page_title="Project S - Public Sentiment Dashboard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# Custom CSS for Project S design - Updated UI
st.markdown("""
<style>
    /* Project S Color Palette - Based on UI Design */
    :root {
        --bg-cream: #F5F1E8;
        --bg-white: #FFFFFF;
        --sidebar-dark: #2C2C2C;
        --text-primary: #1A1A1A;
        --text-secondary: #6B6B6B;

        --sentiment-positive: #2ECC71;
        --sentiment-negative: #E74C3C;
        --sentiment-neutral: #95A5A6;

        --accent-warning: #E67E22;
        --accent-yellow: #F39C12;
        --accent-blue: #3498DB;

        --border-color: #E8E4DC;
        --hover-bg: #EBEBEB;
        --shadow: rgba(0, 0, 0, 0.1);
        --shadow-lg: rgba(0, 0, 0, 0.15);

        --radius-sm: 4px;
        --radius-md: 8px;
        --radius-lg: 12px;
        --radius-xl: 16px;
    }

    /* Main app background */
    .stApp {
        background-color: var(--bg-cream);
    }

    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    .stDeployButton {display:none;}
    header {visibility: hidden;}

    /* Main header styling */
    .main-header {
        font-size: 32px;
        font-weight: 700;
        color: var(--text-primary);
        margin-bottom: 8px;
        font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', sans-serif;
    }

    .main-subheader {
        font-size: 14px;
        color: var(--text-secondary);
        margin-bottom: 24px;
    }

    /* Section headers */
    .section-header {
        font-size: 14px;
        font-weight: 600;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
        margin-bottom: 16px;
        padding-bottom: 12px;
        border-bottom: 2px solid var(--border-color);
    }

    /* Card styling */
    .element-container,
    .stMarkdown,
    div[data-testid="stMetricValue"] {
        background-color: transparent;
    }

    div[data-testid="metric-container"] {
        background-color: var(--bg-white);
        border-radius: var(--radius-lg);
        padding: 24px;
        box-shadow: 0 2px 8px var(--shadow);
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }

    div[data-testid="metric-container"]:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 16px var(--shadow-lg);
    }

    /* Metric styling */
    div[data-testid="stMetricValue"] {
        font-size: 32px;
        font-weight: 700;
        color: var(--text-primary);
    }

    div[data-testid="stMetricLabel"] {
        font-size: 12px;
        color: var(--text-secondary);
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }

    /* Briefing summary card */
    .briefing-summary {
        background: var(--bg-white);
        padding: 24px;
        border-radius: var(--radius-lg);
        box-shadow: 0 2px 8px var(--shadow);
        margin-bottom: 24px;
    }

    .briefing-summary h3 {
        color: var(--text-primary);
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 12px;
    }

    /* Sentiment badge */
    .sentiment-badge {
        display: inline-block;
        padding: 8px 16px;
        border-radius: var(--radius-sm);
        font-weight: 600;
        font-size: 14px;
        margin-bottom: 16px;
        position: relative;
        overflow: hidden;
    }

    .sentiment-badge::before {
        content: '';
        position: absolute;
        left: 0;
        top: 0;
        bottom: 0;
        width: 4px;
    }

    .sentiment-badge.positive {
        background-color: rgba(46, 204, 113, 0.1);
        color: var(--sentiment-positive);
    }

    .sentiment-badge.positive::before {
        background-color: var(--sentiment-positive);
    }

    .sentiment-badge.negative {
        background-color: rgba(231, 76, 60, 0.1);
        color: var(--sentiment-negative);
    }

    .sentiment-badge.negative::before {
        background-color: var(--sentiment-negative);
    }

    .sentiment-badge.neutral {
        background-color: rgba(149, 165, 166, 0.1);
        color: var(--sentiment-neutral);
    }

    .sentiment-badge.neutral::before {
        background-color: var(--sentiment-neutral);
    }

    /* Dataframe styling */
    div[data-testid="stDataFrame"] {
        background-color: var(--bg-white);
        border-radius: var(--radius-lg);
        padding: 16px;
        box-shadow: 0 2px 8px var(--shadow);
    }

    /* Chart containers */
    div[data-testid="stPlotlyChart"] {
        background-color: var(--bg-white);
        border-radius: var(--radius-lg);
        padding: 16px;
        box-shadow: 0 2px 8px var(--shadow);
    }

    /* Expander styling */
    div[data-testid="stExpander"] {
        background-color: var(--bg-white);
        border-radius: var(--radius-lg);
        border: 1px solid var(--border-color);
        box-shadow: 0 2px 8px var(--shadow);
    }

    /* Buttons */
    .stButton > button {
        background-color: var(--accent-blue);
        color: white;
        border-radius: var(--radius-md);
        padding: 12px 24px;
        border: none;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: #2980b9;
        transform: translateY(-2px);
        box-shadow: 0 4px 12px var(--shadow-lg);
    }

    /* Sidebar styling */
    section[data-testid="stSidebar"] {
        background-color: var(--sidebar-dark);
    }

    section[data-testid="stSidebar"] * {
        color: #A0A0A0 !important;
    }

    section[data-testid="stSidebar"] h3 {
        color: var(--accent-yellow) !important;
    }

    /* Info/Warning/Error boxes */
    .stAlert {
        border-radius: var(--radius-md);
        border-left-width: 4px;
    }

    /* Divider */
    hr {
        border-color: var(--border-color);
        margin: 24px 0;
    }

    /* Custom scrollbar */
    ::-webkit-scrollbar {
        width: 8px;
        height: 8px;
    }

    ::-webkit-scrollbar-track {
        background: var(--bg-cream);
    }

    ::-webkit-scrollbar-thumb {
        background: var(--border-color);
        border-radius: 4px;
    }

    ::-webkit-scrollbar-thumb:hover {
        background: var(--text-secondary);
    }
</style>
""", unsafe_allow_html=True)

# Initialize database connection
@st.cache_resource
def get_database():
    """Initialize database connection (cached)"""
    try:
        return SupabaseClient()
    except Exception as e:
        logger.error(f"Database connection failed: {e}")
        return None

db = get_database()

# Data loading functions with caching
@st.cache_data(ttl=300)  # 5-minute cache
def load_sentiment_overview(days: int):
    """Load aggregated sentiment statistics"""
    if not db:
        return None
    return db.get_sentiment_overview(days=days)

@st.cache_data(ttl=300)
def load_recent_videos(days: int, limit: int = 50):
    """Load recent videos"""
    if not db:
        return None
    return db.get_recent_videos(days=days, limit=limit)

# ============================================
# HEADER
# ============================================
st.markdown('<div class="main-header">📊 Project S - Public Sentiment Overview</div>', unsafe_allow_html=True)
st.caption(f"Last updated: {datetime.now().strftime('%B %d, %Y at %H:%M')}")

# Minimal filter in collapsed sidebar
with st.sidebar:
    st.markdown("### Filters")
    days_filter = st.slider("Time Period (days)", 1, 30, 7, help="Analysis period")
    auto_refresh = st.checkbox("Auto-refresh (5 min)", value=False)

    if auto_refresh:
        st.info("Dashboard will refresh every 5 minutes")

# Check database connection
if not db:
    st.error("❌ Database connection failed. Please check your configuration.")
    st.stop()

# Load data
overview = load_sentiment_overview(days_filter)
videos = load_recent_videos(days_filter)

if not overview:
    st.warning("No data available. Start scraping to populate the dashboard.")
    st.stop()

# ============================================
# SECTION 1: BRIEFING SUMMARY (Plain Language)
# ============================================
st.markdown("---")
st.markdown('<div class="section-header">Overview of Public Sentiment</div>', unsafe_allow_html=True)

# Generate plain language summary with sentiment badge
avg_sentiment = overview["avg_sentiment"]
if avg_sentiment >= 7:
    sentiment_label = "Very Positive"
    badge_class = "positive"
elif avg_sentiment >= 5:
    sentiment_label = "Moderately Positive"
    badge_class = "positive"
elif avg_sentiment >= 3:
    sentiment_label = "Neutral"
    badge_class = "neutral"
else:
    sentiment_label = "Negative"
    badge_class = "negative"

total_engagement = overview.get("total_views", 0)
analysis_coverage = int(overview['total_analyzed']/overview['total_videos']*100) if overview['total_videos'] > 0 else 0

summary_html = f"""
<div class="briefing-summary">
    <div class="sentiment-badge {badge_class}">{sentiment_label}</div>
    <h3>Briefing Summary</h3>
    <p style="color: var(--text-secondary); line-height: 1.6; margin-bottom: 20px;">
        Public sentiment is {sentiment_label.lower()}, with {overview['total_videos']} videos tracked over the past {days_filter} days.
        Total engagement reached {total_engagement:,} views across all platforms.
    </p>
    <div style="border-top: 1px solid var(--border-color); padding-top: 16px;">
        <h4 style="font-size: 14px; font-weight: 600; margin-bottom: 12px;">Key Metrics</h4>
        <ul style="list-style: none; padding: 0; margin: 0;">
            <li style="padding: 8px 0; color: var(--text-secondary);">
                <strong style="color: var(--text-primary);">Analysis Coverage:</strong> {overview['total_analyzed']} videos analyzed ({analysis_coverage}%)
            </li>
            <li style="padding: 8px 0; color: var(--text-secondary);">
                <strong style="color: var(--text-primary);">Trending Topic:</strong> {overview.get('top_keyword', 'N/A')}
            </li>
            <li style="padding: 8px 0; color: var(--text-secondary);">
                <strong style="color: var(--text-primary);">Sentiment Score:</strong> {avg_sentiment}/10
            </li>
        </ul>
    </div>
</div>
"""

st.markdown(summary_html, unsafe_allow_html=True)

# ============================================
# SECTION 2: METRICS AT A GLANCE
# ============================================
col1, col2, col3, col4 = st.columns(4)

with col1:
    st.metric(
        label="Total Videos",
        value=f"{overview['total_videos']}",
        delta=None
    )

with col2:
    st.metric(
        label="Analyzed",
        value=f"{overview['total_analyzed']}",
        delta=None
    )

with col3:
    sentiment_score = overview['avg_sentiment']
    sentiment_color = "🟢" if sentiment_score >= 6 else "🔴" if sentiment_score <= 4 else "🟡"
    st.metric(
        label=f"{sentiment_color} Avg Sentiment",
        value=f"{sentiment_score}/10",
        delta=None
    )

with col4:
    st.metric(
        label="Total Reach",
        value=f"{total_engagement:,}",
        delta=None,
        help="Total views across all videos"
    )

st.markdown("---")

# ============================================
# SECTION 3: SENTIMENT DISTRIBUTION
# ============================================
col_left, col_right = st.columns([1, 1])

with col_left:
    st.markdown('<div class="section-header">Overall Public Sentiment</div>', unsafe_allow_html=True)

    # Sentiment breakdown
    sentiment_breakdown = overview.get("sentiment_breakdown", {})

    if sentiment_breakdown:
        # Create DataFrame for chart
        sentiment_df = pd.DataFrame([
            {"Sentiment": k, "Count": v} for k, v in sentiment_breakdown.items()
        ])

        # Color mapping - Updated to match UI design
        color_map = {
            "Positive": "#2ECC71",  # Green
            "Negative": "#E74C3C",  # Red
            "Neutral": "#95A5A6",   # Gray
            "Mixed": "#F39C12"      # Yellow-Orange
        }

        # Pie chart with restrained design
        fig = px.pie(
            sentiment_df,
            values="Count",
            names="Sentiment",
            color="Sentiment",
            color_discrete_map=color_map,
            hole=0.4
        )

        fig.update_traces(
            textposition='inside',
            textinfo='percent+label',
            hovertemplate='%{label}: %{value} videos<extra></extra>'
        )

        fig.update_layout(
            showlegend=False,
            margin=dict(t=20, b=20, l=20, r=20),
            height=300,
            font=dict(size=14)
        )

        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("No sentiment data available yet.")

with col_right:
    st.markdown('<div class="section-header">Key Issues</div>', unsafe_allow_html=True)

    # Extract top keywords from videos
    if videos:
        keyword_counts = {}
        for video in videos:
            kw = video.get("search_keyword")
            if kw:
                keyword_counts[kw] = keyword_counts.get(kw, 0) + 1

        # Sort by frequency
        sorted_keywords = sorted(keyword_counts.items(), key=lambda x: x[1], reverse=True)[:5]

        for i, (keyword, count) in enumerate(sorted_keywords, 1):
            sentiment_icon = "🔥" if i == 1 else "📍"
            st.markdown(f"**{i}. {sentiment_icon} {keyword}**")
            st.caption(f"{count} videos tracked")

            if i < len(sorted_keywords):
                st.markdown("")  # Spacing
    else:
        st.info("No keyword data available yet.")

st.markdown("---")

# ============================================
# SECTION 4: RECENT ACTIVITY (Expandable)
# ============================================
st.markdown('<div class="section-header">News and Social Media Summary</div>', unsafe_allow_html=True)

if videos:
    # Create DataFrame
    video_df = pd.DataFrame(videos)

    # Display summary
    st.caption(f"Showing {len(videos)} most recent videos from the past {days_filter} days")

    # Compact table view
    display_df = video_df[[
        "author_username",
        "description",
        "views_count",
        "likes_count",
        "search_keyword",
        "scraped_at"
    ]].copy()

    display_df.columns = ["Author", "Description", "Views", "Likes", "Keyword", "Scraped"]

    # Format description (truncate)
    display_df["Description"] = display_df["Description"].apply(lambda x: str(x)[:60] + "..." if len(str(x)) > 60 else str(x))

    # Format dates
    display_df["Scraped"] = pd.to_datetime(display_df["Scraped"]).dt.strftime("%b %d, %H:%M")

    # Display table
    st.dataframe(
        display_df,
        hide_index=True,
        use_container_width=True,
        height=300
    )

    # Expandable details
    with st.expander("📋 View Detailed Analysis"):
        selected_video = st.selectbox(
            "Select a video to view analysis",
            range(len(videos)),
            format_func=lambda i: f"{videos[i]['author_username']}: {videos[i]['description'][:50]}..."
        )

        if selected_video is not None:
            video = videos[selected_video]

            col_a, col_b = st.columns([1, 1])

            with col_a:
                st.markdown("**Video Details**")
                st.write(f"**Author:** {video['author_username']}")
                st.write(f"**Description:** {video['description']}")
                st.write(f"**Views:** {video['views_count']:,}")
                st.write(f"**Likes:** {video['likes_count']:,}")
                st.write(f"**Hashtags:** {', '.join(video.get('hashtags', []))}")

            with col_b:
                st.markdown("**AI Analysis**")

                # Fetch sentiment analysis
                try:
                    sentiment_response = db.supabase.table("sentiment_analysis")\
                        .select("*")\
                        .eq("video_id", video["id"])\
                        .execute()

                    if sentiment_response.data:
                        analysis = sentiment_response.data[0]
                        st.info(f"**Topic:** {analysis.get('topic', 'N/A')}")
                        st.write(f"**Discussion:** {analysis.get('discussion_points', 'N/A')}")
                        st.write(f"**Sentiment:** {analysis.get('sentiment', 'N/A')} ({analysis.get('sentiment_score', 'N/A')}/10)")
                    else:
                        st.warning("No analysis available for this video")
                except Exception as e:
                    st.error(f"Error loading analysis: {e}")

else:
    st.info("No videos found for the selected time period.")

# ============================================
# FOOTER
# ============================================
st.markdown("---")
st.caption("Project S - Digital Briefing Board | Data refreshes every 5 minutes")

# Auto-refresh logic
if auto_refresh:
    import time
    time.sleep(300)  # 5 minutes
    st.rerun()
