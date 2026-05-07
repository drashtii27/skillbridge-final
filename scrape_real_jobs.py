"""
SkillBridge AI – Real-World Job Scraper
Scrapes REAL jobs from LinkedIn, Indeed, Glassdoor, ZipRecruiter via:
  1. JSearch API (RapidAPI FREE tier — 200 req/month, aggregates Google for Jobs)
  2. RemoteOK API (FREE, no key needed)
  3. Arbeitnow API (FREE, no key needed)
  4. Adzuna API (already configured)

Setup for JSearch:
  1. Go to https://rapidapi.com/letscrape-6bRBa3QguO5/api/jsearch
  2. Sign up (free) → Subscribe to FREE plan
  3. Copy your X-RapidAPI-Key → paste in .env as RAPIDAPI_KEY

Usage:
  python scrape_real_jobs.py                    # Scrape all sources
  python scrape_real_jobs.py --roles "Software Engineer" "Data Analyst"
  python scrape_real_jobs.py --load-db          # Also load to PostgreSQL
"""
import sys, json, time, argparse, os, hashlib
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

import requests
from loguru import logger
from config import RAW, ALL_ROLES, ADZUNA_ID, ADZUNA_KEY
from utils import clean, save_json, delay

RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")


# ═══════════════════════════════════════════════════════════════
#  1. JSearch API (LinkedIn, Indeed, Glassdoor, ZipRecruiter)
#     FREE: 200 requests/month on RapidAPI
# ═══════════════════════════════════════════════════════════════
def scrape_jsearch(role, pages=2):
    """Scrape jobs from JSearch. Fail fast on 403/429."""
    if not RAPIDAPI_KEY:
        logger.warning("RAPIDAPI_KEY not set — skipping JSearch.")
        return []

    jobs = []
    url = "https://jsearch.p.rapidapi.com/search"
    headers = {
        "X-RapidAPI-Key": RAPIDAPI_KEY,
        "X-RapidAPI-Host": "jsearch.p.rapidapi.com",
    }

    for page in range(1, pages + 1):
        try:
            r = requests.get(
                url,
                headers=headers,
                params={
                    "query": f"{role} in United States",
                    "page": str(page),
                    "num_pages": "1",
                    "date_posted": "month",
                },
                timeout=20,
            )

            if r.status_code == 403:
                logger.error(
                    f"JSearch [{role}] page {page}: 403 Forbidden. "
                    "Skipping JSearch. Check RapidAPI key/subscription/quota."
                )
                return jobs

            if r.status_code == 429:
                logger.error(
                    f"JSearch [{role}] page {page}: 429 Too Many Requests. "
                    "Skipping JSearch for this run."
                )
                return jobs

            r.raise_for_status()
            data = r.json().get("data", [])

            for item in data:
                desc = clean(item.get("job_description", ""))
                jobs.append({
                    "source": item.get("job_publisher", "jsearch"),
                    "role": role,
                    "title": clean(item.get("job_title", "")),
                    "company": clean(item.get("employer_name", "")),
                    "location": f"{item.get('job_city', '')}, {item.get('job_state', '')}",
                    "description": desc[:3000],
                    "url": item.get("job_apply_link", ""),
                    "salary_min": item.get("job_min_salary"),
                    "salary_max": item.get("job_max_salary"),
                    "posted_at": item.get("job_posted_at_datetime_utc", ""),
                    "is_remote": item.get("job_is_remote", False),
                })

            logger.info(f"JSearch [{role}] page {page}: {len(data)} jobs")
            time.sleep(5)

        except Exception as e:
            logger.error(f"JSearch [{role}] page {page}: {e}")
            return jobs

    return jobs

# ═══════════════════════════════════════════════════════════════
#  2. RemoteOK API (FREE, no key needed)
# ═══════════════════════════════════════════════════════════════
def scrape_remoteok():
    """Scrape real remote jobs from RemoteOK (FREE, no API key)."""
    jobs = []
    try:
        r = requests.get(
            "https://remoteok.com/api",
            headers={"User-Agent": "SkillBridgeAI/1.0"},
            timeout=15,
        )
        r.raise_for_status()
        data = r.json()

        # First item is metadata, skip it
        for item in data[1:]:
            if isinstance(item, dict):
                tags = item.get("tags", [])
                jobs.append({
                    "source": "remoteok",
                    "role": item.get("position", ""),
                    "title": clean(item.get("position", "")),
                    "company": clean(item.get("company", "")),
                    "location": "Remote",
                    "description": clean(item.get("description", ""))[:3000],
                    "url": item.get("url", ""),
                    "tags": tags,
                    "posted_at": item.get("date", ""),
                })

        logger.info(f"RemoteOK: {len(jobs)} jobs")

    except Exception as e:
        logger.error(f"RemoteOK: {e}")

    return jobs


