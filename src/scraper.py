import asyncio
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode

async def scrape_job_page(target_url: str):
    """
    Fetches raw Markdown content using anti-bot bypass configurations.
    """
    print(f"[1/3] Launching browser with anti-bot bypass: {target_url}")

    # Configure browser to mimic a real human user
    browser_config = BrowserConfig(
        headless=True,
        verbose=False,
        # Stealth settings to pass Cloudflare checks:
        headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"}
    )

    # Configure crawl settings with magic_mode enabled for Cloudflare bypass
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        magic=True,            # Automatically simulates human cursor and window behavior
        remove_overlay_elements=True, # Removes popups/cookie banners
        page_timeout=30000     # Gives Cloudflare enough time to pass the challenge
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

if __name__ == "__main__":
    # Target URL
    test_url = "https://germantechjobs.de/jobs/Data-Engineer"
    
    # Run the async crawler
    markdown_output = asyncio.run(scrape_job_page(test_url))
    
    if markdown_output:
        print("\n--- SAMPLE EXTRACTED MARKDOWN (FIRST 1000 CHARS) ---")
        print(markdown_output[:1000])
        print("-----------------------------------------------------")