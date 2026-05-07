"""SkillBridge AI – Pipeline Runner with ETL"""
import argparse, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parent))

def cmd_data():
    """Generate sample data (no API needed)."""
    print("\n" + "="*60)
    print("  STEP: GENERATE SAMPLE DATA")
    print("="*60)
    from evaluation import generate_all_sample_data
    generate_all_sample_data()

def cmd_scrape():
    """Scrape live data from Adzuna, LeetCode, HackerRank, StackOverflow."""
    print("\n" + "="*60)
    print("  STEP: SCRAPE LIVE DATA")
    print("="*60)
    from scrapers import scrape_all
    from config import ALL_ROLES
    roles = ALL_ROLES[:10]
    print(f"  Scraping for roles: {roles}")
    jobs, qs = scrape_all(roles, pages=2)
    print(f"  ✅ Scraped: {len(jobs)} jobs, {len(qs)} questions")
    print(f"  Saved to: data/raw/jobs.json, data/raw/questions.json")
    return jobs, qs

def cmd_etl():
    """Run full ETL: init DB → load jobs → load questions → load taxonomy."""
    print("\n" + "="*60)
    print("  STEP: ETL PIPELINE (Extract → Transform → Load)")
    print("="*60)

    # Step 1: Init database (drops old tables, creates new ones)
    print("\n  [1/5] Initializing PostgreSQL database...")
    from database import init_db, load_jobs_to_db, load_questions_to_db, load_skills_taxonomy, get_db_stats
    engine = init_db()
    if not engine:
        print("  ❌ Database not connected. Check PG_URL in .env")
        return
    print("  ✅ Database tables created (dropped old schema)")

    # Step 2: Load raw data
    print("\n  [2/5] Loading raw data from JSON files...")
    from utils import load_json
    from config import RAW
    jobs = load_json(RAW / "jobs.json") if (RAW / "jobs.json").exists() else []
    qs = load_json(RAW / "questions.json") if (RAW / "questions.json").exists() else []
    print(f"  Found: {len(jobs)} jobs, {len(qs)} questions")

    # Step 3: Load jobs to PostgreSQL
    print("\n  [3/5] Loading jobs into PostgreSQL...")
    j_count = load_jobs_to_db(jobs)
    print(f"  ✅ {j_count} jobs loaded")

    # Step 4: Load questions to PostgreSQL
    print("\n  [4/5] Loading interview questions into PostgreSQL...")
    q_count = load_questions_to_db(qs)
    print(f"  ✅ {q_count} questions loaded")

    # Step 5: Load skills taxonomy
    print("\n  [5/5] Loading skills taxonomy into PostgreSQL...")
    from config import ROLE_SKILLS
    load_skills_taxonomy(ROLE_SKILLS)
    print("  ✅ Skills taxonomy loaded")

    # Show final stats
    stats = get_db_stats()
    print("\n" + "-"*40)
    print("  📊 DATABASE RECORDS:")
    print("-"*40)
    for k, v in stats.items():
        if k != "status":
            print(f"    {k:20s}: {v}")
    print(f"    {'status':20s}: {stats.get('status', 'unknown')}")
    print("-"*40)
    print("  ✅ ETL PIPELINE COMPLETE")

