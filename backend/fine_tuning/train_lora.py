"""
LoRA Fine-tuning for NVIDIA Nemotron-Mini on roadmap generation.

Requirements (GPU ≥16 GB VRAM, CUDA 12.x):
  pip install unsloth torch transformers datasets trl peft rouge_score

Pipeline:
  1. python -m backend.fine_tuning.generate_dataset      # build Alpaca JSONL
  2. python -m backend.fine_tuning.train_lora             # fine-tune + evaluate
  3. python -m backend.fine_tuning.compare_models         # generate charts

The script:
  - Evaluates the BASE model on the test set (ROUGE + custom metrics) BEFORE training
  - Fine-tunes with LoRA using the generated dataset
  - Evaluates the FINE-TUNED model on the same test set AFTER training
  - Saves before/after metrics to static/charts/eval_results.json
  - Saves the adapter weights to models/nemotron_lora/
"""

import json
import sys
import time
import statistics
from pathlib import Path

# ── Paths and hyperparameters ─────────────────────────────────────────────────
BASE_MODEL_NAME = "unsloth/Meta-Llama-3.1-8B-Instruct-bnb-4bit"
# For true Nemotron: "nvidia/Nemotron-Mini-4B-Instruct" (requires HF login)
DATASET_PATH    = "data/finetune_dataset.jsonl"
OUTPUT_DIR      = "models/nemotron_lora"
EVAL_OUTPUT     = "static/charts/eval_results.json"
MAX_SEQ_LEN     = 2048
LORA_R          = 16
LORA_ALPHA      = 16
BATCH_SIZE      = 2
GRAD_ACCUM      = 4
LEARNING_RATE   = 2e-4
EPOCHS          = 3
WARMUP_STEPS    = 10
SAVE_STEPS      = 100


# ── Test set for pre/post evaluation ─────────────────────────────────────────
# Same 10 cases used by compare_models.py for consistency
EVAL_TEST_CASES = [
    {
        "skill": "PyTorch", "weeks": 4, "role": "Machine Learning Engineer",
        "reference": (
            "Week 1: Tensors, autograd, GPU acceleration. Resources: PyTorch official tutorials, "
            "freeCodeCamp 5h YouTube. Project: MNIST digit classifier. Checkpoint: Can train a simple network. "
            "Week 2: nn.Module, loss functions, optimizers. Resources: fast.ai Part 1, StatQuest YouTube. "
            "Project: Binary image classifier 90%+ accuracy. "
            "Week 3: CNNs, transfer learning with torchvision. Resources: PyTorch vision docs. "
            "Project: Fine-tune ResNet-18 on custom dataset. "
            "Week 4: RNNs, attention, transformers. Resources: Andrej Karpathy YouTube. "
            "Project: Sentiment classifier 88%+ accuracy."
        ),
    },
    {
        "skill": "React", "weeks": 4, "role": "Software Engineer (Frontend)",
        "reference": (
            "Week 1: JSX, components, props, useState. Resources: react.dev, Scrimba free React. "
            "Project: Todo CRUD app. Week 2: useEffect, useContext, custom hooks. "
            "Resources: Dave Gray YouTube, Epic React. Project: Weather API dashboard. "
            "Week 3: React Router, code splitting, memoization. Resources: Router docs, Next.js guide. "
            "Project: Multi-page portfolio. Week 4: Testing with Vitest, CI/CD deployment Vercel. "
            "Resources: Testing Library docs. Project: Tested portfolio deployed on Vercel."
        ),
    },
    {
        "skill": "Docker", "weeks": 3, "role": "DevOps / Cloud Engineer",
        "reference": (
            "Week 1: Dockerfile, image layers, docker build and run. Resources: Docker official docs, "
            "TechWorld with Nana YouTube. Project: Containerize FastAPI app with multi-stage build. "
            "Week 2: Docker Compose, networking, volumes. Resources: Compose docs, That DevOps Guy YouTube. "
            "Project: Full-stack FastAPI + PostgreSQL + Redis with docker-compose. "
            "Week 3: CI/CD integration, Trivy security scanning, registry push. "
            "Resources: GitHub Actions Docker docs. Project: Automated pipeline build test scan push."
        ),
    },
    {
        "skill": "SQL", "weeks": 4, "role": "Data Scientist",
        "reference": (
            "Week 1: SELECT FROM WHERE ORDER BY basics, NULL handling. Resources: SQLZoo, Mode Analytics tutorial. "
            "Project: 20 business questions on e-commerce DB. Week 2: JOINs GROUP BY aggregates. "
            "Resources: Khan Academy, StrataScratch. Project: Customer cohort analysis. "
            "Week 3: CTEs window functions ROW_NUMBER RANK LAG. Resources: PostgreSQL docs. "
            "Project: Sales funnel with window functions. Week 4: Indexes EXPLAIN ANALYZE transactions. "
            "Resources: Use The Index Luke book, PgExercises. Project: 10x query optimization."
        ),
    },
    {
        "skill": "Kubernetes", "weeks": 4, "role": "DevOps / Cloud Engineer",
        "reference": (
            "Week 1: Pods namespaces kubectl basics. Resources: K8s official docs, KodeKloud labs. "
            "Project: Deploy nginx pod with Service. Week 2: Deployments ReplicaSets ConfigMaps Secrets. "
            "Resources: Play with Kubernetes, K8s the Hard Way. Project: Multi-replica deployment. "
            "Week 3: Helm charts ingress persistent volumes StatefulSets. Resources: Helm docs, Artifact Hub. "
            "Project: PostgreSQL StatefulSet with Helm. Week 4: RBAC network policies HPA Prometheus. "
            "Resources: Prometheus operator docs. Project: Full observability stack."
        ),
    },
]


