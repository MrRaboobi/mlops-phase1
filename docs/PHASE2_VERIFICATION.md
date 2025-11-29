# Phase 2: RAG Engine - Verification Guide

This guide helps you verify that Phase 2 is complete and working correctly.

## ✅ Phase 2 Deliverables Checklist

### D2 - RAG Pipeline (Milestone 2 Requirement)

- [x] **Document Ingestion Script** (`src/ingest.py`)
  - Loads PDFs from `data/docs/`
  - Splits into chunks (500 chars, 50 overlap)
  - Embeds using local sentence-transformers
  - Stores in ChromaDB vector database

- [x] **RAG Engine** (`src/rag_engine.py`)
  - `ECGExplainer` class implemented
  - Loads vector store on initialization
  - Retrieves context based on diagnosis + patient metadata
  - Generates explanations using HuggingFace LLM

- [x] **API Integration** (`src/api/routers/predict.py`)
  - Enhanced `/predict` endpoint
  - Accepts `age` and `sex` parameters
  - Returns prediction + RAG-generated explanation

- [x] **System Architecture Diagram**
  - Created: `docs/diagrams/rag_architecture.md`
  - Shows: PDF → Split → Embed → Vector DB → Retrieval → LLM → Explanation

- [x] **Makefile Target**
  - Added `make rag` and `make ingest` targets
  - Added `python manage.py ingest` and `python manage.py rag` commands

## Step-by-Step Verification

### 1. Verify Document Ingestion

**Check that vector database exists:**
```powershell
dir data\vector_db
```

**Expected output:**
- Directory should exist with ChromaDB files
- Should contain embedded vectors from 5 PDFs

**Re-run ingestion (if needed):**
```powershell
python manage.py ingest
```

**Expected output:**
- ✓ Loaded 5 PDF files
- ✓ Split into ~400 chunks
- ✓ Vector store created

### 2. Verify RAG Engine Initialization

**Test RAG engine directly:**
```python
# Create test script: test_rag.py
from src.rag_engine import ECGExplainer

explainer = ECGExplainer()
result = explainer.generate_explanation(
    diagnosis="MI",
    age=65,
    sex="Male"
)
print(result["explanation"])
```

**Run:**
```powershell
python test_rag.py
```

**Expected:**
- RAG engine loads successfully
- Generates explanation text
- No errors

### 3. Test API with RAG Integration

**Start the API:**
```powershell
python manage.py dev
```

**Test prediction with RAG (PowerShell):**
```powershell
$body = @{
    signal = @(
        @(0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2),
        @(0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3)
    ) * 50  # 100 time steps
    age = 65
    sex = "Male"
} | ConvertTo-Json -Depth 10

Invoke-RestMethod -Uri "http://localhost:8000/predict" -Method POST -Body $body -ContentType "application/json"
```

**Expected response:**
```json
{
    "ecg_id": null,
    "signal_shape": [100, 12],
    "prediction": "NORM",
    "confidence": 0.85,
    "probabilities": {...},
    "class_index": 0,
    "explanation": "Your ECG shows Normal Sinus Rhythm...",
    "patient_metadata": {
        "age": 65,
        "sex": "Male"
    }
}
```

### 4. Verify Architecture Diagram

**Check diagram exists:**
```powershell
Get-Content docs\diagrams\rag_architecture.md
```

**Expected:**
- Mermaid diagram showing RAG flow
- Data flow sequence diagram
- Component details

### 5. Test Different Diagnoses

Test with different predictions to verify RAG retrieves correct context:

```python
# Test script: test_rag_diagnoses.py
from src.rag_engine import ECGExplainer

explainer = ECGExplainer()

diagnoses = ["MI", "STTC", "CD", "HYP", "NORM"]
for diag in diagnoses:
    result = explainer.generate_explanation(diag, age=50, sex="Female")
    print(f"\n{diag}: {result['explanation'][:100]}...")
```

## Success Criteria

Phase 2 is complete when:

- ✅ Vector database exists at `data/vector_db/`
- ✅ Ingestion script runs without errors
- ✅ RAG engine initializes successfully
- ✅ API `/predict` endpoint returns explanations
- ✅ Explanations are relevant to the diagnosis
- ✅ Architecture diagram exists
- ✅ Makefile targets work (`make rag`, `make ingest`)

## Troubleshooting

### Issue: "Vector database not found"
**Solution:** Run `python manage.py ingest` first

### Issue: "HUGGINGFACEHUB_API_TOKEN not found"
**Solution:** Add `HUGGINGFACEHUB_API_TOKEN=your_token` to `.env` file

### Issue: LLM returns empty or error
**Solution:**
- Check HuggingFace API token is valid
- Verify model name is correct (`HuggingFaceH4/zephyr-7b-beta`)
- Check HuggingFace API status

### Issue: Explanations are generic
**Solution:**
- Verify PDFs contain relevant medical content
- Check retrieval is working (test with `similarity_search`)
- Adjust `k_retrieval` parameter (default: 3)

## Quick Verification Command

```powershell
# One-liner verification
python manage.py ingest && python -c "from src.rag_engine import ECGExplainer; e = ECGExplainer(); print('✅ RAG Engine works!')"
```

## Next Steps

Once Phase 2 is verified:
- **Phase 3:** Prompt Engineering & Evaluation
- **Phase 4:** Guardrails & Enhanced Monitoring
- **Phase 5:** Frontend Website
- **Phase 6:** Enhanced CI/CD & Cloud