def cmd_eval():
    """Run model evaluations (fast — uses template baseline for comparison)."""
    import time
    print("\n" + "="*60)
    print("  STEP: MODEL EVALUATION")
    print("="*60)
    from config import FINETUNE, PROCESSED, OPENROUTER_API_KEY
    from utils import load_json, save_json
    from models.model5_roadmap import BaselineRoadmap, NemotronNanoRoadmap, NemotronSuperRoadmap, RoadmapEvaluator

    test = load_json(FINETUNE / "roadmap_test.json")[:10]  # 10 samples = fast
    print(f"  Loaded {len(test)} test samples (using 10 for speed)")

    ev = RoadmapEvaluator()

    t0 = time.time()
    print(f"\n  Evaluating Variant 1: {BaselineRoadmap.NAME}...")
    r1 = ev.evaluate(BaselineRoadmap(), test, BaselineRoadmap.NAME, 10)
    print(f"    ROUGE-L: {r1.get('rougeL',0):.3f}, Structural: {r1.get('structural',0):.3f} ({time.time()-t0:.1f}s)")

    if OPENROUTER_API_KEY:
        t0 = time.time()
        print(f"\n  Evaluating Variant 2: {NemotronNanoRoadmap.NAME}...")
        r2 = ev.evaluate(NemotronNanoRoadmap(), test, NemotronNanoRoadmap.NAME, 5)  # 5 samples with API
        print(f"    ROUGE-L: {r2.get('rougeL',0):.3f}, Structural: {r2.get('structural',0):.3f} ({time.time()-t0:.1f}s)")

        t0 = time.time()
        print(f"\n  Evaluating Variant 3: {NemotronSuperRoadmap.NAME}...")
        r3 = ev.evaluate(NemotronSuperRoadmap(), test, NemotronSuperRoadmap.NAME, 5)
        print(f"    ROUGE-L: {r3.get('rougeL',0):.3f}, Structural: {r3.get('structural',0):.3f} ({time.time()-t0:.1f}s)")
    else:
        print("\n  ⚠️  OPENROUTER_API_KEY not set — skipping Nemotron API evaluation")
        print("     (Using mock results for Nemotron variants)")

    # Merge with mock report (so all 5 models have results)
    from evaluation import generate_mock_eval_report
    report = generate_mock_eval_report()
    report["models"]["M5: Roadmap (3 variants)"]["results"].update(ev.compare())
    save_json(report, PROCESSED / "evaluation_report_latest.json")
    print("\n  ✅ Evaluation saved → data/processed/evaluation_report_latest.json")

def cmd_db_init():
    """Initialize PostgreSQL database tables."""
    print("\n  Initializing database...")
    from database import init_db
    init_db()
    print("  ✅ Database tables created")

def cmd_db_stats():
    """Show database record counts."""
    from database import get_db_stats
    stats = get_db_stats()
    print(json.dumps(stats, indent=2))

def cmd_serve():
    print("\n" + "="*60)
    print("  LAUNCHING STREAMLIT APP")
    print("  Open: http://localhost:8501")
    print("="*60 + "\n")
    import subprocess
    subprocess.run([sys.executable, "-m", "streamlit", "run", "app.py", "--server.port", "8501"])

def cmd_finetune():
    """Run hands-on fine-tuning experiments on Nemotron Super."""
    from run_finetune_eval import run_full_experiment
    run_full_experiment()

def main():
    p = argparse.ArgumentParser(description="SkillBridge AI Pipeline")
    p.add_argument("--data", action="store_true", help="Generate 50K+ sample data")
    p.add_argument("--scrape", action="store_true", help="Scrape live data")
    p.add_argument("--etl", action="store_true", help="Run ETL to PostgreSQL")
    p.add_argument("--eval", action="store_true", help="Quick evaluation (template)")
    p.add_argument("--finetune", action="store_true", help="Full fine-tuning experiment")
    p.add_argument("--db-init", action="store_true", help="Init database")
    p.add_argument("--db-stats", action="store_true", help="Show DB stats")
    p.add_argument("--serve", action="store_true", help="Launch Streamlit")
    p.add_argument("--full", action="store_true", help="Data + ETL + Serve")
    a = p.parse_args()

    print("\n🎯 SkillBridge AI Pipeline")
    print("=" * 60)

    if a.full or not any(vars(a).values()):
        cmd_data()
        cmd_etl()
        cmd_serve()
    else:
        if a.data: cmd_data()
        if a.scrape: cmd_scrape()
        if a.db_init: cmd_db_init()
        if a.etl: cmd_etl()
        if a.eval: cmd_eval()
        if a.finetune: cmd_finetune()
        if a.db_stats: cmd_db_stats()
        if a.serve: cmd_serve()

if __name__ == "__main__": main()
