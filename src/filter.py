import json
import re
from typing import List, Dict, Any
from urllib.parse import unquote
from storage import load_existing_jobs

VISA_KEYWORDS = ["visa", "sponsorship", "relocation", "blue card", "work permit"]
ENGLISH_KEYWORDS = ["english", "international team", "no german required"]
DATA_CORE_KEYWORDS = ["data engineer", "python", "pyspark", "etl", "sql", "data pipeline", "fastapi", "postgresql"]

# Target locations
ALLOWED_LOCATIONS = ["germany", "berlin", "munich", "hamburg", "frankfurt", "cologne", "stuttgart", "remote"]
# Promoted/junk listing terms to ignore
EXCLUDE_TERMS = ["1000+", "curated visa", "paid option", "course"]

def normalize_text(text: str) -> str:
    """Decodes URL encoding (%20 -> space), removes legal suffixes, and strips special chars."""
    text = unquote(text).lower()
    # Strip common company suffixes so 'Superhuman Inc' matches 'Superhuman'
    text = re.sub(r'\b(inc|gmbh|llc|ltd|corp|platform)\b', '', text)
    return re.sub(r'[^a-zA-Z0-9]', '', text)

def filter_and_rank_jobs() -> List[Dict[str, Any]]:
    jobs = load_existing_jobs()
    if not jobs:
        print("[WARN] No jobs found in storage to filter.")
        return []

    ranked_jobs = []
    seen_jobs = set()  # Track unique (title, company) pairs

    for job in jobs:
        title = job.get("title", "").lower()
        company = job.get("company", "").lower()
        location = job.get("location", "").lower()
        
        # 1. Skip promotional/junk posts
        if any(term in title for term in EXCLUDE_TERMS):
            continue

        # 2. Enforce Germany / Remote location filter
        if not any(loc in location for loc in ALLOWED_LOCATIONS):
            continue

        # 3. Deduplicate across scraping sources/pages
        dedup_key = (normalize_text(title), normalize_text(company))
        if dedup_key in seen_jobs:
            continue
        seen_jobs.add(dedup_key)

        score = 0
        match_reasons = []

        searchable_text = f"{title} {' '.join(job.get('tags', []))} {' '.join(job.get('tech_stack', []))}".lower()

        # Check for Visa & Relocation indicators
        for kw in VISA_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", searchable_text):
                score += 3
                match_reasons.append(f"Visa/Relocation ({kw.title()})")
                break

        # Check for English environment
        for kw in ENGLISH_KEYWORDS:
            if re.search(rf"\b{re.escape(kw)}\b", searchable_text):
                score += 2
                match_reasons.append("English-Friendly")
                break

        # Check for Core Data Stack with strict word boundaries
        matched_tech = []
        for tech in DATA_CORE_KEYWORDS:
            pattern = rf"\b{re.escape(tech)}\b"
            if re.search(pattern, searchable_text) or re.search(pattern, title):
                matched_tech.append(tech)

        if matched_tech:
            score += (len(matched_tech) * 2)
            match_reasons.append(f"Data Stack ({', '.join(matched_tech).title()})")

        # Bonus weight (+3) if key role terms appear directly in the job TITLE
        primary_roles = ["data engineer", "backend", "data platform"]
        if any(re.search(rf"\b{re.escape(role)}\b", title) for role in primary_roles):
            score += 3
            match_reasons.append("Direct Title Match")

        if score > 0:
            job_copy = dict(job)
            job_copy["match_score"] = score
            job_copy["match_reasons"] = match_reasons
            ranked_jobs.append(job_copy)

    ranked_jobs.sort(key=lambda x: x["match_score"], reverse=True)
    return ranked_jobs

if __name__ == "__main__":
    ranked = filter_and_rank_jobs()
    print(f"\n--- Refined Germany Data Engineering Filter ---")
    print(f"Target Roles Matched: {len(ranked)}\n")

    for idx, job in enumerate(ranked[:5], 1):
        print(f"[{idx}] Score: {job['match_score']} | {job['title']} @ {job['company']}")
        print(f"    Location: {job['location']}")
        print(f"    Reasons: {', '.join(job['match_reasons'])}")
        print(f"    URL: {job.get('url') or job.get('apply_url', '')}\n")