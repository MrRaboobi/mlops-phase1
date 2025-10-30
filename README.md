<h1 align="center">HEARTSIGHT</h1>

<p align="center">
  <img src="docs/mlops_app_logo.png" alt="Heartsight Logo" width="300"/>
</p>

<p align="center">
  HEARTSIGHT is an AI-powered ECG monitoring and early warning system designed to support distributed healthcare data collection and predictive diagnostics.
  This README represents <strong>Milestone 1</strong> of the MLOps course project that builds the foundation for a reproducible, production-grade pipeline with CI/CD, monitoring, observability, and compliance features.
</p>


## Architecture Diagram

The following diagram illustrates the flow from **data ingestion → training → inference API**, along with supporting MLOps components (CI/CD, monitoring, and compliance).

![Architecture Diagram](docs/architecture_diagram.png)

---

## Quick Start Guide

### 1. Clone the Repository
git clone https://github.com/<your-username>/mlops-phase1.git
cd mlops-phase1
git checkout ms1_hk

### 2. Create and Activate Virtual Environment

To set up your Python virtual environment, execute the following commands in your terminal:
python -m venv venv
.\venv\Scripts\activate

### 3. Install Dependencies

Once your virtual environment is active, install all necessary project dependencies using `pip`:
pip install -r requirements.txt

### 4. Run the Application

To start the application in development mode, use the `make dev` command:

The API will be accessible at: [http://localhost:8000](http://localhost:8000)

### 5. Run Dockerized Version

For a Dockerized deployment, build and run the Docker container with these commands:
make docker
make run

The Docker container will serve the application at: [http://localhost:8000]

## Makefile Targets

| Target        | Description                                  |
| :------------ | :------------------------------------------- |
| `make dev`    | Run FastAPI app in development mode          |
| `make docker` | Build Docker image                           |
| `make run`    | Run containerized application                |
| `make lint`   | Run Ruff and Black linters                   |
| `make format` | Auto-format code using Black                 |
| `make test`   | Run Pytest with coverage                     |
| `make audit`  | Run dependency and license audit             |
| `make clean`  | pre-commit run --all-files                   |
| `make check`  | Run dependency and license audit             |

## Deliverables Summary

### D1 – Repository and Documentation
- Added `README.md` with architecture, quick start guide, and setup instructions.
- Defined folder structure for scalability and clarity.

### D2 – Collaboration & Contribution
- Added `CONTRIBUTION.md` to define roles and branching conventions.
- Configured `.gitignore` to exclude unwanted files.

### D3 – Dockerization
- Created `Dockerfile` for containerized deployment.
- Added `scripts/healthcheck.sh` for service validation.

### D4 – CI/CD Pipeline
- Implemented GitHub Actions workflow (`.github/workflows/ci.yml`).
- Automated linting, testing, and Docker image builds.

### D5 – Monitoring & Observability
- Integrated **MLflow**, **Evidently**, and **Prometheus**.
- Generated monitoring dashboards and sample reports under `/docs`.

### D6 – Code Quality & Pre-commit Hooks
- Configured `.pre-commit-config.yaml` for linting, formatting, and security scanning.
- Integrated pre-commit validation into GitHub Actions.

### D7 – API Documentation
- Added FastAPI routes (`/`, `/predict`, `/health`).
- Enabled auto-generated Swagger `/docs` and ReDoc `/redoc` UIs.

### D8 – Compliance and Security
- Introduced `.env` for configuration management.
- Implemented `pip-audit` and `pip-licenses` for dependency audits.
- Generated compliance report (`docs/compliance_report.txt`).

## Environment Variables

| Variable              | Description                      |
|-----------------------|----------------------------------|
| `MLFLOW_TRACKING_URI` | MLflow tracking server address   |
| `PROMETHEUS_PORT`     | Prometheus metrics port          |
| `SECRET_KEY`          | Mock secret key for API security |
| `APP_ENV`             | Application environment type     |
| `DEBUG`               | Enable or disable debug mode     |

---

## FAQ / Troubleshooting

| Issue                                 | Solution                                                     |
|---------------------------------------|--------------------------------------------------------------|
| **Pre-commit hook fails**             | Run `pip install pre-commit then pre-commit install then pre-commit run --all-files`   |
| **Docker build fails**                | Ensure Docker Desktop and WSL2 backend are running           |
| **Python version mismatch**           | Use Python 3.11 as specified in `requirements.txt`           |
| **Cannot run .sh scripts on Windows** | Use the `.ps1` PowerShell versions provided under `/scripts` |

---

## Compatibility

| Platform           | Status                                      |
|--------------------|---------------------------------------------|
| **Windows 10+**    |  Fully supported (PowerShell-based scripts) |
| **macOS**          |  Tested with Python 3.11                    |
| **Linux (Ubuntu)** | Native bash script support                  |

## License & Compliance

All dependencies were scanned using:

- `pip-audit` → vulnerability detection
- `pip-licenses` → open-source license validation

Audit results stored in `docs/compliance_report.txt`.

---

## Future Work

- Integrate real ECG model training pipeline.
- Deploy to a cloud-based infrastructure (Azure or GCP).
- Add Grafana dashboards for real-time drift monitoring.
- Enable continuous model retraining.
