import os
from datetime import datetime
from typing import List, Dict, Any
from filter import filter_and_rank_jobs

def generate_digest(top_jobs: List[Dict[str, Any]], output_path: str = "data/digest.md") -> str:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    today_str = datetime.now().strftime("%Y-%m-%d %H:%M")
    
    lines = []
    lines.append(f"# 🎯 Germany Data Engineering Job Digest")
    lines.append(f"**Generated:** {today_str} | **Top Matches Found:** {len(top_jobs)}\n")
    lines.append("---")
    
    if not top_jobs:
        lines.append("\n*No new high-priority roles matched the filtering criteria today.*")
    else:
        for idx, job in enumerate(top_jobs, 1):
            title = job.get("title", "N/A")
            company = job.get("company", "N/A")
            location = job.get("location", "N/A")
            score = job.get("match_score", 0)
            reasons = ", ".join(job.get("match_reasons", []))
            
            # Check multiple common key names for the URL
            url = (
                job.get("url")
                or job.get("apply_url")
                or job.get("link")
                or job.get("job_url")
                or "#"
            )
            
            lines.append(f"### {idx}. {title}")
            lines.append(f"- **Company:** {company}")
            lines.append(f"- **Location:** {location}")
            lines.append(f"- **Match Score:** {score}")
            lines.append(f"- **Highlights:** {reasons}")
            
            # Clean Markdown link formatting to prevent ugly URL wrapping
            if url != "#":
                lines.append(f"- **Apply Link:** [Click to Apply Direct]({url})\n")
            else:
                lines.append(f"- **Apply Link:** *N/A*\n")
    
    digest_content = "\n".join(lines)
    
    with open(output_path, "w", encoding="utf-8") as f:
        f.write(digest_content)
        
    print(f"[SUCCESS] Digest generated with {len(top_jobs)} roles -> {output_path}")
    return digest_content

if __name__ == "__main__":
    ranked = filter_and_rank_jobs()
    generate_digest(ranked[:10])