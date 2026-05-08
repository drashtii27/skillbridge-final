import hashlib
import asyncio
import re
from datetime import datetime, timezone, timedelta
from typing import Optional
import httpx
from loguru import logger
from ..core.config import get_settings


def _strip_html(text: str) -> str:
    return re.sub(r"<[^>]+>", " ", text).replace("&amp;", "&").replace("&nbsp;", " ").strip()


def _is_relevant(job_title: str, role: str) -> bool:
    """Return True if the job title is relevant to the target role."""
    role_words = set(w.lower() for w in re.split(r"[\s/\-]+", role) if len(w) > 2)
    title_lower = job_title.lower()
    return any(word in title_lower for word in role_words)


def _make_hash(title: str, company: str) -> str:
    return hashlib.md5(f"{title}{company}".lower().encode()).hexdigest()


def _is_recent(date_str: Optional[str], hours: int = 24) -> bool:
    """Return True if date_str is within the last `hours` hours."""
    if not date_str:
        return True
    try:
        for fmt in ("%Y-%m-%dT%H:%M:%S", "%Y-%m-%d", "%Y-%m-%dT%H:%M:%SZ", "%Y-%m-%dT%H:%M:%S.%fZ"):
            try:
                dt = datetime.strptime(date_str[:19], fmt[:len(date_str[:19])])
                dt = dt.replace(tzinfo=timezone.utc)
                return (datetime.now(timezone.utc) - dt) < timedelta(hours=hours)
            except ValueError:
                continue
    except Exception:
        pass
    return True


async def _fetch_adzuna(client: httpx.AsyncClient, role: str, count: int) -> list[dict]:
    settings = get_settings()
    if not settings.adzuna_app_id or not settings.adzuna_app_key:
        return []
    try:
        r = await client.get(
            "https://api.adzuna.com/v1/api/jobs/us/search/1",
            params={
                "app_id": settings.adzuna_app_id,
                "app_key": settings.adzuna_app_key,
                "what": role,
                "results_per_page": count,
                "content-type": "application/json",
            },
            timeout=8,
        )
        r.raise_for_status()
        jobs = []
        for item in r.json().get("results", []):
            jobs.append({
                "title": item.get("title", ""),
                "company": item.get("company", {}).get("display_name", ""),
                "location": item.get("location", {}).get("display_name", ""),
                "salary_min": int(item.get("salary_min") or 0),
                "salary_max": int(item.get("salary_max") or 0),
                "url": item.get("redirect_url", ""),
                "description_snippet": item.get("description", "")[:300],
                "source": "Adzuna",
                "posted_at": item.get("created", ""),
                "hash": _make_hash(item.get("title", ""), item.get("company", {}).get("display_name", "")),
            })
        return jobs
    except Exception as e:
        logger.warning(f"Adzuna failed: {e}")
        return []


async def _fetch_remotive(client: httpx.AsyncClient, role: str, count: int) -> list[dict]:
    """Remotive — free remote job board API, no auth required."""
    try:
        r = await client.get(
            "https://remotive.com/api/remote-jobs",
            params={"search": role, "limit": count},
            timeout=8,
        )
        r.raise_for_status()
        jobs = []
        for item in r.json().get("jobs", [])[:count]:
            jobs.append({
                "title": item.get("title", ""),
                "company": item.get("company_name", ""),
                "location": item.get("candidate_required_location", "Remote"),
                "salary_min": 0,
                "salary_max": 0,
                "url": item.get("url", ""),
                "description_snippet": _strip_html(item.get("description", ""))[:300],
                "source": "Remotive",
                "posted_at": item.get("publication_date", ""),
                "hash": _make_hash(item.get("title", ""), item.get("company_name", "")),
            })
        return jobs
    except Exception as e:
        logger.warning(f"Remotive failed: {e}")
        return []


async def _fetch_jobicy(client: httpx.AsyncClient, role: str, count: int) -> list[dict]:
    """Jobicy — free remote job API, no auth required."""
    try:
        r = await client.get(
            "https://jobicy.com/api/v2/remote-jobs",
            params={"keyword": role, "count": count},
            timeout=8,
        )
        r.raise_for_status()
        jobs = []
        for item in r.json().get("jobs", [])[:count]:
            jobs.append({
                "title": item.get("jobTitle", ""),
                "company": item.get("companyName", ""),
                "location": item.get("jobGeo", "Remote"),
                "salary_min": 0,
                "salary_max": 0,
                "url": item.get("url", ""),
                "description_snippet": item.get("jobExcerpt", "")[:300],
                "source": "Jobicy",
                "posted_at": item.get("pubDate", ""),
                "hash": _make_hash(item.get("jobTitle", ""), item.get("companyName", "")),
            })
        return jobs
    except Exception as e:
        logger.warning(f"Jobicy failed: {e}")
        return []


