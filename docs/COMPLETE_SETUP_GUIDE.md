# HEARTSIGHT Complete Setup & Run Guide

## ✅ Verification Checklist

### Phase 1: Data & The "Classic" Model - COMPLETE ✅

- [x] **Training Script** (`src/pipeline/train.py`)
  - ✅ Loads PTB-XL data (train_signal.csv, train_meta.csv)
  - ✅ Extracts features from 12-lead ECG signals (shape: 1000, 12)
  - ✅ Targets: 5 Super-Classes (NORM, MI, STTC, CD, HYP)
  - ✅ Uses XGBoost classifier
  - ✅ MLflow Integration:
    - ✅ Logs parameters (epochs, batch_size)
    - ✅ Logs metrics (accuracy, F1-score)
    - ✅ Registers model artifact to MLflow Model Registry
    - ✅ Model name: `heartsight_xgb_v1`

- [x] **Model Loader** (`src/utils/model_loader.py`)
  - ✅ Loads model from MLflow registry
  - ✅ Extracts features from incoming signals
  - ✅ Returns predictions with confidence scores

### Phase 2: The RAG Engine - COMPLETE ✅

- [x] **PDF Documents** (`data/docs/`)
  - ✅ 5 PDFs for the 5 diagnostic classes
  - ✅ Conduction_Disturbance_Guide.pdf
  - ✅ General_ECG_Guide.pdf
  - ✅ Hypertrophy_Management.pdf
  - ✅ MI_Recovery_Guide.pdf
  - ✅ STTC_Ischemia_Guide.pdf

- [x] **Ingestion Pipeline** (`src/ingest.py`)
  - ✅ PDF loading using PyPDFLoader
  - ✅ Text splitting (chunk size: 500, overlap: 50)
  - ✅ Embedding using sentence-transformers/all-MiniLM-L6-v2 (local)
  - ✅ Vector DB: ChromaDB (saved to `data/vector_db/`)
  - ✅ Command: `python manage.py ingest`

- [x] **RAG Engine** (`src/rag_engine.py`)
  - ✅ Loads vector DB
  - ✅ Initializes LLM: `mistralai/Mistral-7B-Instruct-v0.2` (HuggingFace API)
  - ✅ Retrieves context based on diagnosis + age + sex
  - ✅ Generates patient-friendly explanations

- [x] **API Integration** (`src/api/routers/predict.py`)
  - ✅ `/predict` endpoint accepts:
    - `signal`: 2D array (time_steps, 12)
    - `age`: Optional patient age
    - `sex`: Optional patient sex
  - ✅ Flow: Predict Class → Retrieve Guidelines → Generate Explanation
  - ✅ Returns: prediction, confidence, probabilities, explanation

- [x] **System Architecture Diagram**
  - ✅ Created: `docs/diagrams/rag_architecture.md`

### Phase 5: The Website - COMPLETE ✅

- [x] **React Frontend** (`ui/`)
  - ✅ Drag-and-drop CSV upload
  - ✅ ECG visualization (Lead I & Lead II) using Recharts
  - ✅ Prediction display with confidence bars
  - ✅ Chat widget for follow-up questions
  - ✅ Modern, user-friendly UI

- [x] **Chat Endpoint** (`src/api/routers/chat.py`)
  - ✅ `/chat` endpoint for interactive questions
  - ✅ RAG-powered responses

## 📋 CSV Format Verification

Your `sample_upload_TEST_PATIENT.csv` is **COMPATIBLE** ✅

**Format:**
- Columns: `ecg_id, channel-0, channel-1, ..., channel-11`
- 1000 rows of signal data
- 12 channels (channel-0 through channel-11)

**Frontend Processing:**
1. Frontend reads CSV with PapaParse
2. Filters out `ecg_id` column
3. Extracts 12 channel columns
4. Converts to 2D array: `(1000, 12)`
5. Sends to `/predict` endpoint

**Model Processing:**
1. API receives `(1000, 12)` signal array
2. Extracts statistical features (108 features total)
3. XGBoost predicts class (NORM, MI, STTC, CD, HYP)
4. RAG engine generates explanation
5. Returns results to frontend

## 🚀 How to Run Everything

### Step 1: Verify Prerequisites

```bash
# Check Python version (3.8+)
python --version

# Check Node.js version (18+)
node --version

# Check if virtual environment is activated
# (You should see (venv) or (activate) in your prompt)
```

### Step 2: Install Backend Dependencies

```bash
# Make sure you're in the project root
cd C:\Users\VICTUS\Documents\AAA - IBA POST SPRING 2025\Fall 2025\MLOPS\Project\mlops-phase1

# Install Python dependencies
pip install -r requirements.txt
```

### Step 3: Train the Model (If Not Already Done)

