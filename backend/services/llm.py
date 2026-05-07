"""
Multi-model LLM routing for SkillBridge.

4 models, each best-in-class for its task:
  Model 1 — NVIDIA Nemotron Ultra 253B (OpenRouter primary, Ollama fallback) → Roadmap Generation
  Model 2 — Mistral Small 3.2 24B (OpenRouter)                               → Skill Extraction
  Model 3 — DeepSeek R1 671B MoE (OpenRouter)                                → Market Insight / RAG
  Model 4 — Qwen3 235B (OpenRouter)                                          → Interview & Quiz Questions

Fallback chain for every model: try OpenRouter → fall back to local Ollama.
"""

import json
import re
from typing import Any, Optional
import httpx
from loguru import logger
from ..core.config import get_settings

def _or_model(attr: str) -> str:
    """Read model ID from settings so it's overridable via .env."""
    return getattr(get_settings(), attr)


# ─── Low-level callers ───────────────────────────────────────────────────────

async def _call_ollama(
    prompt: str,
    system: str,
    temperature: float,
    max_tokens: int,
    model_override: Optional[str] = None,
) -> Optional[str]:
    settings = get_settings()
    model = model_override or settings.ollama_model
    payload = {
        "model": model,
        "prompt": prompt,
        "system": system,
        "stream": False,
        "options": {"temperature": temperature, "num_predict": max_tokens},
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(f"{settings.ollama_base_url}/api/generate", json=payload)
            r.raise_for_status()
            return r.json().get("response", "")
    except Exception as e:
        logger.warning(f"Ollama ({model}) call failed: {e}")
        return None


async def _call_openrouter(
    prompt: str,
    system: str,
    temperature: float,
    max_tokens: int,
    model_id: str,
) -> Optional[str]:
    settings = get_settings()
    if not settings.openrouter_api_key:
        return None
    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})
    payload = {
        "model": model_id,
        "messages": messages,
        "temperature": temperature,
        "max_tokens": max_tokens,
    }
    headers = {
        "Authorization": f"Bearer {settings.openrouter_api_key}",
        "HTTP-Referer": "https://skillbridge.ai",
        "X-Title": "SkillBridge",
    }
    try:
        async with httpx.AsyncClient(timeout=120.0) as client:
            r = await client.post(
                "https://openrouter.ai/api/v1/chat/completions",
                json=payload,
                headers=headers,
            )
            r.raise_for_status()
            return r.json()["choices"][0]["message"]["content"]
    except Exception as e:
        logger.warning(f"OpenRouter ({model_id}) call failed: {e}")
        return None


# ─── Model 1: Nemotron (Ollama) — Roadmap Generation ────────────────────────

async def call_nemotron(
    prompt: str,
    system: str = "",
    temperature: float = 0.7,
    max_tokens: int = 4096,
    expect_json: bool = False,
) -> str:
    """
    Primary LLM for roadmap generation.
    OpenRouter (Nemotron Ultra 253B) → Llama 3.3 70B → Ollama fallback.
    """
    settings = get_settings()
    if settings.openrouter_api_key:
        # Primary: NVIDIA Nemotron Ultra 253B
        result = await _call_openrouter(
            prompt, system, temperature, max_tokens,
            settings.openrouter_model,  # nvidia/llama-3.1-nemotron-ultra-253b-v1:free
        )
        if result:
            return result
        # Secondary: Llama 3.3 70B
        result = await _call_openrouter(
            prompt, system, temperature, max_tokens,
            "meta-llama/llama-3.3-70b-instruct:free",
        )
        if result:
            return result
    result = await _call_ollama(prompt, system, temperature, max_tokens)
    if result:
        return result
    logger.error("All roadmap LLM options (OpenRouter + Ollama) failed.")
    return ""


# ─── Model 2: Mistral Small 3.2 24B — Skill Extraction ──────────────────────

async def call_mistral(
    prompt: str,
    system: str = "",
    temperature: float = 0.2,
    max_tokens: int = 1024,
) -> str:
    """
    Skill extraction LLM layer. Tries Mistral Small 24B → Nemotron Ultra 253B → Llama 3.3 70B.
    Note: GLiNER is the primary extractor; this LLM enriches the results.
    """
    result = await _call_openrouter(prompt, system, temperature, max_tokens, _or_model("skill_model"))
    if result:
        return result
    # Fallback: Nemotron Ultra 253B
    result = await _call_openrouter(prompt, system, temperature, max_tokens, "nvidia/llama-3.1-nemotron-ultra-253b-v1:free")
    if result:
        return result
    result = await _call_openrouter(prompt, system, temperature, max_tokens, "meta-llama/llama-3.3-70b-instruct:free")
    if result:
        return result
    logger.warning("All skill extraction LLMs failed — GLiNER result will be used as-is")
    return ""