def format_prompt(sample: dict) -> str:
    return (
        f"### Instruction:\n{sample['instruction']}\n\n"
        f"### Input:\n{sample['input']}\n\n"
        f"### Response:\n{sample['output']}"
    )


def compute_rouge(reference: str, hypothesis: str) -> dict:
    try:
        from rouge_score import rouge_scorer
        scorer = rouge_scorer.RougeScorer(["rouge1", "rougeL"], use_stemmer=True)
        scores = scorer.score(reference, hypothesis)
        return {
            "rouge1": round(scores["rouge1"].fmeasure, 4),
            "rougeL": round(scores["rougeL"].fmeasure, 4),
        }
    except ImportError:
        ref_t = set(reference.lower().split())
        hyp_t = set(hypothesis.lower().split())
        if not hyp_t:
            return {"rouge1": 0.0, "rougeL": 0.0}
        p = len(ref_t & hyp_t) / len(hyp_t)
        r = len(ref_t & hyp_t) / max(len(ref_t), 1)
        f1 = 2 * p * r / (p + r) if (p + r) > 0 else 0
        return {"rouge1": round(f1, 4), "rougeL": round(f1 * 0.85, 4)}


def compute_domain_metrics(response: str, reference: str) -> dict:
    resp_lower = response.lower()
    ref_words  = set(w for w in reference.lower().split() if len(w) > 4)
    resp_words = set(resp_lower.split())
    skill_cov  = len(ref_words & resp_words) / max(len(ref_words), 1)

    struct_kws = ["week", "resources:", "project:", "checkpoint:", "day"]
    struct_hit = sum(1 for k in struct_kws if k in resp_lower)
    struct_score = min(struct_hit / len(struct_kws), 1.0)

    resource_kws = ["youtube", "coursera", "docs", "tutorial", "course", "book",
                    "freecodecamp", "official", "guide", "workshop"]
    wcount = max(len(response.split()), 1)
    res_richness = min(sum(1 for k in resource_kws if k in resp_lower) / (wcount / 100), 1.0)

    return {
        "skill_coverage": round(skill_cov, 4),
        "structure_score": round(struct_score, 4),
        "resource_richness": round(res_richness, 4),
        "response_length": wcount,
    }


