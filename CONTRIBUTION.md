# CONTRIBUTION GUIDE

## Team Members

| Name               | Student ERP ID | Email                |
|--------------------|:--------------:|----------------------|
| John Doe           | 22XX0001       | johndoe@email.com    |
| Jane Smith         | 22XX0002       | janesmith@email.com  |
| Alex Lee           | 22XX0003       | alexlee@email.com    |

*Update names, IDs, and contact info above.*

---

## Responsibility Table

| Task                                      | Contributor     | Details/Notes                                      |
|-------------------------------------------|-----------------|----------------------------------------------------|
| **API Design & Implementation**           | John Doe        | Designed FastAPI endpoints: `/predict`, `/health`  |
| **MLflow Integration**                    | Jane Smith      | Wrote `mlflow_tracking.py`, sample runs, model log |
| **Evidently Integration & Report**        | Jane Smith      | Built `drift_dashboard.py` & generated report      |
| **Prometheus Metrics**                    | Alex Lee        | Implemented `prometheus_metrics.py`                |
| **CI/CD Workflow (GitHub Actions)**       | Alex Lee        | Authored `.github/workflows/ci.yml`, canary step   |
| **Dockerization & Healthcheck**           | John Doe        | Created multi-stage `Dockerfile` and health script |
| **Testing (Pytest) and Test Cases**       | [name]          | Author/maintainer for test coverage                |
| **Compliance, Pre-commit, Pip-Audit**     | Alex Lee        | Setup `.pre-commit-config.yaml`, pip-audit         |
| **Documentation (README, contribution)**  | All             | Authored README sections & diagrams                |
| **Model Build/Training Pipeline (future)**| All             | Placeholder for Milestones 2/3                     |

---

## Branch Naming Convention

All new work is done on feature or fix branches before merging to `main` or the milestone branch (`ms1_hk`):

- **Features:** `feat/<short-description>`
  _e.g._, `feat/predict-endpoint`
- **Bugfixes:** `fix/<short-description>`
  _e.g._, `fix/mlflow-uri`
- **Infrastructure:** `infra/<short-description>`
  _e.g._, `infra/ci-pipeline`
- **Documentation:** `docs/<short-description>`
  _e.g._, `docs/readme-updates`

**Pull Requests:**
All PRs must be reviewed by at least one other team member and must pass `make check` and the full CI suite before merge.

---

## How to Contribute

1. Fork the repository or branch from `main` or `ms1_hk`.
2. Use the branch naming convention above.
3. Add your changes and update documentation/tests as needed.
4. Push and open a pull request; select reviewers from other team members.
5. Wait for CI/CD checks to pass and for peer review.
6. After approval, merge your branch. Delete it if done.

---

*For more details, see the [README.md](README.md) and code comments throughout the source tree.*