# ─── Model 3: DeepSeek R1 671B MoE — Market Insight / RAG ───────────────────

async def call_llama70b(
    prompt: str,
    system: str = "",
    temperature: float = 0.6,
    max_tokens: int = 512,
) -> str:
    """
    DeepSeek R1 671B MoE — strongest reasoning for market analysis and RAG synthesis.
    Falls back to Nemotron Ultra 253B then Ollama.
    """
    result = await _call_openrouter(prompt, system, temperature, max_tokens, _or_model("insight_model"))
    if result:
        return result
    # Fallback: Nemotron Ultra 253B
    result = await _call_openrouter(prompt, system, temperature, max_tokens, "nvidia/llama-3.1-nemotron-ultra-253b-v1:free")
    if result:
        return result
    logger.warning("Market insight models failed — falling back to Ollama")
    return await _call_ollama(prompt, system, temperature, max_tokens) or ""


# ─── Model 4: Qwen3 235B — Interview & Quiz ─────────────────────────────────

async def call_qwen(
    prompt: str,
    system: str = "",
    temperature: float = 0.75,
    max_tokens: int = 3000,
) -> str:
    """
    Qwen3 235B (interview/quiz) → DeepSeek R1 → Ollama fallback.
    Best for structured interview questions and multiple-choice quiz generation.
    """
    result = await _call_openrouter(prompt, system, temperature, max_tokens, _or_model("interview_model"))
    if result:
        return result
    # Fallback: DeepSeek R1
    result = await _call_openrouter(prompt, system, temperature, max_tokens, "deepseek/deepseek-r1:free")
    if result:
        return result
    logger.warning("Interview models failed — falling back to Ollama")
    return await _call_ollama(prompt, system, temperature, max_tokens) or ""


# ─── JSON extraction helper ──────────────────────────────────────────────────

def extract_json(text: str) -> Any:
    """Pull the first valid JSON object or array out of a model response."""
    fence_match = re.search(r"```(?:json)?\s*([\s\S]+?)\s*```", text)
    if fence_match:
        try:
            return json.loads(fence_match.group(1))
        except json.JSONDecodeError:
            pass
    text = text.strip()
    for start_char, end_char in [("{", "}"), ("[", "]")]:
        start = text.find(start_char)
        end = text.rfind(end_char)
        if start != -1 and end != -1 and end > start:
            try:
                return json.loads(text[start : end + 1])
            except json.JSONDecodeError:
                pass
    return None


# ─── System prompts ──────────────────────────────────────────────────────────

SKILL_EXTRACT_SYSTEM = """You are an expert technical recruiter and skills extractor.
Given resume text, extract ALL technical skills across ANY engineering or tech domain.
Return ONLY a JSON array of strings.
Include: programming languages, frameworks, tools, hardware skills, instruments, simulation tools,
engineering standards, certifications, design software, lab equipment, methodologies, platforms.
Exclude pure soft skills like "communication" or "teamwork". Be thorough and inclusive."""

SKILL_GAP_SYSTEM = """You are a senior career analyst with real-time industry knowledge.
Given a user's skills and their target role, provide a concise, data-driven market insight
(2-3 sentences) about what the 2026 job market demands for this role.
Be specific: mention in-demand tools, average salary ranges, and the #1 skill gap."""

ROADMAP_SYSTEM = """You are an expert career coach and structured learning path designer.
Generate a detailed, week-by-week career roadmap as valid JSON. Follow the exact schema.
Include real YouTube video titles, real course platforms, and real practice platform URLs.
Be specific with weekly goals and daily plans. Output ONLY valid JSON, no markdown, no explanation."""

INTERVIEW_SYSTEM = """You are a principal engineer at a top-tier tech company conducting technical interviews.
Generate realistic, challenging interview questions that would actually be asked for this role and skill level.
Return ONLY a JSON array. Each object must include: question, difficulty, category, skills_tested, answer_outline."""

