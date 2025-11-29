# 🚀 HEARTSIGHT Quick Start Guide

## Fix Applied ✅

The `uvicorn` command issue has been fixed. The `manage.py` script now uses `python -m uvicorn` instead of just `uvicorn`.

## How to Run (Updated)

### Step 1: Start Backend API

**Open Terminal 1:**

```powershell
python manage.py dev
```

**Expected Output:**
```
============================================================
Running: FastAPI Development Server
Command: python -m uvicorn src.api.main:app --reload
============================================================

INFO:     Will watch for changes in these directories: ['C:\\Users\\VICTUS\\...']
INFO:     Uvicorn running on http://127.0.0.1:8000 (Press CTRL+C to quit)
INFO:     Started reloader process
INFO:     Started server process
INFO:     Waiting for application startup.
✅ Model loaded successfully. Classes: ['NORM', 'MI', 'STTC', 'CD', 'HYP']
INFO:     Application startup complete.
```

**✅ Keep this terminal open!**

### Step 2: Start Frontend

**Open Terminal 2 (New Window):**

```powershell
python manage.py ui
```

**OR manually:**

```powershell
cd ui
npm run dev
```

**Expected Output:**
```
  VITE v5.0.8  ready in XXX ms

  ➜  Local:   http://localhost:3000/
  ➜  Network: use --host to expose
```

**✅ Keep this terminal open!**

### Step 3: Open Website

1. Open your browser
2. Navigate to: **http://localhost:3000**
3. You should see the HEARTSIGHT upload interface

### Step 4: Test with Sample CSV

1. **Drag and drop** `sample_upload_TEST_PATIENT.csv` onto the upload area
2. **Optionally enter:**
   - Patient Age: e.g., `45`
   - Patient Sex: `Male` or `Female`
3. **Wait for processing** (loading indicator)
4. **View Results:**
   - ECG Visualization (Lead I and Lead II)
   - AI Prediction (diagnosis, confidence)
   - AI Explanation
5. **Test Chat Widget:**
   - Ask questions about your results

## Troubleshooting

### If Backend Still Won't Start

**Try this directly:**
```powershell
python -m uvicorn src.api.main:app --reload
```

**If that works, the issue is with manage.py. If not, check:**
```powershell
# Verify uvicorn is installed
python -m pip show uvicorn

# If not installed:
python -m pip install uvicorn fastapi
```

### If Frontend Won't Start

**Check Node.js:**
```powershell
node --version
npm --version
```

**Install dependencies:**
```powershell
cd ui
npm install
npm run dev
```

## Alternative: Run Directly (Without manage.py)

### Backend:
```powershell
python -m uvicorn src.api.main:app --reload --host 127.0.0.1 --port 8000
```

### Frontend:
```powershell
cd ui
npm run dev
```

## Success Indicators

- ✅ Backend: http://localhost:8000 shows API docs
- ✅ Frontend: http://localhost:3000 shows upload interface
- ✅ CSV upload works
- ✅ Results display correctly

## Need Help?

Run verification:
```powershell
python verify_setup.py
```

This will check if everything is set up correctly.