```bash
# Train the XGBoost model and register to MLflow
python manage.py train
```

**Expected Output:**
- Model training progress
- MLflow metrics logged
- Model registered as `heartsight_xgb_v1`
- Model saved to `mlruns/models/heartsight_xgb_v1/`

### Step 4: Ingest PDFs for RAG (If Not Already Done)

```bash
# Ingest PDFs and create vector database
python manage.py ingest
```

**Expected Output:**
- PDFs loaded from `data/docs/`
- Text split into chunks
- Embeddings created
- Vector DB saved to `data/vector_db/`
- Test query verification

### Step 5: Verify Environment Variables

```bash
# Check .env file exists and has API token
Get-Content .env
```

**Should contain:**
```
HUGGINGFACEHUB_API_TOKEN=hf_aFfveOzvkQXgchKnYEDUNjboLauwKTd
```

### Step 6: Start the Backend API

**Open Terminal 1:**

```bash
# Start FastAPI server
python manage.py dev
```

**Expected Output:**
```
INFO:     Uvicorn running on http://127.0.0.1:8000
INFO:     Application startup complete.
✅ Model loaded successfully. Classes: ['NORM', 'MI', 'STTC', 'CD', 'HYP']
```

**Keep this terminal open!**

### Step 7: Start the Frontend

**Open Terminal 2 (New Window):**

```bash
# Navigate to project root (if not already there)
cd C:\Users\VICTUS\Documents\AAA - IBA POST SPRING 2025\Fall 2025\MLOPS\Project\mlops-phase1

# Start React frontend
python manage.py ui
```

**OR manually:**

```bash
cd ui
npm run dev
```

**Expected Output:**
```
  VITE v5.0.8  ready in XXX ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

**Keep this terminal open!**

### Step 8: Open the Website

1. Open your browser
2. Navigate to: **http://localhost:3000**
3. You should see the HEARTSIGHT upload interface

### Step 9: Test with Sample CSV

1. **Drag and drop** `sample_upload_TEST_PATIENT.csv` onto the upload area
   - OR click the upload area and browse for the file
2. **Optionally enter:**
   - Patient Age: e.g., `45`
   - Patient Sex: Select `Male` or `Female`
3. **Wait for processing** (you'll see a loading indicator)
4. **View Results:**
   - ECG Visualization (Lead I and Lead II charts)
   - AI Prediction (diagnosis badge, confidence bar)
   - Class Probabilities breakdown
   - AI Explanation (RAG-generated)
5. **Test Chat Widget:**
   - Scroll to the chat section
   - Ask questions like:
     - "What lifestyle changes should I make?"
     - "What does this condition mean?"
     - "What should I do next?"

## 🔍 Troubleshooting

### Backend Won't Start

**Error: Model not found**
```bash
# Train the model first
python manage.py train
```

**Error: Vector DB not found**
```bash
# Ingest PDFs first
python manage.py ingest
```

**Error: HUGGINGFACEHUB_API_TOKEN not found**
```bash
# Check .env file exists and has the token
Get-Content .env
```

### Frontend Won't Start

**Error: npm not found**
```bash
# Install Node.js from nodejs.org
```

**Error: Dependencies not installed**
```bash
cd ui
npm install
```

### CSV Upload Fails

**Error: "CSV file is empty"**
- Check the CSV file has data
- Ensure file is not corrupted

**Error: "Signal must have 12 channels"**
- Verify CSV has columns: `channel-0` through `channel-11`
- Check CSV format matches expected structure

### API Connection Errors

**Error: "Network Error" or "CORS Error"**
- Ensure backend is running on port 8000
- Check CORS is configured (already done in `src/api/main.py`)

**Error: "Failed to process ECG data"**
- Check backend terminal for error messages
- Verify model is loaded successfully
- Check RAG engine is initialized

## 📊 Expected Workflow

1. **User uploads CSV** → Frontend parses CSV
2. **Frontend sends to API** → `/predict` endpoint
3. **API processes signal** → Feature extraction
4. **XGBoost predicts** → Class (NORM, MI, STTC, CD, HYP)
5. **RAG engine retrieves** → Relevant medical context
6. **LLM generates explanation** → Patient-friendly text
7. **Results displayed** → Charts, prediction, explanation
8. **User asks questions** → Chat widget uses RAG

## ✅ Success Indicators

- ✅ Backend running on http://localhost:8000
- ✅ Frontend running on http://localhost:3000
- ✅ CSV upload works without errors
- ✅ ECG visualization displays correctly
- ✅ Prediction shows with confidence score
- ✅ AI explanation appears
- ✅ Chat widget responds to questions

## 🎉 You're Ready!

Everything is set up and ready to test. Follow the steps above to run the complete system and interact with the website!
