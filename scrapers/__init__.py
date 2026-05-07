"""SkillBridge AI – All Scrapers (Adzuna, Muse, LeetCode, HackerRank, SO, ESCO)."""
import requests
from typing import List, Dict
from loguru import logger
from config import ADZUNA_APP_ID, ADZUNA_APP_KEY, ADZUNA_COUNTRY, MUSE_BASE_URL, MUSE_API_KEY, STACKEXCHANGE_KEY, ESCO_BASE_URL, RAW
from utils import clean, delay, save_json

def scrape_adzuna(role, pages=2):
    jobs = []
    for p in range(1, pages+1):
        try:
            r = requests.get(f"https://api.adzuna.com/v1/api/jobs/{ADZUNA_COUNTRY}/search/{p}",
                params={"app_id": ADZUNA_APP_ID, "app_key": ADZUNA_APP_KEY, "results_per_page": 50, "what": role, "max_days_old": 30}, timeout=15)
            r.raise_for_status()
            for i in r.json().get("results", []):
                jobs.append({"source":"adzuna","role":role,"title":clean(i.get("title","")),"company":clean(i.get("company",{}).get("display_name","")),"description":clean(i.get("description",""))})
            delay(1,2)
        except Exception as e: logger.error(f"Adzuna: {e}"); break
    return jobs

def scrape_muse(role, pages=2):
    jobs = []
    for p in range(pages):
        try:
            params = {"page": p}
            if MUSE_API_KEY: params["api_key"] = MUSE_API_KEY
            r = requests.get(MUSE_BASE_URL, params=params, timeout=15); r.raise_for_status()
            for i in r.json().get("results", []):
                if role.lower() in i.get("name","").lower():
                    jobs.append({"source":"muse","role":role,"title":clean(i.get("name","")),"description":clean(i.get("contents",""))})
            delay(1,2)
        except Exception as e: logger.error(f"Muse: {e}"); break
    return jobs

def scrape_leetcode(limit=300):
    qs = []
    query = 'query q($l:Int,$s:Int,$f:QuestionListFilterInput){problemsetQuestionList:questionList(categorySlug:"",limit:$l,skip:$s,filters:$f){questions:data{title titleSlug difficulty topicTags{name}isPaidOnly}}}'
    for skip in range(0, limit, 100):
        try:
            r = requests.post("https://leetcode.com/graphql", json={"query":query,"variables":{"l":100,"s":skip,"f":{}}},
                headers={"Content-Type":"application/json","Referer":"https://leetcode.com"}, timeout=30); r.raise_for_status()
            for p in r.json().get("data",{}).get("problemsetQuestionList",{}).get("questions",[]):
                if not p.get("isPaidOnly"):
                    qs.append({"source":"leetcode","question":p["title"],"difficulty":p.get("difficulty","Medium"),
                              "tags":[t["name"] for t in p.get("topicTags",[])],"url":f"https://leetcode.com/problems/{p['titleSlug']}/"})
            delay(1,2)
        except Exception as e: logger.error(f"LC: {e}"); break
    return qs

def scrape_hackerrank():
    qs = []
    tracks = {"python":"Software Engineer","java":"Software Engineer","sql":"Data Analyst","algorithms":"Software Engineer","data-structures":"Software Engineer"}
    for track, role in tracks.items():
        try:
            r = requests.get(f"https://www.hackerrank.com/rest/contests/master/tracks/{track}/challenges", params={"offset":0,"limit":100}, timeout=15); r.raise_for_status()
            for i in r.json().get("models",[]):
                qs.append({"source":"hackerrank","question":i.get("name",""),"difficulty":i.get("difficulty_name","Medium"),"tags":[track],"role":role})
            delay(0.5,1)
        except Exception as e: logger.error(f"HR [{track}]: {e}")
    return qs

def scrape_stackoverflow(pages=3):
    qs = []
    for p in range(1, pages+1):
        try:
            params = {"page":p,"pagesize":100,"order":"desc","sort":"votes","tagged":"interview-questions","site":"stackoverflow"}
            if STACKEXCHANGE_KEY: params["key"] = STACKEXCHANGE_KEY
            r = requests.get("https://api.stackexchange.com/2.3/questions", params=params, timeout=15); r.raise_for_status()
            for i in r.json().get("items",[]):
                qs.append({"source":"stackoverflow","question":clean(i.get("title","")),"tags":i.get("tags",[])})
            delay(0.5,1)
        except Exception as e: logger.error(f"SO: {e}"); break
    return qs

def scrape_all(roles, pages=2):
    all_jobs, all_qs = [], []
    for role in roles:
        all_jobs.extend(scrape_adzuna(role, pages))
        all_jobs.extend(scrape_muse(role, pages))
    all_qs.extend(scrape_leetcode(300))
    all_qs.extend(scrape_hackerrank())
    all_qs.extend(scrape_stackoverflow(3))
    save_json(all_jobs, RAW / "jobs.json")
    save_json(all_qs, RAW / "questions.json")
    logger.info(f"TOTAL: {len(all_jobs)} jobs, {len(all_qs)} questions")
    return all_jobs, all_qs
