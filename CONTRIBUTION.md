# CONTRIBUTION GUIDE

## Team Members

| Name/Role (placeholder) | Focus Area                                  |
|-------------------------|---------------------------------------------|
| Muhammad Ibrahim Farid 27098               | Project setup, ML model pipeline, frontend scaffold |
| Muhammad Hammad Khan 26917                | RAG engine, Ingestion utilities, Prompt Evaluation and Monitoring setup          |
| Muhammad Maaz Siddiqui 27070                | CI/CD, Docker, security/compliance          |
| Muhammad Ibrahim Iqbal 27085                | Testing, data ops support, documentation    |



## Responsibilities by Phase

| Scope / Phase | Owner | Notes |
| :--- | :--- | :--- |
| Repo bootstrap, env setup, app wiring | Muhammad Maaz Siddiqui | Created base FastAPI app, routing skeleton, config loading. |
| Model training pipeline | Muhammad Ibrahim Farid | Built `src/pipeline/train.py`, feature extraction, MLflow runs. |
| Frontend scaffold / API docs surfacing | Muhammad Ibrahim Farid | Exposed docs at `/docs` & `/redoc`, basic UI shell. |
| RAG ingestion and retrieval utilities | Muhammad Ibrahim Farid | Authored ingestion utilities and retrieval logic (chunking/embedding). |
| RAG Engine & Prompt Evaluation | Muhammad Hammad Khan | Implemented `src/rag_engine.py` logic and A/B testing of prompts in `experiments/`. |
| System Monitoring & Observability | Muhammad Hammad Khan | Integrated Prometheus metrics, Grafana dashboards, and Evidently AI drift detection. |
| API integration for retrieved context | Muhammad Hammad Khan | Wired context-aware responses into inference flow. |
| Dockerfile + health checks | Muhammad Hammad Khan | Multi-stage build, `scripts/healthcheck.sh`, image publishing. |
| Test plan & Pytest coverage | Muhammad Maaz Siddiqui | Authored/maintains unit/integration tests. |
| GitHub Actions CI | Muhammad Maaz Siddiqui | Lint/test/audit/build workflow in `.github/workflows/ci.yml`. |
| Security & compliance | Muhammad Maaz Siddiqui | `pip-audit`, licenses, `.pre-commit-config.yaml`. |
| Data processing support | Muhammad Ibrahim Iqbal | Validated chunked loaders, feature schemas, sample datasets. |
| Documentation (README, diagrams) | Muhammad Ibrahim Iqbal | Consolidated project docs and developer instructions. |


---

## Branch Naming Convention

All work lands via Pull Requests into `main` (or milestone branches such as `ms1_hk`).


  - Examples: `refactor/rag-engine`, `refactor/model-loader`

**Pull Request Requirements:**
- PR title should clearly describe the change.
- PR description should include:
  - What changed and why
  - Testing performed (unit tests, manual testing)
  - Any breaking changes
  - Related issue/deliverable number (if applicable)

---

## How to Contribute

### Prerequisites

- Python 3.11 (as specified in `requirements.txt`)
- Git configured with your name and email
- Access to the repository (fork or direct access)

### Development Workflow

1. **Sync with main branch:**
   ```bash
   git checkout main
   git pull origin main
   ```

2. **Create a feature branch:**
   ```bash
   git checkout -b feat/your-feature-name
   ```

3. **Set up development environment:**
   ```bash
   python -m venv venv
   source venv/bin/activate  # Windows: .\venv\Scripts\activate
   pip install -r requirements.txt
   ```

4. **Make your changes:**
   - Follow the project structure:
     - Backend API: `src/api/`
     - ML Pipeline: `src/pipeline/`
     - RAG Engine: `src/rag_engine.py`, `src/ingest.py`
     - Guardrails: `src/guardrails.py`
     - Monitoring: `src/monitoring/`
     - Frontend: `ui/`
     - Experiments: `experiments/`
   - Write clear, documented code with docstrings
   - Follow existing code style (Black formatting, Ruff linting)

5. **Run pre-commit checks locally:**
   ```bash
   make check          # Runs pre-commit hooks
   # or
   pre-commit run --all-files
   ```

6. **Run tests and ensure coverage:**
   ```bash
   make test           # Run pytest
   make lint           # Check code style (Ruff + Black)
   ```
   - Target: ≥80% test coverage (enforced in CI)
   - Add unit tests for new functions/classes
   - Add integration tests for API endpoints

7. **Update documentation:**
   - Update `README.md` if adding new features or changing setup
   - Add docstrings to new functions/classes
   - Update `SECURITY.md` if security-related changes
   - Update `EVALUATION.md` if prompt/experiment changes

