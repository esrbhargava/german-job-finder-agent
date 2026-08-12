import json
import os
from typing import List, Dict, Any

DATA_FILE = os.path.join("data", "jobs.json")

def load_existing_jobs() -> List[Dict[str, Any]]:
    """Loads existing jobs from local JSON file."""
    if not os.path.exists(DATA_FILE):
        return []
    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, IOError):
        return []

def save_jobs(jobs: List[Dict[str, Any]]) -> None:
    """Saves job listings to local JSON file."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(jobs, f, indent=4, ensure_ascii=False)

def deduplicate_and_save(new_jobs: List[Dict[str, Any]]) -> tuple[int, int]:
    """
    Appends only unique new jobs based on apply_url or title+company fallback.
    Returns (added_count, total_count).
    """
    existing_jobs = load_existing_jobs()
    
    # Track existing unique keys
    existing_keys = {
        job.get("apply_url") or f"{job.get('title')}_{job.get('company')}"
        for job in existing_jobs
    }
    
    added_count = 0
    for job in new_jobs:
        job_key = job.get("apply_url") or f"{job.get('title')}_{job.get('company')}"
        if job_key not in existing_keys:
            existing_jobs.append(job)
            existing_keys.add(job_key)
            added_count += 1
            
    if added_count > 0:
        save_jobs(existing_jobs)
        
    return added_count, len(existing_jobs)