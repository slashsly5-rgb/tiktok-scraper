import asyncio
from playwright.async_api import async_playwright
import urllib.parse

class TikTokScraper:
    def __init__(self, headless=True):
        self.headless = headless
        self.browser = None
        self.context = None
        self.playwright = None

    async def start(self):
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=self.headless,
            args=['--disable-blink-features=AutomationControlled']
        )
        self.context = await self.browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/114.0.0.0 Safari/537.36",
            viewport={'width': 1280, 'height': 720},
            locale='en-US',
            timezone_id='America/New_York'
        )
        # Add init script to hide webdriver property
        await self.context.add_init_script("""
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
        """)

    async def stop(self):
        if self.context:
            await self.context.close()
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()

    async def search_videos(self, keyword, limit=5):
        page = await self.context.new_page()
        encoded_keyword = urllib.parse.quote(keyword)
        url = f"https://www.tiktok.com/search?q={encoded_keyword}"
        
        print(f"Navigating to {url}")
        await page.goto(url)
        
        # Wait for results to load
        video_links = []
        # Try to find any links to videos if the specific container fails
        try:
            await page.wait_for_selector('a[href*="/video/"]', timeout=10000)
        except:
            print("Timeout waiting for video links")
            # Debug logic...
            await page.screenshot(path="debug_search_timeout.png")
            return []

        while len(video_links) < limit:
            elements = await page.query_selector_all('a[href*="/video/"]')
            for el in elements:
                href = await el.get_attribute('href')
                if href and '/video/' in href and href not in video_links:
                    video_links.append(href)
                    if len(video_links) >= limit:
                        break
            
            if len(video_links) < limit:
                await page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
                await asyncio.sleep(2)
        
        await page.close()
        return video_links[:limit]

    async def scrape_video_details(self, url):
        import random
        page = await self.context.new_page()
        print(f"Scraping {url}")
        
        data = {'url': url}
        max_retries = 2
        
        for attempt in range(max_retries + 1):
            try:
                await page.goto(url)
                # Random delay to mimic human
                await asyncio.sleep(random.uniform(2, 5))
                
                # Wait for load
                try:
                    await page.wait_for_load_state('networkidle', timeout=10000)
                except:
                    pass

                # Try JSON extraction first
                import json
                import re
                content = await page.content()
                
                # ... (JSON extraction logic same as before, abbreviated for brevity in this tool call, but I need to include it or the file will be broken. 
                # Actually, I should just wrap the existing logic in the retry loop or keep it simple.)
                # Let's just add the DOM fallbacks AFTER the existing JSON block, and keep the page load robust.
                
                # Check if we got blocked (simple check)
                if "verify" in await page.title() or "captcha" in content.lower():
                    print("Captcha detected, waiting longer...")
                    await asyncio.sleep(5)
                    continue # Retry
                
                break # Success
            except Exception as e:
                print(f"Attempt {attempt} failed: {e}")
                if attempt == max_retries:
                    await page.close()
                    return None

        # ... (JSON Extraction Block - keeping existing logic but ensuring variables exist) ...
        # I will rewrite the JSON block to be safe
        
        try:
            content = await page.content()
            sigi_match = re.search(r'<script id="SIGI_STATE" type="application/json">(.*?)</script>', content)
            if sigi_match:
                sigi_data = json.loads(sigi_match.group(1))
                item_module = sigi_data.get('ItemModule', {})
                for key, item in item_module.items():
                    data['description'] = item.get('desc', data.get('description', ''))
                    data['author'] = item.get('author', data.get('author', ''))
                    stats = item.get('stats', {})
                    data['stats'] = {
                        'views': stats.get('playCount', 0),
                        'likes': stats.get('diggCount', 0),
                        'shares': stats.get('shareCount', 0),
                        'comments': stats.get('commentCount', 0)
                    }
                    video_info = item.get('video', {})
                    data['thumbnail'] = video_info.get('cover', '')
                    challenges = item.get('challenges', [])
                    data['hashtags'] = [c.get('title') for c in challenges]
                    break
            
            # Universal Data Fallback
            if 'description' not in data:
                univ_match = re.search(r'<script id="__UNIVERSAL_DATA_FOR_REHYDRATION__" type="application/json">(.*?)</script>', content)
                if univ_match:
                    univ_data = json.loads(univ_match.group(1))
                    default_scope = univ_data.get('__DEFAULT_SCOPE__', {})
                    webapp_video_detail = default_scope.get('webapp.video-detail', {})
                    item_info = webapp_video_detail.get('itemInfo', {}).get('itemStruct', {})
                    if item_info:
                        data['description'] = item_info.get('desc', data.get('description', ''))
                        data['author'] = item_info.get('author', {}).get('nickname', data.get('author', ''))
                        stats = item_info.get('stats', {})
                        data['stats'] = {
                            'views': stats.get('playCount', 0),
                            'likes': stats.get('diggCount', 0),
                            'shares': stats.get('shareCount', 0),
                            'comments': stats.get('commentCount', 0)
                        }
                        video_info = item_info.get('video', {})
                        data['thumbnail'] = video_info.get('cover', '')
                        challenges = item_info.get('challenges', [])
                        data['hashtags'] = [c.get('title') for c in challenges]

        except Exception as e:
            print(f"JSON extraction failed: {e}")

        # --- DOM/META FALLBACKS ---
        
        # Description
        if not data.get('description'):
            try:
                # 1. Try Meta Description (Very reliable)
                meta_desc = await page.query_selector('meta[name="description"]')
                if meta_desc:
                    content = await meta_desc.get_attribute('content')
                    # Clean up "Watch [Author] video..." prefix if present
                    data['description'] = content.split(' on TikTok')[0]
                
                # 2. Try Page Title
                if not data.get('description'):
                    title = await page.title()
                    # Title format: "Description | Author | TikTok" or similar
                    if "|" in title:
                        data['description'] = title.split('|')[0].strip()
                    else:
                        data['description'] = title

                # 3. Try DOM
                if not data.get('description'):
                    desc_el = await page.query_selector('[data-e2e="browse-video-desc"]')
                    if not desc_el: desc_el = await page.query_selector('h1')
                    data['description'] = await desc_el.inner_text() if desc_el else "No description found"
            except: data['description'] = ""

        # Thumbnail
        if not data.get('thumbnail'):
            try:
                # Try OpenGraph Image
                og_img = await page.query_selector('meta[property="og:image"]')
                if og_img:
                    data['thumbnail'] = await og_img.get_attribute('content')
            except: pass

        # Author
        if not data.get('author'):
            try:
                author_el = await page.query_selector('[data-e2e="browse-user-detail"] h3')
                if not author_el: author_el = await page.query_selector('span[data-e2e="browse-username"]')
                data['author'] = await author_el.inner_text() if author_el else "Unknown Author"
            except: data['author'] = ""

        # Stats (DOM Fallback)
        if 'stats' not in data:
            data['stats'] = {}
            try:
                likes_el = await page.query_selector('[data-e2e="like-count"]')
                data['stats']['likes'] = await likes_el.inner_text() if likes_el else "N/A"
                
                comments_el = await page.query_selector('[data-e2e="comment-count"]')
                data['stats']['comments'] = await comments_el.inner_text() if comments_el else "N/A"
                
                # Views often not shown on video page detail, only on feed.
                data['stats']['views'] = "N/A" 
            except: pass

        # Hashtags (DOM Fallback)
        if 'hashtags' not in data:
            try:
                # Hashtags are usually links in the description
                tag_els = await page.query_selector_all('a[href*="/tag/"]')
                data['hashtags'] = [await t.inner_text() for t in tag_els]
            except: data['hashtags'] = []

        # Comments (Scroll and scrape)
        await page.evaluate("window.scrollTo(0, 500)")
        await asyncio.sleep(3)
        
        comments = []
        comment_elements = await page.query_selector_all('[data-e2e="comment-level-1"]')
        if not comment_elements:
             comment_elements = await page.query_selector_all('div[class*="DivCommentContentContainer"]')

        for el in comment_elements[:20]: 
            text_el = await el.query_selector('p[data-e2e="comment-level-1__content"]')
            if not text_el: text_el = await el.query_selector('p')
            if text_el:
                text = await text_el.inner_text()
                if "trouble playing" not in text:
                    comments.append(text)
        
        if not comments:
             ps = await page.query_selector_all('p')
             for p in ps[:20]:
                 text = await p.inner_text()
                 if len(text) > 5 and len(text) < 200 and "trouble playing" not in text:
                     comments.append(text)

        data['comments'] = comments
        
        await page.close()
        return data
