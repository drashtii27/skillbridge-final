"""SkillBridge AI – Utilities."""
import re, json, hashlib, time, random
from pathlib import Path
from typing import List
from loguru import logger
from config import NOISE

logger.add("skillbridge.log", rotation="5 MB", level="INFO")

def clean(t):
    if not t: return ""
    t = re.sub(r"<[^>]+>", " ", t)
    t = re.sub(r"http\S+", "", t)
    return re.sub(r"\s+", " ", t).strip()

def is_noise(s):
    return s.lower().strip() in NOISE or len(s.strip()) <= 2

def filter_skills(skills):
    return [s.strip() for s in skills if not is_noise(s)]

def save_json(data, path: Path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f: json.dump(data, f, indent=2, default=str)

def load_json(path: Path):
    with open(path) as f: return json.load(f)

def delay(lo=1.0, hi=3.0):
    time.sleep(random.uniform(lo, hi))