8. **Commit your changes:**
   ```bash
   git add .
   git commit -m "feat: add new feature description"
   ```
   - Use conventional commit messages (feat, fix, docs, test, refactor)
   - Keep commits atomic (one logical change per commit)

9. **Push and create Pull Request:**
   ```bash
   git push origin feat/your-feature-name
   ```
   - Open PR on GitHub targeting `main` (or milestone branch)
   - Request review from at least one team member
   - Link related issues/deliverables in PR description

10. **Address review feedback:**
    - Make requested changes
    - Push updates to the same branch
    - Respond to comments

11. **Ensure CI passes:**
    The CI pipeline (`.github/workflows/ci.yml`) runs:
    - Pre-commit hooks (formatting, linting)
    - Ruff + Black linting
    - `pip-audit` security scan (fails on critical CVEs)
    - Pytest with coverage (≥80% required)
    - Docker build and push to GHCR
    - Canary deployment tests
    - All checks must pass before merge

12. **Merge and cleanup:**
    - Once approved and CI is green, merge the PR
    - Delete the feature branch after merge
    - Update local main branch: `git checkout main && git pull`

### Code Quality Standards

**Linting & Formatting:**
- **Ruff:** Fast Python linter (replaces flake8, isort)
- **Black:** Code formatter (line length: 88 chars)
- Run before committing: `make lint` or `make format`

**Testing Requirements:**
- **Coverage Target:** ≥80% (enforced in CI)
- **Test Structure:**
  - Unit tests: `tests/test_<module>.py`
  - Integration tests: `tests/test_api.py`, `tests/test_rag.py`
  - Use pytest fixtures for common setup
- **Run tests:** `make test` or `pytest --cov=src`

**Security Checks:**
- **pip-audit:** Automatically runs in CI, fails on critical CVEs
- **Pre-commit hooks:** Include security checks
- **Guardrails:** All user inputs/outputs must pass guardrail validation

**Documentation Standards:**
- **Docstrings:** Use Google-style docstrings for functions/classes
- **Type Hints:** Add type annotations where possible
- **README Updates:** Document new features, API changes, setup steps
- **SECURITY.md:** Update for security-related changes

### Project-Specific Guidelines

**ML Pipeline (`src/pipeline/train.py`):**
- Log all parameters and metrics to MLflow
- Register models with versioning: `heartsight_xgb_v1`
- Ensure reproducibility (seed random states, log data paths)

**RAG Engine (`src/rag_engine.py`, `src/ingest.py`):**
- Use LangChain for document processing
- Store vector DB in `data/vector_db/`
- Ensure `make rag` runs end-to-end pipeline
- Test retrieval quality with sample queries

**API Endpoints (`src/api/routers/`):**
- Use FastAPI with Pydantic models
- Apply guardrails to all user inputs (`apply_guardrails_to_input`)
- Apply guardrails to LLM outputs (`apply_guardrails_to_output`)
- Log metrics to Prometheus
- Return clear error messages

**Monitoring (`src/monitoring/`):**
- Expose Prometheus metrics on port 9000
- Use Evidently for drift detection
- Log guardrail events to metrics

**Frontend (`ui/`):**
- Use React + Vite
- Follow existing component structure
- Test with sample ECG CSV files
- Ensure CORS is configured for API calls

**Experiments (`experiments/`):**
- Store prompt templates in `experiments/prompts/`
- Run evaluation: `python experiments/eval.py`
- Generate reports: `experiments/prompt_report.md`
- Log metrics to MLflow

### Common Issues & Solutions

**Pre-commit hooks fail:**
```bash
pip install pre-commit
pre-commit install
pre-commit run --all-files
```

**Docker build fails:**
- Ensure Docker Desktop is running (Windows/Mac)
- Check WSL2 backend is enabled (Windows)
- Verify Dockerfile syntax

**CI fails on pip-audit:**
- Check `docs/compliance_report.txt` for CVE details
- Update vulnerable packages in `requirements.txt`
- Re-run CI after fixes

**Test coverage below 80%:**
- Add unit tests for uncovered functions
- Use `pytest --cov=src --cov-report=html` to see coverage report
- Focus on critical paths (API endpoints, guardrails, RAG engine)

---

## Additional Resources

- **Project README:** [README.md](README.md) - Full project documentation
- **Security Guide:** [SECURITY.md](SECURITY.md) - Security practices and guardrails
- **API Documentation:** Run `make dev` and visit `http://localhost:8000/docs`
- **MLflow UI:** Run `mlflow ui` and visit `http://localhost:5000`
- **Makefile Targets:** See `make help` or `README.md` for available commands

---

**Questions?** Contact your team lead or open a GitHub issue for discussion.