# ═══════════════════════════════════════════════════════════════
#  3. Arbeitnow API (FREE, no key needed)
# ═══════════════════════════════════════════════════════════════
def scrape_arbeitnow(pages=3):
    """Scrape real jobs from Arbeitnow (FREE, no API key)."""
    jobs = []
    for page in range(1, pages + 1):
        try:
            r = requests.get(
                f"https://www.arbeitnow.com/api/job-board-api?page={page}",
                timeout=15,
            )
            r.raise_for_status()
            data = r.json().get("data", [])

            for item in data:
                jobs.append({
                    "source": "arbeitnow",
                    "role": clean(item.get("title", "")),
                    "title": clean(item.get("title", "")),
                    "company": clean(item.get("company_name", "")),
                    "location": clean(item.get("location", "")),
                    "description": clean(item.get("description", ""))[:3000],
                    "url": item.get("url", ""),
                    "is_remote": item.get("remote", False),
                    "tags": item.get("tags", []),
                })

            logger.info(f"Arbeitnow page {page}: {len(data)} jobs")
            delay(1, 2)

        except Exception as e:
            logger.error(f"Arbeitnow page {page}: {e}")
            break

    return jobs


# ═══════════════════════════════════════════════════════════════
#  4. Adzuna API (already configured)
# ═══════════════════════════════════════════════════════════════
def scrape_adzuna(role, pages=3):
    """Scrape from Adzuna API."""
    jobs = []
    for p in range(1, pages + 1):
        try:
            r = requests.get(
                f"https://api.adzuna.com/v1/api/jobs/us/search/{p}",
                params={"app_id": ADZUNA_ID, "app_key": ADZUNA_KEY,
                        "results_per_page": 50, "what": role, "max_days_old": 30},
                timeout=15,
            )
            r.raise_for_status()
            for item in r.json().get("results", []):
                jobs.append({
                    "source": "adzuna",
                    "role": role,
                    "title": clean(item.get("title", "")),
                    "company": clean(item.get("company", {}).get("display_name", "")),
                    "location": clean(item.get("location", {}).get("display_name", "")),
                    "description": clean(item.get("description", ""))[:3000],
                    "url": item.get("redirect_url", ""),
                })
            delay(1, 2)
        except Exception as e:
            logger.error(f"Adzuna [{role}] p{p}: {e}")
            break
    return jobs


# ═══════════════════════════════════════════════════════════════
#  Master scraper
# ═══════════════════════════════════════════════════════════════
def scrape_all_real(roles=None, jsearch_pages=1, adzuna_pages=2):
    """Scrape real jobs from all sources."""
    roles = roles or ALL_ROLES[:15]  # Top 15 roles
    all_jobs = []

    print(f"\n  Scraping real jobs for {len(roles)} roles...\n")

    # 1. JSearch (LinkedIn/Indeed/Glassdoor)
    if RAPIDAPI_KEY:
        print("  📡 JSearch (LinkedIn, Indeed, Glassdoor, ZipRecruiter)...")
        for role in roles:
            jobs = scrape_jsearch(role, pages=jsearch_pages)
            all_jobs.extend(jobs)
            print(f"    {role}: {len(jobs)} jobs")
    else:
        print("  ⚠️  JSearch skipped (set RAPIDAPI_KEY in .env)")

    # 2. RemoteOK (free, no key)
    print("\n  📡 RemoteOK (free, no key needed)...")
    remote_jobs = scrape_remoteok()
    all_jobs.extend(remote_jobs)
    print(f"    RemoteOK: {len(remote_jobs)} jobs")

    # 3. Arbeitnow (free, no key)
    print("\n  📡 Arbeitnow (free, no key needed)...")
    arb_jobs = scrape_arbeitnow(pages=3)
    all_jobs.extend(arb_jobs)
    print(f"    Arbeitnow: {len(arb_jobs)} jobs")

    # 4. Adzuna (already configured)
    print("\n  📡 Adzuna API...")
    for role in roles[:10]:
        jobs = scrape_adzuna(role, pages=adzuna_pages)
        all_jobs.extend(jobs)
        print(f"    {role}: {len(jobs)} jobs")

    # Deduplicate by title+company hash
    seen = set()
    unique_jobs = []
    for job in all_jobs:
        h = hashlib.sha256(f"{job.get('title','')}_{job.get('company','')}".encode()).hexdigest()
        if h not in seen:
            seen.add(h)
            unique_jobs.append(job)

    # Save
    save_json(unique_jobs, RAW / "real_jobs.json")

    # Source breakdown
    sources = {}
    for j in unique_jobs:
        s = j.get("source", "unknown")
        sources[s] = sources.get(s, 0) + 1

    print(f"\n  ✅ Total: {len(unique_jobs)} unique real-world jobs scraped")
    print(f"  Sources: {json.dumps(sources, indent=4)}")
    print(f"  Saved → data/raw/real_jobs.json")

    return unique_jobs


def main():
    parser = argparse.ArgumentParser(description="Scrape real-world jobs")
    parser.add_argument("--roles", nargs="+", default=None, help="Roles to scrape")
    parser.add_argument("--load-db", action="store_true", help="Also load to PostgreSQL")
    args = parser.parse_args()

    jobs = scrape_all_real(roles=args.roles)

    if args.load_db:
        print("\n  Loading to PostgreSQL...")
        from database import init_db, load_jobs_to_db
        init_db()
        count = load_jobs_to_db(jobs)
        print(f"  ✅ {count} new jobs loaded to DB")


if __name__ == "__main__":
    main()