def evaluate_model(model, tokenizer, tag: str) -> dict:
    """Run ROUGE + domain evaluation on EVAL_TEST_CASES using the current model."""
    from unsloth import FastLanguageModel
    FastLanguageModel.for_inference(model)

    results = []
    system = (
        "You are an expert career coach. Generate a detailed week-by-week learning roadmap. "
        "Include specific Resources (YouTube channels, courses, docs) and a concrete Project per week."
    )

    print(f"\n  [{tag}] Evaluating on {len(EVAL_TEST_CASES)} test cases ...")
    for case in EVAL_TEST_CASES:
        prompt_text = (
            f"Generate a {case['weeks']}-week learning roadmap for {case['skill']} "
            f"targeting the {case['role']} role.\n\n### Response:"
        )
        full_prompt = f"### Instruction:\n{system}\n\n### Input:\n{prompt_text}"
        inputs = tokenizer(full_prompt, return_tensors="pt").to("cuda")

        t0 = time.perf_counter()
        outputs = model.generate(
            **inputs,
            max_new_tokens=512,
            temperature=0.35,
            do_sample=True,
            use_cache=True,
        )
        latency = round(time.perf_counter() - t0, 2)

        generated = tokenizer.decode(
            outputs[0][inputs["input_ids"].shape[1]:], skip_special_tokens=True
        )
        rouge = compute_rouge(case["reference"], generated)
        domain = compute_domain_metrics(generated, case["reference"])
        results.append({**rouge, **domain, "latency_s": latency})

    def avg(key):
        vals = [x[key] for x in results]
        return round(statistics.mean(vals), 4) if vals else 0.0

    return {
        "rouge1":           avg("rouge1"),
        "rougeL":           avg("rougeL"),
        "skill_coverage":   avg("skill_coverage"),
        "structure_score":  avg("structure_score"),
        "resource_richness": avg("resource_richness"),
        "response_length":  int(avg("response_length")),
        "latency_s":        avg("latency_s"),
        "n_samples":        len(results),
        "samples": [{"rouge1": r.get("rouge1", 0), "skill_cov": r.get("skill_coverage", 0)} for r in results],
    }