QUIZ_SYSTEM = """You are a technical educator designing assessments for career learners.
Generate multiple-choice quiz questions with exactly 4 options each.
Each question must have a clear single correct answer. Return ONLY a JSON array.
Include an 'explanation' field explaining why the correct answer is right."""


# ─── GLiNER local skill extractor ────────────────────────────────────────────

_gliner_model = None
_gliner_labels = [
    # Software / Data
    "programming language", "framework", "library", "database",
    "cloud platform", "tool", "technology", "technical skill",
    "methodology", "software", "algorithm", "data science skill",
    # Engineering (broader)
    "engineering skill", "hardware skill", "electronic component",
    "instrument", "simulation tool", "design software", "engineering standard",
    "certification", "technical competency", "industrial tool",
]

# Comprehensive keyword list for regex fallback — software + all engineering domains
_SKILL_KEYWORDS = [
    # Software / Data Science
    "python","sql","java","javascript","typescript","c++","c#","r","scala","go","rust","kotlin","swift",
    "react","angular","vue","node.js","django","flask","fastapi","spring","express","next.js","nuxt",
    "tensorflow","pytorch","keras","scikit-learn","pandas","numpy","scipy","matplotlib","seaborn","plotly",
    "spark","hadoop","kafka","airflow","dbt","databricks","snowflake","bigquery","redshift","hive",
    "mysql","postgresql","mongodb","redis","cassandra","elasticsearch","dynamodb","sqlite","oracle",
    "aws","azure","gcp","docker","kubernetes","terraform","ansible","jenkins","github actions","ci/cd",
    "git","linux","bash","shell scripting","rest api","graphql","microservices","devops","mlops",
    "machine learning","deep learning","nlp","computer vision","llm","transformers","bert","gpt",
    "tableau","power bi","looker","excel","vba","sas","spss","stata","matlab",
    "html","css","webpack","figma","jira","confluence","agile","scrum",
    "opencv","nltk","hugging face","langchain","vector database","rag","fine-tuning","lora",
    "data analysis","data visualization","data engineering","data modeling","etl","feature engineering",
    # Electrical Engineering
    "circuit design","pcb layout","pcb design","altium","kicad","eagle","cadence","orcad",
    "embedded c","embedded systems","rtos","firmware","microcontroller","arduino","raspberry pi",
    "power electronics","power systems","signal processing","signal integrity","signal analysis",
    "oscilloscope","multimeter","dmm","logic analyzer","spectrum analyzer","function generator",
    "fpga","vhdl","verilog","system verilog","pld","cpld","xilinx","altera","vivado",
    "matlab simulink","simulink","ltspice","spice","hspice","pspice","ansys","maxwell",
    "plc programming","scada","hmi","ladder logic","iec 61131","modbus","profibus","canbus","can bus",
    "emc","emi","electromagnetic compatibility","rf design","antenna design","microwave",
    "battery systems","bms","ev","electric vehicle","motor control","inverter","converter",
    "nec","ieee","iec standards","ul certification","iso 26262","functional safety",
    "hardware design","hardware testing","board bring-up","schematic capture","layout review",
    "trade studies","system engineering","requirements analysis","design verification",
    "usb","ethernet","spi","i2c","uart","rs232","rs485","pcie","ddr","sdram",
    "cad","autocad","solidworks","catia","revit","civil 3d",
    "structural analysis","finite element analysis","fea","cfd","thermodynamics",
    "project management","pmp","six sigma","lean","kaizen",
    # Biomedical / Chemical / Other Engineering
    "labview","ni instruments","national instruments","data acquisition","daq",
    "python","c","c++","assembly","arm","dsp","image processing",
]

def _extract_skills_gliner(text: str) -> list[str]:
    """Extract skills using GLiNER (local NER model, no API needed)."""
    global _gliner_model
    try:
        if _gliner_model is None:
            from gliner import GLiNER
            _gliner_model = GLiNER.from_pretrained("knowledgator/gliner-multitask-large-v0.5")
            logger.info("GLiNER loaded for skill extraction")
        ents = _gliner_model.predict_entities(text[:4000], _gliner_labels, threshold=0.30, flat_ner=True)
        seen: set[str] = set()
        skills = []
        for e in sorted(ents, key=lambda x: x["score"], reverse=True):
            name = e["text"].strip()
            # Filter OCR artifacts: no newlines, no leading special chars, reasonable length
            if (name.lower() not in seen
                    and 1 < len(name) < 60
                    and '\n' not in name
                    and not re.match(r'^[^a-zA-Z0-9]', name)):
                seen.add(name.lower())
                skills.append(name)
        return skills
    except Exception as e:
        logger.warning(f"GLiNER extraction failed: {e}")
        return []

