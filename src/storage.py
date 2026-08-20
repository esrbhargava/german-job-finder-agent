import json
import os
import hashlib
from typing import List, Tuple
from parser import JobPosting

DATA_DIR = "data"
STORAGE_FILE = os.path.join(DATA_DIR, "jobs.json")

def ensure_data_dir():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

def load_existing_jobs() -> List[dict]:
    ensure_data_dir()
    if not os.path.exists(STORAGE_FILE):
        return []
    try:
        with open(STORAGE_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        print(f"[ERROR] Failed to load existing jobs: {e}")
        return []

def deduplicate_and_save(new_jobs: List[JobPosting]) -> Tuple[int, int]:
    existing_jobs = load_existing_jobs()
    existing_hashes = {job.get("hash") for job in existing_jobs if "hash" in job}

    added_count = 0
    for job in new_jobs:
        # Support both Pydantic model and dict
        if isinstance(job, JobPosting):
            job_dict = job.model_dump()
        else:
            job_dict = dict(job)

        # Generate MD5 hash based on URL or title+company
        key_str = job_dict.get("apply_url") or job_dict.get("url") or f"{job_dict.get('title')}_{job_dict.get('company')}"
        job_hash = hashlib.md5(key_str.encode("utf-8")).hexdigest()
        job_dict["hash"] = job_hash

        if job_hash not in existing_hashes:
            existing_jobs.append(job_dict)
            existing_hashes.add(job_hash)
            added_count += 1

    ensure_data_dir()
    with open(STORAGE_FILE, "w", encoding="utf-8") as f:
        json.dump(existing_jobs, f, indent=2, ensure_ascii=False)

    return added_count, len(existing_jobs)