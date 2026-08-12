import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def scrape_job_page(target_url: str):
    """
    Fetches raw Markdown content using anti-bot bypass configurations.
    """
    print(f"[1/3] Launching browser with anti-bot bypass: {target_url}")

    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
    )

    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        magic=True,
        remove_overlay_elements=True,
        flatten_shadow_dom=True,
        page_timeout=30000,
        delay_before_return_html=3.0
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=target_url, config=run_config)

        if result.success:
            print(f"[2/3] Successfully bypassed anti-bot check!")
            print(f"[3/3] Extracted {len(result.markdown)} characters of raw Markdown content.")
            return result.markdown
        else:
            print(f"[ERROR] Failed to crawl page: {result.error_message}")
            return None