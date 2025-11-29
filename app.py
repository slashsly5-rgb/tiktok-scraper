import streamlit as st
import asyncio
import sys
from scraper import TikTokScraper
from analyzer import Analyzer
from dotenv import load_dotenv
import os

# Fix for Windows asyncio loop
if sys.platform == 'win32':
    asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())

# Ensure Playwright browsers are installed (for Streamlit Cloud)
import subprocess
try:
    subprocess.run(["playwright", "install", "chromium"], check=True)
except Exception as e:
    print(f"Error installing playwright: {e}")

# Load env vars
load_dotenv()

st.set_page_config(page_title="TikTok Scraper & Analyzer by Dr. Rahmat Aidil Djubair", layout="wide")

st.title("🎵 TikTok Scraper & Analyzer by Dr. Rahmat Aidil Djubair")
st.markdown("Search for videos, scrape details, and analyze sentiment using AI.")

# Sidebar for controls
with st.sidebar:
    st.header("Settings")
    keyword = st.text_input("Search Keyword", "funny cats")
    limit = st.slider("Number of Videos", min_value=1, max_value=10, value=3)
    headless = st.checkbox("Headless Mode", value=True, help="Run browser in background")
    
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        st.warning("⚠️ OpenAI API Key not found in .env. Analysis will be disabled.")
    else:
        st.success("✅ OpenAI API Key detected.")

    start_btn = st.button("Start Scraping", type="primary")

async def run_scraper(keyword, limit, headless):
    scraper = TikTokScraper(headless=headless)
    analyzer = Analyzer()
    
    status_text = st.empty()
    progress_bar = st.progress(0)
    
    try:
        status_text.text("Initializing browser...")
        await scraper.start()
        
        status_text.text(f"Searching for '{keyword}'...")
        video_urls = await scraper.search_videos(keyword, limit=limit)
        
        if not video_urls:
            st.error("No videos found. Try a different keyword.")
            if os.path.exists("search_debug.png"):
                st.image("search_debug.png", caption="Debug: What the scraper saw")
            return []
            
        status_text.text(f"Found {len(video_urls)} videos. Starting scrape...")
        
        results = []
        for i, url in enumerate(video_urls):
            progress = (i / len(video_urls))
            progress_bar.progress(progress)
            status_text.text(f"Scraping video {i+1}/{len(video_urls)}...")
            
            data = await scraper.scrape_video_details(url)
            if data:
                # Analyze
                status_text.text(f"Analyzing video {i+1}...")
                analysis = analyzer.analyze_video(
                    data.get('comments', []),
                    data.get('description', ''),
                    data.get('hashtags', [])
                )
                data['analysis'] = analysis
                
                results.append(data)
        
        progress_bar.progress(1.0)
        status_text.text("Done!")
        return results
        
    finally:
        await scraper.stop()

if start_btn:
    if not keyword:
        st.error("Please enter a keyword.")
    else:
        with st.spinner("Running scraper... This may take a minute."):
            # Run the async function
            results = asyncio.run(run_scraper(keyword, limit, headless))
            
            if results:
                st.divider()
                st.subheader(f"Results for '{keyword}'")
                
                for vid in results:
                    with st.container():
                        st.markdown(f"### {vid.get('description', 'Video')[:50]}...")
                        
                        col1, col2, col3 = st.columns([1, 2, 2])
                        
                        with col1:
                            # Display Screenshot if available
                            if vid.get('screenshot_base64'):
                                import base64
                                image_bytes = base64.b64decode(vid.get('screenshot_base64'))
                                st.image(image_bytes, caption="Page Screenshot", use_container_width=True)
                            elif vid.get('thumbnail'):
                                st.image(vid['thumbnail'], use_container_width=True)
                            else:
                                st.text("No Thumbnail")
                            
                            st.markdown(f"[Watch Video]({vid['url']})")

                        with col2:
                            st.markdown("#### 📊 Stats")
                            stats = vid.get('stats', {})
                            s_col1, s_col2 = st.columns(2)
                            s_col1.metric("Views", stats.get('views', 'N/A'))
                            s_col2.metric("Likes", stats.get('likes', 'N/A'))
                            
                            st.markdown("#### 🏷️ Hashtags")
                            tags = vid.get('hashtags', [])
                            if tags:
                                st.markdown(" ".join([f"`#{t}`" for t in tags]))
                            else:
                                st.text("No hashtags")
                            st.markdown("#### 🧠 AI Insights")
                            analysis = vid.get('analysis', {})
                            
                            st.info(f"**Topic:** {analysis.get('topic', 'N/A')}")
                            st.write(f"**Discussion:** {analysis.get('discussion', 'N/A')}")
                            
                            sent = analysis.get('sentiment', 'N/A')
                            score = analysis.get('score', 'N/A')
                            if "Positive" in sent:
                                st.success(f"Sentiment: {sent} ({score}/10)")
                            elif "Negative" in sent:
                                st.error(f"Sentiment: {sent} ({score}/10)")
                            else:
                                st.warning(f"Sentiment: {sent} ({score}/10)")

                        st.divider()
