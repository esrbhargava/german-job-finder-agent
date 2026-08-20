import sys
import os
import asyncio

# Add src/ directory to module search path
sys.path.append(os.path.join(os.path.dirname(__file__), "src"))

from filter import filter_and_rank_jobs
from notify import generate_digest

# Import async scraper function from src/scraper.py
try:
    from scraper import scrape_job_page
except ImportError:
    scrape_job_page = None

# Import API fetcher if present
try:
    from api_fetcher import fetch_arbeitnow_jobs
except ImportError:
    fetch_arbeitnow_jobs = None


def run_scraping_step():
    """Triggers both Crawl4AI scraper and API fetchers."""
    # 1. API Fetching (Arbeitnow)
    if fetch_arbeitnow_jobs:
        print("  -> Running API fetcher (Arbeitnow)...")
        try:
            fetch_arbeitnow_jobs()
            print("  -> [SUCCESS] API jobs fetched and stored.")
        except Exception as e:
            print(f"  -> [ERROR] API fetcher failed: {e}")

    # 2. Async Web Crawling (Crawl4AI)
    if scrape_job_page:
        target_url = "https://www.arbeitnow.com/jobs/germany/data-engineer"
        print(f"  -> Running Crawl4AI web crawler on: {target_url}")
        try:
            markdown_content = asyncio.run(scrape_job_page(target_url))
            if markdown_content:
                print("  -> [SUCCESS] Web crawler extracted target page content.")
        except Exception as e:
            print(f"  -> [ERROR] Async crawler failed: {e}")


def main():
    print("=" * 50)
    print("🚀 Starting German Job Finder Agent Pipeline")
    print("=" * 50)

    # 1. Fetch raw jobs
    print("\n[STEP 1/3] Running scrapers to fetch latest job postings...")
    run_scraping_step()

    # 2. Filter & Rank Jobs
    print("\n[STEP 2/3] Filtering and ranking jobs...")
    ranked_jobs = filter_and_rank_jobs()
    print(f"[SUCCESS] Filtered {len(ranked_jobs)} relevant roles.")

    # 3. Generate Digest
    print("\n[STEP 3/3] Generating job digest...")
    digest_path = "data/digest.md"
    generate_digest(ranked_jobs[:10], output_path=digest_path)

    print("\n" + "=" * 50)
    print("✅ Pipeline execution complete!")
    print(f"📄 Digest available at: {digest_path}")
    print("=" * 50)


if __name__ == "__main__":
    main()