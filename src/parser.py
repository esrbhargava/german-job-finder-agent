import os
import json
import time
from typing import List, Optional
from pydantic import BaseModel
from google import genai

# Define the Pydantic Schema for job listings
class JobPosting(BaseModel):
    title: str
    company: str
    location: str
    url: str
    apply_url: Optional[str] = None
    salary: Optional[str] = "Not Specified"
    tech_stack: List[str] = []
    tags: List[str] = []

def parse_job_listings_from_markdown(markdown_content: str) -> List[JobPosting]:
    """
    Uses Gemini API to extract structured JobPosting objects from raw Markdown scraped from the web.
    Includes automated retry logic for temporary 503 API demand spikes.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] GEMINI_API_KEY environment variable is not set.")
        return []

    client = genai.Client(api_key=api_key)

    prompt = f"""
    Extract all relevant job postings from the following Markdown content.
    Return a valid JSON array of objects, where each object matches this schema:
    - title (string): Job title
    - company (string): Company name
    - location (string): Location or Remote status
    - url (string): Job detail link
    - apply_url (string, optional): Direct application link if available, otherwise same as url
    - salary (string, optional): Salary range if mentioned, otherwise 'Not Specified'
    - tech_stack (list of strings): Technologies mentioned (e.g. Python, SQL, PySpark)
    - tags (list of strings): Other tags like Visa Sponsorship, Relocation, Full-time

    Markdown Content:
    {markdown_content}
    """

    print("[1/2] Sending extracted Markdown to Gemini LLM for structured parsing...")

    max_retries = 3
    response = None

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-3.6-flash",
                contents=prompt,
                config={
                    "response_mime_type": "application/json",
                    "response_schema": list[JobPosting]
                }
            )
            break
        except Exception as e:
            if "503" in str(e) and attempt < max_retries - 1:
                wait_time = (attempt + 1) * 3
                print(f"[RETRY] Gemini API busy (503). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                print(f"[ERROR] Failed to parse JSON response: {e}")
                return []

    if not response or not response.text:
        print("[WARN] Received empty response from Gemini API.")
        return []

    try:
        raw_data = json.loads(response.text)
        parsed_jobs = [JobPosting(**item) for item in raw_data]
        print(f"[2/2] Successfully parsed {len(parsed_jobs)} structured job postings!")
        return parsed_jobs
    except Exception as e:
        print(f"[ERROR] Failed to instantiate JobPosting schema from Gemini output: {e}")
        return []