def _extract_skills_regex(text: str) -> list[str]:
    """Regex keyword matching — guaranteed fallback that never fails."""
    import re
    text_lower = text.lower()
    found = []
    for kw in _SKILL_KEYWORDS:
        if kw.lower() in text_lower:
            found.append(kw.title() if kw.islower() else kw)
    # Grab multi-word capitalized phrases from a single line (e.g. "Signal Integrity Analysis")
    for line in text.splitlines():
        line = line.strip()
        phrases = re.findall(r'\b[A-Z][a-zA-Z]+(?:\s+[A-Z][a-zA-Z]+)+\b', line)
        _noise_words = {
            'Work','Experience','Professional','Summary','Education','Background',
            'Bachelor','Master','Science','University','State','Atlanta',
        }
        for p in phrases:
            words = p.split()
            if not any(w in _noise_words for w in words) and 3 < len(p) < 50:
                found.append(p)
    # Single capitalized tech terms/acronyms (PCB, USB, CAD, FPGA, etc.)
    single = re.findall(r'\b[A-Z][a-zA-Z0-9+#./]{1,}\b', text)
    _skip = {
        'The','And','For','With','This','That','Your','From','Have','More','Into',
        'Was','Are','Has','Not','But','Our','All','New','Can','Get','Its','One',
        'Will','May','Per','Two','Also','Each','Both','Such','Been','When','Than',
        'Upon','Using','Used','Under','Over','After','About','Above','Below',
        'Designed','Developed','Executed','Conducted','Supervised','Partnered',
        'Contributed','Engineered','Communicated','Delegated','Drafted','Wired',
        'Attended','Building','Leveraging','Providing','Following','Reviewing',
    }
    for c in single:
        if c not in _skip and '\n' not in c:
            found.append(c)
    return list(dict.fromkeys(found))[:60]


# ─── Task-specific callers (each uses its dedicated model) ───────────────────

async def extract_skills_from_text(resume_text: str) -> list[str]:
    """
    3-layer skill extraction:
    1. GLiNER (local NER — no API, always works)
    2. LLM via OpenRouter (enriches/adds to GLiNER results)
    3. Regex keyword fallback (guaranteed non-empty result)
    """
    # Layer 1: GLiNER — local NER, run in thread so it doesn't block the event loop
    import asyncio
    loop = asyncio.get_event_loop()
    try:
        gliner_skills = await asyncio.wait_for(
            loop.run_in_executor(None, _extract_skills_gliner, resume_text),
            timeout=25.0,
        )
    except asyncio.TimeoutError:
        logger.warning("GLiNER timed out — skipping to LLM layer")
        gliner_skills = []
    logger.info(f"GLiNER extracted {len(gliner_skills)} skills")

    # Layer 2: LLM enhancement (adds context-aware skills GLiNER may miss)
    llm_skills: list[str] = []
    prompt = (
        f"Extract ALL technical skills from this resume text. "
        f"Return ONLY a JSON array of skill name strings, nothing else.\n\n"
        f"{resume_text[:2500]}"
    )
    response = await call_mistral(prompt, SKILL_EXTRACT_SYSTEM, temperature=0.1, max_tokens=800)
    if response:
        result = extract_json(response)
        if isinstance(result, list):
            llm_skills = [str(s).strip() for s in result if s and len(str(s).strip()) > 1]

    # Merge GLiNER + LLM, deduplicate (case-insensitive)
    seen: set[str] = set()
    merged: list[str] = []
    for s in gliner_skills + llm_skills:
        if s.lower() not in seen:
            seen.add(s.lower())
            merged.append(s)

    if merged:
        return merged[:50]

    # Layer 3: Regex fallback — never returns empty
    logger.warning("GLiNER + LLM both empty — using regex fallback")
    return _extract_skills_regex(resume_text)