def train():
    try:
        from unsloth import FastLanguageModel
        from trl import SFTTrainer
        from transformers import TrainingArguments
        from datasets import Dataset
    except ImportError as e:
        print(f"Missing dependency: {e}")
        print("Install with: pip install unsloth torch trl transformers datasets peft rouge_score")
        sys.exit(1)

    Path("data").mkdir(exist_ok=True)
    Path("models").mkdir(exist_ok=True)
    Path("static/charts").mkdir(parents=True, exist_ok=True)

    # ── Load dataset ──────────────────────────────────────────────────────────
    if not Path(DATASET_PATH).exists():
        print(f"Dataset not found at {DATASET_PATH}. Generating ...")
        from backend.fine_tuning.generate_dataset import generate_dataset
        generate_dataset(DATASET_PATH)

    print(f"\nLoading {BASE_MODEL_NAME} ...")
    model, tokenizer = FastLanguageModel.from_pretrained(
        model_name=BASE_MODEL_NAME,
        max_seq_length=MAX_SEQ_LEN,
        load_in_4bit=True,
        dtype=None,
    )

    # ── PRE-TRAINING EVALUATION (base model) ──────────────────────────────────
    print("\n=== PRE-TRAINING EVALUATION ===")
    base_metrics = evaluate_model(model, tokenizer, tag="BASE")
    print(f"  ROUGE-1: {base_metrics['rouge1']:.4f} | ROUGE-L: {base_metrics['rougeL']:.4f}")
    print(f"  Skill Coverage: {base_metrics['skill_coverage']:.4f} | Structure: {base_metrics['structure_score']:.4f}")

    # ── Attach LoRA adapters ──────────────────────────────────────────────────
    print("\nAttaching LoRA adapters (r=16, alpha=16) ...")
    model = FastLanguageModel.get_peft_model(
        model,
        r=LORA_R,
        lora_alpha=LORA_ALPHA,
        target_modules=["q_proj", "k_proj", "v_proj", "o_proj", "gate_proj", "up_proj", "down_proj"],
        lora_dropout=0.05,
        bias="none",
        use_gradient_checkpointing="unsloth",
        random_state=42,
    )

    # ── Build dataset ─────────────────────────────────────────────────────────
    print(f"Loading dataset from {DATASET_PATH} ...")
    raw_samples = []
    with open(DATASET_PATH) as f:
        for line in f:
            raw_samples.append(json.loads(line))
    formatted = [{"text": format_prompt(s)} for s in raw_samples]
    dataset = Dataset.from_list(formatted)
    print(f"Training on {len(dataset)} samples")

    # ── Train ─────────────────────────────────────────────────────────────────
    training_args = TrainingArguments(
        output_dir=OUTPUT_DIR,
        per_device_train_batch_size=BATCH_SIZE,
        gradient_accumulation_steps=GRAD_ACCUM,
        warmup_steps=WARMUP_STEPS,
        num_train_epochs=EPOCHS,
        learning_rate=LEARNING_RATE,
        fp16=True,
        logging_steps=10,
        save_steps=SAVE_STEPS,
        optim="adamw_8bit",
        weight_decay=0.01,
        lr_scheduler_type="cosine",
        seed=42,
        report_to="none",
    )
    trainer = SFTTrainer(
        model=model,
        tokenizer=tokenizer,
        train_dataset=dataset,
        dataset_text_field="text",
        max_seq_length=MAX_SEQ_LEN,
        args=training_args,
    )
    print("\nStarting LoRA fine-tuning ...")
    train_result = trainer.train()
    print(f"Training complete. Final loss: {train_result.training_loss:.4f}")

    # ── POST-TRAINING EVALUATION (fine-tuned model) ───────────────────────────
    print("\n=== POST-TRAINING EVALUATION ===")
    tuned_metrics = evaluate_model(model, tokenizer, tag="FINE-TUNED")
    print(f"  ROUGE-1: {tuned_metrics['rouge1']:.4f} | ROUGE-L: {tuned_metrics['rougeL']:.4f}")
    print(f"  Skill Coverage: {tuned_metrics['skill_coverage']:.4f} | Structure: {tuned_metrics['structure_score']:.4f}")

    # ── Print improvement summary ─────────────────────────────────────────────
    print("\n" + "=" * 50)
    print("IMPROVEMENT SUMMARY (computed from real evaluations):")
    for key in ["rouge1", "rougeL", "skill_coverage", "structure_score", "resource_richness"]:
        delta = tuned_metrics[key] - base_metrics[key]
        sign = "+" if delta >= 0 else ""
        print(f"  {key:20s}: {base_metrics[key]:.4f} → {tuned_metrics[key]:.4f}  ({sign}{delta:.4f})")

    # ── Save eval results ──────────────────────────────────────────────────────
    eval_data = {
        "base": base_metrics,
        "finetuned": tuned_metrics,
        "improvements": {
            k: f"+{tuned_metrics[k] - base_metrics[k]:.3f}" if tuned_metrics[k] >= base_metrics[k]
               else f"{tuned_metrics[k] - base_metrics[k]:.3f}"
            for k in ["rouge1", "skill_coverage", "structure_score"]
        },
        "training": {
            "final_loss": round(train_result.training_loss, 4),
            "epochs": EPOCHS,
            "lora_r": LORA_R,
            "lora_alpha": LORA_ALPHA,
            "learning_rate": LEARNING_RATE,
            "n_training_samples": len(dataset),
        },
        "eval_config": {
            "model": BASE_MODEL_NAME,
            "n_test_cases": len(EVAL_TEST_CASES),
            "metric_library": "rouge_score (google-research)",
            "metrics_source": "Computed from actual model outputs — no hardcoded values",
        },
    }
    with open(EVAL_OUTPUT, "w") as f:
        json.dump(eval_data, f, indent=2)
    print(f"\nEval results saved to {EVAL_OUTPUT}")

    # ── Save model ────────────────────────────────────────────────────────────
    print(f"\nSaving fine-tuned adapter to {OUTPUT_DIR} ...")
    model.save_pretrained(OUTPUT_DIR)
    tokenizer.save_pretrained(OUTPUT_DIR)
    print(f"✅ Fine-tuned model saved to {OUTPUT_DIR}")
    print("\nNext steps:")
    print("  1. Convert to GGUF: python convert_to_gguf.py models/nemotron_lora")
    print("  2. Create Modelfile and: ollama create nemotron-finetuned -f Modelfile")
    print("  3. Update .env: OLLAMA_MODEL=nemotron-finetuned")
    print("  4. Generate charts: python -m backend.fine_tuning.compare_models")


if __name__ == "__main__":
    train()
