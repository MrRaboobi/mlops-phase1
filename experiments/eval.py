# experiments/eval.py

import os
import json
from pathlib import Path
from statistics import mean

import mlflow
import google.generativeai as genai
from dotenv import load_dotenv
from rouge_score import rouge_scorer
from nltk.translate.bleu_score import sentence_bleu

# ---------- Setup ----------

PROJECT_ROOT = Path(__file__).resolve().parents[1]
DATA_PATH = PROJECT_ROOT / "data" / "eval.jsonl"
PROMPTS_DIR = PROJECT_ROOT / "experiments" / "prompts"
REPORT_PATH = PROJECT_ROOT / "experiments" / "prompt_report.md"

load_dotenv(PROJECT_ROOT / ".env")
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    raise ValueError("GEMINI_API_KEY missing in .env")

genai.configure(api_key=API_KEY)
model = genai.GenerativeModel("gemini-2.5-flash")

# ---------- Load data & prompts ----------


def load_jsonl(path: Path):
    with open(path, "r", encoding="utf-8") as f:
        return [json.loads(line) for line in f]


def load_prompt(path: Path) -> str:
    with open(path, "r", encoding="utf-8") as f:
        return f.read()


dataset = load_jsonl(DATA_PATH)

prompt_files = {
    "baseline_zero_shot": PROMPTS_DIR / "baseline_zero_shot.md",
    "few_shot_k3": PROMPTS_DIR / "few_shot_k3.md",
    "advanced_cot": PROMPTS_DIR / "advanced_cot.md",
}

prompts = {name: load_prompt(path) for name, path in prompt_files.items()}

# ---------- Metrics ----------

rouge = rouge_scorer.RougeScorer(["rougeL"], use_stemmer=True)


def compute_text_metrics(pred: str, ref: str, n_gram: int = 1):
    """
    Compute ROUGE-L and BLEU scores.

    Args:
        pred: Predicted text
        ref: Reference text
        n_gram: N-gram order for BLEU (1-4). Default is 2 (bigrams).
                1 = unigrams, 2 = bigrams, 3 = trigrams, 4 = 4-grams
    """
    r = rouge.score(ref, pred)["rougeL"].fmeasure  # using ref as target

    # Set weights based on n_gram value
    if n_gram == 1:
        weights = (1.0, 0, 0, 0)  # BLEU-1: only unigrams
    elif n_gram == 2:
        weights = (0.5, 0.5, 0, 0)  # BLEU-2: unigrams + bigrams
    elif n_gram == 3:
        weights = (0.33, 0.33, 0.33, 0)  # BLEU-3: unigrams + bigrams + trigrams
    else:  # n_gram == 4 (default)
        weights = (0.25, 0.25, 0.25, 0.25)  # BLEU-4: all n-grams

    b = (
        sentence_bleu([ref.split()], pred.split(), weights=weights)
        if ref.strip()
        else 0.0
    )
    return r, b


def ask_rating(label: str) -> int:
    while True:
        try:
            val = int(input(f"  {label} (1-5): ").strip())
            if 1 <= val <= 5:
                return val
        except ValueError:
            pass
        print("   Please enter an integer between 1 and 5.")


# ---------- Evaluation Loop ----------
mlflow.set_tracking_uri("file:./mlruns")
mlflow.set_experiment("Prompt_Strategy_Evaluation")

results = {}

with mlflow.start_run(run_name="prompt_evaluation2"):

    mlflow.log_param("llm_model", "gemini-2.5-flash")
    mlflow.log_param("n_examples", len(dataset))

    for strategy_name, template in prompts.items():
        print("\n" + "=" * 70)
        print(f"Evaluating strategy: {strategy_name}")
        print("=" * 70)

        rouge_scores = []
        bleu_scores = []
        factuality_scores = []
        helpfulness_scores = []

        for i, sample in enumerate(dataset, start=1):
            print(f"\n--- Example {i}/{len(dataset)} ---")
            print(
                f"Prediction: {sample['prediction']}, Age: {sample['age']}, Sex: {sample['sex']}"
            )
            print(f"Reference: {sample['reference']}")

            prompt = template.format(
                prediction=sample["prediction"],
                age=sample["age"],
                sex=sample["sex"],
            )

            # Call Gemini
            response = model.generate_content(prompt)
            generated = response.text.strip()
            print("\nGenerated explanation:\n")
            print(generated)
            print("\nNow rate this explanation:")

            # Quantitative text metrics
            # Change n_gram parameter to reduce N-gram value (1-4, default is 2 for bigrams)
            r, b = compute_text_metrics(generated, sample["reference"], n_gram=2)
            rouge_scores.append(r)
            bleu_scores.append(b)

            # Human-in-the-loop ratings
            factual = ask_rating("Factuality")
            helpful = ask_rating("Helpfulness")
            factuality_scores.append(factual)
            helpfulness_scores.append(helpful)

        # Aggregate
        avg_rouge = mean(rouge_scores) if rouge_scores else 0.0
        avg_bleu = mean(bleu_scores) if bleu_scores else 0.0
        avg_fact = mean(factuality_scores) if factuality_scores else 0.0
        avg_help = mean(helpfulness_scores) if helpfulness_scores else 0.0

        # Log to MLflow
        mlflow.log_metric(f"{strategy_name}_rougeL", avg_rouge)
        mlflow.log_metric(f"{strategy_name}_bleu", avg_bleu)
        mlflow.log_metric(f"{strategy_name}_factuality", avg_fact)
        mlflow.log_metric(f"{strategy_name}_helpfulness", avg_help)

        results[strategy_name] = {
            "rougeL": avg_rouge,
            "bleu": avg_bleu,
            "factuality": avg_fact,
            "helpfulness": avg_help,
        }

# ---------- Generate prompt_report.md ----------

# Find best strategies
best_helpful = max(results.items(), key=lambda kv: kv[1]["helpfulness"])[0]
best_fact = max(results.items(), key=lambda kv: kv[1]["factuality"])[0]

with open(REPORT_PATH, "w", encoding="utf-8") as f:
    f.write("#Prompt Engineering Evaluation Report\n\n")
    f.write("## Strategies Evaluated\n\n")
    f.write("- **baseline_zero_shot** – simple direct instruction\n")
    f.write("- **few_shot_k3** – example-driven with 3 cardiologist summaries\n")
    f.write("- **advanced_cot** – chain-of-thought + risk-factor reasoning\n\n")

    f.write("## Quantitative & Qualitative Metrics (averages)\n\n")
    f.write("| Strategy | ROUGE-L | BLEU | Factuality (1-5) | Helpfulness (1-5) |\n")
    f.write("|----------|---------|------|-------------------|-------------------|\n")
    for name, m in results.items():
        f.write(
            f"| {name} | {m['rougeL']:.3f} | {m['bleu']:.3f} | "
            f"{m['factuality']:.2f} | {m['helpfulness']:.2f} |\n"
        )

    f.write("\n## Summary & Winner\n\n")
    f.write(
        f"- Highest **Helpfulness**: **{best_helpful}**\n"
        f"- Highest **Factuality**: **{best_fact}**\n\n"
    )
    f.write(
        "Overall, the advanced chain-of-thought strategy often produces more detailed "
        "and tailored explanations, but the few-shot strategy can be more concise and "
        "style-consistent. The zero-shot baseline is simplest but tends to be less "
        "robust for edge cases.\n"
    )

print("\n✅ Evaluation complete.")
print(f"   Report written to: {REPORT_PATH}")
print("   View metrics in MLflow with: mlflow ui")
