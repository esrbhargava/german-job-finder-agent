import os
import json
from typing import List, Optional
from pydantic import BaseModel, Field
from google import genai
from google.genai import types
from dotenv import load_dotenv

load_dotenv()

class JobPosting(BaseModel):
    title: str = Field(description="Exact job title, e.g. Senior Data Engineer")
    company: str = Field(description="Company offering the position")
    location: str = Field(description="City in Germany, 'Remote', or 'Hybrid'")
    salary: Optional[str] = Field(description="Salary range if listed, otherwise 'N/A'")
    tech_stack: List[str] = Field(description="List of technologies mentioned, e.g. ['Python', 'SQL', 'Spark']")
    apply_url: str = Field(description="Full URL or link path to apply for the job")

class JobListings(BaseModel):
    jobs: List[JobPosting]

def parse_jobs_from_markdown(markdown_text: str) -> List[dict]:
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key:
        print("[ERROR] GEMINI_API_KEY not found in .env file!")
        return []

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an expert technical recruitment assistant.
    Analyze the following raw Markdown scraped from GermanTechJobs.
    Extract every single open job posting listed on the page.
    Do not skip any job card or listing.

    RAW MARKDOWN CONTENT:
    {markdown_text}
    """

    print("[1/2] Sending extracted Markdown to Gemini LLM for structured parsing...")

    try:
        response = client.models.generate_content(
            model='gemini-flash-latest',
            contents=prompt,
            config=types.GenerateContentConfig(
                response_mime_type="application/json",
                response_schema=JobListings,
                temperature=0.1
            ),
        )

        parsed_data = json.loads(response.text)
        jobs_list = parsed_data.get("jobs", [])
        print(f"[2/2] Successfully parsed {len(jobs_list)} structured job postings!")
        return jobs_list
    except Exception as e:
        print(f"[ERROR] Failed to parse JSON response: {e}")
        return []