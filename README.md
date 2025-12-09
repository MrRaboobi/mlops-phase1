<h1 align="center">HEARTSIGHT</h1>

<p align="center">
  <img src="docs/mlops_app_logo.png" alt="Heartsight Logo" width="300"/>
</p>

<p align="center">
  HEARTSIGHT is an AI-powered ECG monitoring and early warning system. This README tracks the full milestone scope: classic ECG model, RAG pipeline, prompt evaluation, guardrails/monitoring, CI/CD + cloud, and the web UI.
</p>

---

## Table of Contents

1. [Project Overview](#project-overview)  
2. [Business Problem](#business-problem)  
3. [Architecture](#architecture)  
4. [Quick Start](#quick-start)  
5. [Data Setup](#data-setup)  
6. [Makefile Targets](#makefile-targets)  
7. [Phases & Deliverables](#phases--deliverables)  
8. [Model Training (Phase 1)](#model-training-phase-1)  
9. [RAG Engine (Phase 2)](#rag-engine-phase-2)  
10. [Prompt Engineering & Eval (Phase 3)](#prompt-engineering--eval-phase-3)  
11. [Guardrails & Monitoring (Phase 4)](#guardrails--monitoring-phase-4)  
12. [CI/CD, Security & Cloud (Phase 5)](#cicd-security--cloud-phase-5)  
13. [Website & Final Docs (Phase 6)](#website--final-docs-phase-6)  
14. [API Usage](#api-usage)  
15. [Environment Variables](#environment-variables)  
16. [Testing](#testing)  
17. [FAQ](#faq)  
18. [Compatibility](#compatibility)  
19. [License & Compliance](#license--compliance)  

---

## Project Overview

We provide: (a) a classic ECG classifier trained on PTB-XL; (b) a RAG-backed explanation layer that cites cardiology guidelines; (c) prompt experimentation and evaluation; (d) guardrails plus monitoring; (e) CI/CD and cloud hooks; (f) a React-based UI for uploads, visualization, and chat follow-ups.

## Business Problem

Input: user uploads ECG CSV (Holter/Apple Watch).  
Traditional ML: predict one of PTB-XL super-classes (NORM, MI, STTC, CD, HYP).  
Explanation (LLM+RAG): generate a human-readable report grounded in trusted guidelines.  
Interactive triage: chat follow-ups (e.g., “Can I still drink coffee?”) with safety guardrails preventing harmful advice.  
Admin view: drift and cost/latency monitoring for clinical readiness.

## Architecture

Data ingestion → feature extraction → classic model → API → RAG retrieval → LLM generation → guardrails → monitoring → UI. See `docs/architecture_diagram.png` and additional RAG/data-flow diagrams (Phase 2).

---

## Quick Start

```bash
git clone https://github.com/MrRaboobi/mlops-phase1.git
cd mlops-phase1
python -m venv venv
source venv/bin/activate           # Windows: .\venv\Scripts\activate
pip install -r requirements.txt
make dev                           # Windows: python manage.py dev
```
API: http://localhost:8000 (Swagger at /docs, ReDoc at /redoc).

---

## Data Setup

- Download PTB-XL Reformatted `train_signal.csv` and `train_meta.csv`.
- Place in `data/raw/`.
- Place five cardiology PDFs in `data/docs/` (for RAG): AHA MI guidelines, hypertrophy management, etc.
- Evaluation set for prompts: `data/eval.jsonl` (held-out).

---

## Makefile Targets

| Target        | Description                                            |
| :------------ | :----------------------------------------------------- |
| `make dev`    | Run FastAPI app (uvicorn, reload)                      |
| `make test`   | Run Pytest                                             |
| `make lint`   | Ruff + Black check                                     |
| `make format` | Black format                                           |
| `make docker` | Build Docker image `ecg-app`                           |
| `make run`    | Run Docker image on port 8000                          |
| `make clean`  | Remove caches                                          |
| `make check`  | Run pre-commit across repo                             |
| `make audit`  | Dependency audit via `scripts/dependency_audit.sh`     |
| `make train`  | Train classic model (`src/pipeline/train.py`)          |
| `make ingest` | Build RAG vector store (`src/ingest.py`)               |
| `make rag`    | Alias for ingest                                       |
| `make evidently` | Launch drift dashboard server (port 7000)           |
| `make ui`     | Run frontend dev server (`ui/`)                        |
| `make ui-build` | Build frontend assets                                |

---

## Phases & Deliverables

**Phase 1: Data & Classic Model (Foundational)**  
- Data: PTB-XL reformatted (`train_signal.csv`, `train_meta.csv` → `data/raw/`).  
- Training script: `src/pipeline/train.py` handles 12-lead signals (1000,12) targeting NORM, MI, STTC, CD, HYP.  
- MLflow: log params (epochs, batch_size, tree params), metrics (accuracy, F1), artifact `model.h5` (for API + D5 canary).  

**Phase 2: RAG Engine (D2 + Bonus)**  
- Docs: 5+ PDFs in `data/docs/`.  
- Ingestion: `src/ingest.py` (LangChain/LlamaIndex retrievers) → split, embed, store (Chroma/FAISS).  
- Diagrams: system architecture + data-flow (RAG) in `docs/`.  
- Make target: `make rag` for reproducible pipeline.  
- API (`src/app.py`): accepts `ecg_file` + `patient_metadata` (Age, Sex), predicts class, retrieves guidelines, generates explanation with LLM + retrieved context.

**Phase 3: Prompt Engineering & Eval (D1 + Bonus)**  
- Folder: `experiments/prompts/` with strategies:  
  - `baseline_zero_shot.md` (zero-shot).  
  - `few_shot_k3.md` (k=3 vs k=5 cardiologist summaries).  
  - `advanced_cot.md` (chain-of-thought/meta prompting using Age/Sex + prediction).  
- Eval script: `experiments/eval.py` runs strategies on `data/eval.jsonl`.  
- Metrics: ROUGE, BLEU, embedding cosine; qualitative 1–5 rubric (Factuality, Helpfulness) logged to MLflow/W&B.  
- Bonus: A/B testing dashboard comparing prompt variants.  
- Report: `prompt_report.md` summarizing strategy structure and results.

**Phase 4: Guardrails & Monitoring (D3 & D4)**  
- Guardrails: `src/guardrails.py` (Guardrails AI/NeMo/custom).  
  - Input validation: PII detection, prompt-injection filters.  
  - Output moderation: block dosage advice (e.g., replace “Take 500mg aspirin” with “Consult a cardiologist”).  
  - Log guardrail events to monitoring.  
- Monitoring stack: Prometheus for LLM metrics (latency, tokens, cost, violations); Grafana dashboards with screenshots in `docs/`.  
- Drift: `src/monitoring/drift.py` (Evidently) for retrieval corpus + ECG signal drift; serve at port 7000; capture screenshots.

**Phase 5: CI/CD, Security & Cloud (D5, D7, D8 + Bonus)**  
- GitHub Actions: lint/test for prompt scripts, automated prompt eval (small set), Docker build/push for RAG API, canary deployment for LLM service, ≥80% coverage target.  
- Security: `SECURITY.md`, prompt-injection defenses, privacy stance; `pip-audit` fails CI on critical CVEs.  
- Cloud: use at least two services (e.g., AWS S3 for docs/index, EC2 for serving; or GCP/Azure equivalents).  
- Bonus: optional managed LLM deploy (Vertex AI / Azure AI Studio).

**Phase 6: Website & Final Documentation (D6)**  
- Frontend scaffold: `npm create vite@latest ui -- --template react`.  
- Features: drag-drop upload of PTB-XL CSV; Recharts plot of Lead I/II from JSON response; chat widget for follow-ups to RAG.  
- Auth: JWT login requirement (D8).  
- Dashboards: history of scans; admin drift alerts surfaced from Evidently.  
- Docs: README updated with LLMOps objectives, diagrams, dashboard links, RAG deployment steps, API examples; `EVALUATION.md` for methodology and insights.  
- Tag release: `v2.0-milestone2` with passing CI.

---

## Model Training (Phase 1)

File: `src/pipeline/train.py`  
- Input: `data/raw/train_signal.csv` (shape ~1000 x 12 per ECG) + `data/raw/train_meta.csv`.  
- Labels: NORM, MI, STTC, CD, HYP (LabelEncoder).  
- Feature extraction: statistical features per lead.  
- Split: stratified train/test.  
- Model: XGBoost multi-class; log params/metrics to MLflow; save `model.h5` + `class_names.txt` for API loading.  
Run:
```bash
make train
# or
python src/pipeline/train.py
```

---

## RAG Engine (Phase 2)

File: `src/ingest.py`  
- Load PDFs from `data/docs/`, split, embed, store in Chroma/FAISS.  
- Custom retrievers (LangChain/LlamaIndex) for cardiology-specific queries.  
- `make rag` (alias `make ingest`) builds/refreshes the vector DB.  
- API flow: predict class → retrieve guideline chunks → generate explanation conditioned on prediction + patient metadata.

---

## Prompt Engineering & Eval (Phase 3)

- Prompts in `experiments/prompts/`: `baseline_zero_shot.md`, `few_shot_k3.md`, `advanced_cot.md`.  
- Eval runner: `experiments/eval.py` over `data/eval.jsonl`; logs quantitative (ROUGE/BLEU/embeddings) + qualitative (1–5 rubric) to MLflow/W&B.  
- Bonus: A/B dashboard for prompt variants.  
- Summary: `prompt_report.md`.

---

## Guardrails & Monitoring (Phase 4)

- Guardrails module: `src/guardrails.py` for input filtering (PII, injections) and output moderation (dosage/medical advice).  
- Monitoring: Prometheus metrics (latency, tokens, cost, guardrail_violations); Grafana dashboards (store screenshots in `docs/`).  
- Drift: `src/monitoring/drift.py` + `make evidently` to serve dashboard on port 7000 (ECG + retrieval corpus drift).  

---

## CI/CD, Security & Cloud (Phase 5)

- Workflow: `.github/workflows/ci.yml` extended for lint, tests, prompt eval, Docker build/push, canary deploy.  
- Coverage goal: ≥80% unit/integration.  
- Security: `SECURITY.md`, `pip-audit` in CI, dependency/license checks.  
- Cloud: S3 (docs/index), EC2 (API), or equivalents on GCP/Azure; optional managed LLM deployment bonus.

---

## Website & Final Docs (Phase 6)

- Frontend: Vite/React (`ui/`), drag-drop upload for ECG CSV, Recharts plotting of Lead I/II, chat widget for RAG Q&A, JWT login, scan history dashboard, admin drift alert banner.  
- Docs: README + diagrams; `EVALUATION.md` for prompt eval; deployment guide for hospital IT admins; release tag `v2.0-milestone2`.

---

## API Usage

- Base: `src/api/main.py` (FastAPI).  
- Endpoints: `/`, `/predict`, `/health`; RAG-enhanced prediction accepts file + patient metadata.  
- Docs: `/docs` (Swagger), `/redoc`.
Run locally:
```bash
make dev          # or python manage.py dev on Windows
```

---

## Environment Variables

| Variable              | Description                            |
|-----------------------|----------------------------------------|
| `MLFLOW_TRACKING_URI` | MLflow tracking server                 |
| `SECRET_KEY`          | API/ auth secret                       |
| `APP_ENV`             | Environment (dev/test/prod)            |
| `DEBUG`               | Enable debug mode                      |

Add RAG/LLM provider keys and vector DB settings as needed (not committed).

---

## Testing

```bash
make test
make lint
make check      # pre-commit
```
Target ≥80% coverage (Phase 5).

---

## FAQ

| Issue                         | Solution                                      |
|-------------------------------|-----------------------------------------------|
| Pre-commit fails              | `pip install pre-commit && pre-commit install && pre-commit run --all-files` |
| Docker build fails            | Ensure Docker Desktop + WSL2 running          |
| Python mismatch               | Use Python 3.11 (see `requirements.txt`)      |
| `.sh` on Windows              | Use PowerShell equivalents in `scripts/`      |

---

## Compatibility

| Platform    | Status                               |
|-------------|--------------------------------------|
| Windows 10+ | Fully supported (PowerShell scripts) |
| macOS       | Tested with Python 3.11              |
| Linux       | Native bash script support           |

## License & Compliance

- MIT License (`LICENSE`).  
- Dependency/License scans: `pip-audit`, `pip-licenses`; results in `docs/compliance_report.txt`.  
- Security posture and prompt-injection guidance: `SECURITY.md` (Phase 5).  

---

## Notes

- Use `us-east-1` defaults for S3 when applicable.  
- Keep `boto3` listed in `requirements.txt` for containerized runs.  
- Store architecture, diagrams, and monitoring screenshots under `docs/`.  