async def _fetch_the_muse(client: httpx.AsyncClient, role: str, count: int) -> list[dict]:
    """The Muse — free job board API."""
    try:
        # The Muse paginates; fetch page 1
        r = await client.get(
            "https://www.themuse.com/api/public/jobs",
            params={"keyword": role, "page": 1, "descending": "true"},
            timeout=8,
        )
        r.raise_for_status()
        jobs = []
        for item in r.json().get("results", [])[:count]:
            locations = item.get("locations", [{}])
            loc = locations[0].get("name", "US") if locations else "US"
            company = item.get("company", {}).get("short_name", "")
            jobs.append({
                "title": item.get("name", ""),
                "company": company,
                "location": loc,
                "salary_min": 0,
                "salary_max": 0,
                "url": item.get("refs", {}).get("landing_page", ""),
                "description_snippet": _strip_html(item.get("contents", ""))[:300],
                "source": "The Muse",
                "posted_at": item.get("publication_date", ""),
                "hash": _make_hash(item.get("name", ""), company),
            })
        return jobs
    except Exception as e:
        logger.warning(f"The Muse failed: {e}")
        return []


def _mock_jobs(role: str, count: int) -> list[dict]:
    companies = ["Google", "Meta", "Stripe", "Databricks", "Scale AI", "OpenAI", "Anthropic", "Figma", "Notion", "Linear"]
    levels = ["Senior", "Staff", "Lead", "Mid-Level", "Principal"]
    cities = ["San Francisco, CA", "New York, NY", "Austin, TX", "Seattle, WA", "Remote"]
    boards = ["LinkedIn", "Indeed", "Jobright", "Glassdoor", "Lever"]
    jobs = []
    for i in range(min(count, len(companies))):
        company = companies[i]
        level = levels[i % len(levels)]
        city = cities[i % len(cities)]
        salary_base = 130000 + (i * 15000)
        jobs.append({
            "title": f"{level} {role}",
            "company": company,
            "location": city,
            "salary_min": salary_base,
            "salary_max": salary_base + 40000,
            "url": f"https://jobs.lever.co/{company.lower().replace(' ', '-')}/skillbridge-demo",
            "description_snippet": f"We're looking for a {level} {role} to join our team at {company}. You'll work on cutting-edge problems at scale.",
            "source": boards[i % len(boards)],
            "posted_at": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S"),
            "hash": _make_hash(f"{level} {role}", company),
        })
    return jobs


async def fetch_jobs_multi_source(role: str, count_per_source: int = 6) -> list[dict]:
    """Fetch from Adzuna + Remotive + Jobicy + The Muse concurrently."""
    async with httpx.AsyncClient(follow_redirects=True) as client:
        results = await asyncio.gather(
            _fetch_adzuna(client, role, count_per_source),
            _fetch_remotive(client, role, count_per_source),
            _fetch_jobicy(client, role, count_per_source),
            _fetch_the_muse(client, role, count_per_source),
            return_exceptions=True,
        )

    all_jobs: list[dict] = []
    seen_hashes: set[str] = set()
    for result in results:
        if isinstance(result, list):
            for job in result:
                h = job.get("hash", "")
                if h and h not in seen_hashes and _is_relevant(job.get("title", ""), role):
                    seen_hashes.add(h)
                    all_jobs.append(job)

    if not all_jobs:
        logger.warning("All job APIs failed — returning mock jobs")
        return _mock_jobs(role, count_per_source * 2)

    # Sort so most recently posted appear first
    all_jobs.sort(key=lambda j: j.get("posted_at", ""), reverse=True)
    return all_jobs[:count_per_source * 4]


# Sync wrapper for FastAPI routes that run in a sync context
def fetch_adzuna_jobs(role: str, location: str = "us", count: int = 10) -> list[dict]:
    """Legacy sync entry-point kept for backwards compatibility."""
    try:
        return asyncio.run(fetch_jobs_multi_source(role, count_per_source=max(4, count // 4)))
    except RuntimeError:
        # Already inside an event loop (e.g., called from async FastAPI route)
        import concurrent.futures
        with concurrent.futures.ThreadPoolExecutor() as pool:
            future = pool.submit(asyncio.run, fetch_jobs_multi_source(role, count_per_source=max(4, count // 4)))
            return future.result()
