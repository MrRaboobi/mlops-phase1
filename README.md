# Federated ECGGuard
**AI-Powered ECG Monitoring and Early Warning System**

---

## Elevator Pitch
Federated ECGGuard is an AI-powered system that continuously monitors ECG signals, detects early cardiac abnormalities, and provides clinician-friendly, guideline-based explanations using LLMs — all while preserving patient privacy through federated learning.

---

## 🏗️ Architecture
![Architecture Diagram](docs/architecture_diagram.png)

**Flow:**
ECG Data → Pre-processing → CNN/LSTM Model → FastAPI Inference → LLM Explanations → Monitoring (Dashboards)

---

## FAQ

### Q: Docker build fails on Windows?
A: Make sure Docker Desktop is running and WSL 2 backend is enabled.

### Q: Lint check errors like E501 line too long?
A: Run make format to auto-format code using Black.

### Q: MLflow URI not found?
A: For now it’s a placeholder; real tracking will be added in further milestones.

---

## 👥 Team

Muhammad Hammad Khan
Muhammad Maaz Siddiqui
Muhammad Ibrahim Iqbal
Muhammad Ibrahim Farid

## ⚡ Quick Start

```bash
# clone the repo
git clone https://github.com/MrRaboobi/mlops-phase1
cd mlops_ms1

# set up environment
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# run dev build
make dev