async def get_market_insight(role: str, skills: list[str], context: str = "") -> str:
    """Model 3 — DeepSeek R1 671B handles market insight and RAG synthesis."""
    prompt = f"""Role: {role}
User skills: {', '.join(skills[:15])}
{f'Live market context (from job boards): {context[:1500]}' if context else ''}

Provide a 2-3 sentence data-driven market insight for this role in 2026.
Mention specific in-demand tools, salary trends, and the biggest skill gap candidates face."""
    response = await call_llama70b(prompt, SKILL_GAP_SYSTEM, temperature=0.6, max_tokens=350)
    return response.strip() or (
        f"The {role} market in 2026 is highly competitive — top candidates combine deep technical "
        f"expertise with project portfolios. Companies are paying 15-25% premiums for engineers with "
        f"hands-on AI/ML integration experience."
    )


async def generate_interview_questions(
    role: str, skills: list[str], count: int = 10, context: str = ""
) -> list[dict]:
    """Model 4 — Qwen3 235B handles interview question generation."""
    schema_example = json.dumps({
        "question": "Explain the difference between L1 and L2 regularization",
        "difficulty": "Medium",
        "category": "Technical",
        "skills_tested": ["Machine Learning"],
        "answer_outline": [
            "L1 (Lasso) adds absolute value penalty — promotes sparsity",
            "L2 (Ridge) adds squared penalty — penalizes large weights",
            "L1 produces sparse solutions, L2 distributes weight more evenly",
        ],
    }, indent=2)
    prompt = f"""Role: {role}
Skills to test: {', '.join(skills[:10])}
{f'Reference context: {context[:800]}' if context else ''}

Generate {count} real interview questions a top company would ask. Schema for each:
{schema_example}

Return a JSON array of exactly {count} question objects."""
    response = await call_qwen(prompt, INTERVIEW_SYSTEM, temperature=0.75, max_tokens=3500)
    result = extract_json(response)
    if isinstance(result, list):
        return result
    return _fallback_interview_questions(role, skills, count)


async def generate_quiz_questions(role: str, skills: list[str], count: int = 15) -> list[dict]:
    """Model 4 — Qwen3 235B handles quiz generation. Falls back to static questions."""
    prompt = f"""Role: {role}, Skills focus: {', '.join(skills[:6])}
Generate exactly {count} multiple-choice quiz questions for a {role} interview assessment.
Each must have exactly 4 options and correct_index (0-3).
Schema: {{"question":"...","options":["A","B","C","D"],"correct_index":0,"skill_tag":"...","difficulty":"Easy|Medium|Hard","explanation":"..."}}
Return JSON array of exactly {count} objects. Cover different skills and mix difficulty levels."""
    response = await call_qwen(prompt, QUIZ_SYSTEM, temperature=0.7, max_tokens=4000)
    result = extract_json(response)
    if isinstance(result, list) and len(result) >= 5:
        return result[:count]
    return _fallback_quiz_questions(role, skills, count)


