import asyncio
import json
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig, CacheMode
from parser import parse_jobs_from_markdown

async def run_pipeline(url: str):
    print(f"=== Starting German Job Finder Agent ===")
    print(f"Target URL: {url}\n")
    
    # Configure browser with anti-detection flags
    browser_config = BrowserConfig(
        headless=False,  # Cloudflare allows non-headless browsers to solve JS challenges automatically
        extra_args=[
            "--disable-blink-features=AutomationControlled",
            "--no-sandbox"
        ],
        headers={
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36"
        }
    )
    
    # Allow time for Cloudflare JS to complete before grabbing content
    run_config = CrawlerRunConfig(
        cache_mode=CacheMode.BYPASS,
        delay_before_return_html=5.0  # Waits 5s for Cloudflare check to clear
    )

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(url=url, config=run_config)
        
        if not result.success:
            print(f"[ERROR] Failed to scrape page: {result.error_message}")
            return

        markdown_content = result.markdown.raw_markdown if result.markdown else ""
        print(f"[OK] Successfully scraped {len(markdown_content)} characters of Markdown.\n")

    # Send Markdown content to Gemini LLM for structured extraction
    jobs = parse_jobs_from_markdown(markdown_content)
    
    print("\n=== FINAL PARSED JOBS ===")
    print(json.dumps(jobs, indent=2))

if __name__ == "__main__":
    target_url = "https://germantechjobs.de/en/jobs/Data/all"
    asyncio.run(run_pipeline(target_url))