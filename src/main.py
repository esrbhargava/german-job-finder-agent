import asyncio
from scraper import scrape_job_page
from parser import parse_job_listings_from_markdown
from storage import deduplicate_and_save

TARGET_URLS = [
    "https://relocate.me/search?country=Germany&query=Data+Engineer",
    "https://www.arbeitnow.com/jobs/germany/data-engineer"
]

async def main():
    print("--- Starting German Job Finder Pipeline ---")
    
    total_added = 0
    for url in TARGET_URLS:
        print(f"\n[TARGET] Scraping: {url}")
        raw_markdown = await scrape_job_page(url)
        if not raw_markdown:
            continue

        jobs = parse_job_listings_from_markdown(raw_markdown)
        if jobs:
            added_count, current_total = deduplicate_and_save(jobs)
            total_added += added_count
            print(f"Added {added_count} new unique jobs from this source. Total in storage: {current_total}")
        else:
            print("[WARN] No structured jobs extracted from this source.")

    print("\n--- Pipeline Run Finished ---")
    print(f"Total new jobs added across all sources: {total_added}")

if __name__ == "__main__":
    asyncio.run(main())