def _fallback_quiz_questions(role: str, skills: list[str], count: int) -> list[dict]:
    """Static MCQ bank covering common roles and skills."""
    bank: list[dict] = [
        # ── Python / Programming ──
        {"question": "What does the Python 'yield' keyword do?", "options": ["Returns a value and exits the function", "Pauses the function and returns a generator", "Raises an exception", "Imports a module"], "correct_index": 1, "skill_tag": "Python", "difficulty": "Medium", "explanation": "'yield' turns a function into a generator, pausing execution and returning a value each time next() is called."},
        {"question": "Which Python data structure maintains insertion order and allows duplicates?", "options": ["set", "dict (keys)", "list", "frozenset"], "correct_index": 2, "skill_tag": "Python", "difficulty": "Easy", "explanation": "Lists maintain insertion order and allow duplicate values. Sets and frozensets are unordered and unique."},
        {"question": "What is the time complexity of Python dict lookup?", "options": ["O(n)", "O(log n)", "O(1) average", "O(n²)"], "correct_index": 2, "skill_tag": "Python", "difficulty": "Medium", "explanation": "Python dicts use hash tables, giving O(1) average-case lookup."},
        {"question": "Which keyword makes a Python class attribute shared across all instances?", "options": ["global", "shared", "class-level (defined outside __init__)", "static"], "correct_index": 2, "skill_tag": "Python", "difficulty": "Medium", "explanation": "Attributes defined at class level (not inside __init__) are shared across all instances."},
        # ── SQL ──
        {"question": "What does a LEFT JOIN return?", "options": ["Only matching rows from both tables", "All rows from the left table and matching rows from the right", "Only rows from the right table", "The Cartesian product"], "correct_index": 1, "skill_tag": "SQL", "difficulty": "Easy", "explanation": "LEFT JOIN returns all rows from the left table, with NULL for non-matching right-table rows."},
        {"question": "Which SQL clause is used to filter aggregate results?", "options": ["WHERE", "HAVING", "GROUP BY", "ORDER BY"], "correct_index": 1, "skill_tag": "SQL", "difficulty": "Easy", "explanation": "HAVING filters after aggregation (like SUM, COUNT), while WHERE filters individual rows before aggregation."},
        {"question": "What is a database index primarily used for?", "options": ["Storing backups", "Enforcing uniqueness only", "Speeding up SELECT queries", "Compressing data"], "correct_index": 2, "skill_tag": "SQL", "difficulty": "Easy", "explanation": "Indexes create sorted data structures that allow the database to find rows without a full table scan."},
        {"question": "Which window function returns the rank of a row without gaps?", "options": ["RANK()", "ROW_NUMBER()", "DENSE_RANK()", "NTILE()"], "correct_index": 2, "skill_tag": "SQL", "difficulty": "Hard", "explanation": "DENSE_RANK() gives sequential rank values without gaps, unlike RANK() which skips numbers after ties."},
        # ── Data Engineering / Spark ──
        {"question": "What is Apache Spark's primary advantage over MapReduce?", "options": ["Better SQL support", "In-memory processing for faster computation", "Native Python support", "Easier cluster setup"], "correct_index": 1, "skill_tag": "Spark", "difficulty": "Easy", "explanation": "Spark keeps intermediate results in memory, avoiding the disk I/O overhead of MapReduce's write-between-stages approach."},
        {"question": "In Spark, what is a DataFrame transformation vs action?", "options": ["Transformations execute immediately; actions are lazy", "Actions execute immediately; transformations build a DAG", "Both execute immediately", "Both are lazy"], "correct_index": 1, "skill_tag": "Spark", "difficulty": "Medium", "explanation": "Transformations (map, filter) are lazy and build a DAG. Actions (collect, count) trigger execution."},
        {"question": "What is the purpose of Apache Kafka?", "options": ["Batch processing of large files", "Distributed streaming message queue", "SQL analytics engine", "Container orchestration"], "correct_index": 1, "skill_tag": "Kafka", "difficulty": "Easy", "explanation": "Kafka is a distributed event streaming platform for high-throughput, fault-tolerant message queues."},
        {"question": "What does ETL stand for in data engineering?", "options": ["Execute, Transform, Load", "Extract, Transform, Load", "Extract, Test, Launch", "Event, Transform, Log"], "correct_index": 1, "skill_tag": "Data Engineering", "difficulty": "Easy", "explanation": "ETL = Extract data from source, Transform it (clean, enrich), Load into the destination warehouse."},
        # ── Machine Learning ──
        {"question": "What does overfitting mean in machine learning?", "options": ["Model performs well on training data but poorly on new data", "Model is too simple to learn patterns", "Model takes too long to train", "Model uses too much memory"], "correct_index": 0, "skill_tag": "Machine Learning", "difficulty": "Easy", "explanation": "Overfitting occurs when a model memorizes training data instead of learning generalizable patterns."},
        {"question": "Which regularization technique sets some model weights to exactly zero?", "options": ["Ridge (L2)", "Dropout", "Lasso (L1)", "Batch Normalization"], "correct_index": 2, "skill_tag": "Machine Learning", "difficulty": "Medium", "explanation": "L1 (Lasso) regularization adds an absolute penalty that forces sparse weights, driving some to zero."},
        {"question": "What is the purpose of the learning rate in gradient descent?", "options": ["Number of training epochs", "Size of each step toward the minimum", "Fraction of data used per batch", "Number of hidden layers"], "correct_index": 1, "skill_tag": "Machine Learning", "difficulty": "Easy", "explanation": "The learning rate controls how large each weight update step is. Too high → overshooting; too low → slow convergence."},
        # ── Docker / DevOps ──
        {"question": "What does 'docker-compose up' do?", "options": ["Builds a single container", "Starts all services defined in docker-compose.yml", "Pushes images to DockerHub", "Runs tests inside a container"], "correct_index": 1, "skill_tag": "Docker", "difficulty": "Easy", "explanation": "docker-compose up reads the YAML config and starts all defined services, creating networks and volumes as needed."},
        {"question": "What is the difference between a Docker image and container?", "options": ["Images run; containers are templates", "Containers run; images are read-only templates", "They are identical", "Images are for Linux; containers for Windows"], "correct_index": 1, "skill_tag": "Docker", "difficulty": "Easy", "explanation": "An image is a read-only blueprint. A container is a running instance of that image with a writable layer."},
        # ── System Design ──
        {"question": "What is the CAP theorem?", "options": ["A distributed system can guarantee all three: Consistency, Availability, Partition Tolerance", "A distributed system can guarantee at most two of: Consistency, Availability, Partition Tolerance", "CAP describes CPU, API, and Performance trade-offs", "CAP is a database indexing strategy"], "correct_index": 1, "skill_tag": "System Design", "difficulty": "Medium", "explanation": "CAP theorem: in a distributed system you can only guarantee 2 of 3 properties: Consistency, Availability, Partition Tolerance."},
        {"question": "Which caching strategy writes data to cache and database simultaneously?", "options": ["Cache-aside (lazy loading)", "Write-through", "Write-back (write-behind)", "Read-through"], "correct_index": 1, "skill_tag": "System Design", "difficulty": "Hard", "explanation": "Write-through writes to cache and DB at the same time, ensuring consistency at the cost of write latency."},
        # ── General CS ──
        {"question": "What is Big O notation used for?", "options": ["Measuring exact execution time", "Describing algorithm complexity as input grows", "Counting lines of code", "Measuring memory in bytes"], "correct_index": 1, "skill_tag": "Algorithms", "difficulty": "Easy", "explanation": "Big O describes how algorithm time/space scales with input size n, ignoring constant factors."},
        {"question": "Which sorting algorithm has O(n log n) average complexity?", "options": ["Bubble sort", "Insertion sort", "Merge sort", "Selection sort"], "correct_index": 2, "skill_tag": "Algorithms", "difficulty": "Medium", "explanation": "Merge sort divides the array recursively and merges, giving O(n log n) in all cases."},
    ]
    # Prioritize questions matching the requested skills
    skill_lower = [s.lower() for s in skills]
    def relevance(q: dict) -> int:
        tag = q["skill_tag"].lower()
        return any(s in tag or tag in s for s in skill_lower)
    sorted_bank = sorted(bank, key=relevance, reverse=True)
    result = sorted_bank[:count]
    # If not enough, repeat from bank
    while len(result) < count:
        result.extend(sorted_bank[:count - len(result)])
    return result[:count]


