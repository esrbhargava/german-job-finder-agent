import httpx
from typing import List
from parser import JobPosting

ARBEITNOW_API_URL = "https://www.arbeitnow.com/api/job-board-api?visa_sponsorship=true"

def fetch_jobs_via_api() -> List[JobPosting]:
    """
    Directly fetches structured job data from public API endpoints.
    Bypasses Playwright, DOM rendering, and Gemini LLM parsing completely.
    """
    print("\n[API FETCH] Querying Arbeitnow Public API for Data/Visa jobs...")
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) Chrome/122.0.0.0 Safari/537.36"
    }

    try:
        response = httpx.get(ARBEITNOW_API_URL, headers=headers, timeout=10.0)
        response.raise_for_status()
        data = response.json()

        raw_jobs = data.get("data", [])
        parsed_jobs: List[JobPosting] = []

        for item in raw_jobs:
            title = item.get("title", "")
            title_lower = title.lower()
            if any(keyword in title_lower for keyword in ["data", "python", "backend", "etl", "database"]):
                tags = item.get("tags", [])
                job_url = item.get("url", "")
                
                job = JobPosting(
                    title=title,
                    company=item.get("company_name", "Unknown"),
                    location=item.get("location", "Germany / Remote"),
                    url=job_url,
                    apply_url=job_url,
                    salary="Not Specified",
                    tech_stack=tags if tags else ["Python", "Data Engineering"],
                    tags=tags
                )
                parsed_jobs.append(job)

        print(f"[API SUCCESS] Direct API returned {len(parsed_jobs)} relevant structured jobs in milliseconds!")
        return parsed_jobs

    except Exception as e:
        print(f"[API ERROR] Failed to fetch jobs via API: {e}")
        return []