async def get_adaptive_question(role: str, skills: list[str], step: int = 0) -> dict:
    """Model 3 — DeepSeek R1 understands context well for adaptive profiling."""
    ADAPTIVE_SYSTEM = """You are a personalized learning advisor.
Ask one targeted question to better understand the user's background, learning style, and goals.
Return ONLY a JSON object: {"question": "...", "options": ["...", "...", "...", "..."], "purpose": "..."}"""
    prompt = f"""User targeting: {role}
Current skills: {', '.join(skills[:8])}
Profiling step: {step + 1}/3

Ask a focused question to personalize their learning roadmap."""
    response = await call_llama70b(prompt, ADAPTIVE_SYSTEM, temperature=0.6, max_tokens=400)
    result = extract_json(response)
    if isinstance(result, dict):
        return result
    return {
        "question": "How many hours per week can you dedicate to learning?",
        "options": ["< 5 hours", "5-10 hours", "10-20 hours", "20+ hours"],
        "purpose": "Calibrate roadmap intensity and weekly goal size",
    }


def _fallback_interview_questions(role: str, skills: list[str], count: int) -> list[dict]:
    templates = [
        {
            "question": f"Explain the key concepts you need to master for a {role} role.",
            "difficulty": "Easy",
            "category": "Domain-Specific",
            "skills_tested": skills[:2],
            "answer_outline": [f"Focus on {s}" for s in skills[:3]],
        },
        {
            "question": f"Describe a project where you applied {skills[0] if skills else 'your skills'}.",
            "difficulty": "Medium",
            "category": "Behavioral",
            "skills_tested": skills[:2],
            "answer_outline": ["Use STAR method", "Quantify impact", "Highlight technical decisions"],
        },
    ]
    return (templates * ((count // 2) + 1))[:count]
