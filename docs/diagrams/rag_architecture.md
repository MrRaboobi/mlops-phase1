# RAG Architecture Diagram

## System Architecture: RAG-Enhanced ECG Explanation Pipeline

```mermaid
graph TB
    subgraph "Data Ingestion Phase"
        A[PDF Documents<br/>data/docs/] --> B[PDF Loader<br/>PyPDFLoader]
        B --> C[Text Splitter<br/>Chunk Size: 500<br/>Overlap: 50]
        C --> D[Embedding Model<br/>sentence-transformers<br/>all-MiniLM-L6-v2]
        D --> E[ChromaDB<br/>Vector Store<br/>data/vector_db/]
    end

    subgraph "Inference Phase"
        F[ECG Signal Input] --> G[XGBoost Model<br/>Phase 1]
        G --> H[Prediction<br/>NORM/MI/STTC/CD/HYP]
        H --> I[RAG Engine<br/>ECGExplainer]
        J[Patient Metadata<br/>Age, Sex] --> I
        E --> I
        I --> K[LLM<br/>HuggingFace<br/>zephyr-7b-beta]
        K --> L[Explanation<br/>Patient-Friendly]
    end

    subgraph "API Response"
        H --> M[JSON Response]
        L --> M
        M --> N[Prediction + Explanation<br/>+ Confidence + Probabilities]
    end

    style A fill:#e1f5ff
    style E fill:#fff4e1
    style G fill:#e8f5e9
    style K fill:#f3e5f5
    style N fill:#ffebee
```

## Data Flow Diagram

```mermaid
sequenceDiagram
    participant User
    participant API
    participant Model
    participant RAG
    participant VectorDB
    participant LLM

    User->>API: POST /predict<br/>{signal, age, sex}
    API->>Model: predict_ecg_signal(signal)
    Model-->>API: {prediction: "MI", confidence: 0.95}
    API->>RAG: generate_explanation("MI", age=65, sex="Male")
    RAG->>VectorDB: similarity_search("myocardial infarction elderly")
    VectorDB-->>RAG: [Relevant chunks from PDFs]
    RAG->>LLM: Prompt with context + patient info
    LLM-->>RAG: Generated explanation
    RAG-->>API: {explanation: "..."}
    API-->>User: {prediction, confidence, explanation}
```

## Component Details

### 1. Document Ingestion (`src/ingest.py`)
- **Input:** 5 PDF files in `data/docs/`
- **Process:**
  1. Load PDFs using PyPDFLoader
  2. Split into chunks (500 chars, 50 overlap)
  3. Embed using local sentence-transformers model
  4. Store in ChromaDB vector database
- **Output:** Persistent vector store at `data/vector_db/`

### 2. RAG Engine (`src/rag_engine.py`)
- **ECGExplainer Class:**
  - Loads vector store on initialization
  - Initializes HuggingFace LLM via API
  - Retrieves relevant context based on diagnosis + patient metadata
  - Generates personalized explanations

### 3. API Integration (`src/api/routers/predict.py`)
- **Enhanced `/predict` endpoint:**
  - Accepts: `signal`, `age`, `sex` (optional)
  - Returns: `prediction`, `confidence`, `explanation`, `probabilities`

### 4. Retrieval Strategy
- **Diagnosis-based search terms:**
  - NORM → "normal sinus rhythm", "normal ECG"
  - MI → "myocardial infarction", "heart attack"
  - STTC → "ST-T changes", "ischemia"
  - CD → "conduction disturbance", "bundle branch block"
  - HYP → "hypertrophy", "LVH"
- **Age-enhanced queries:**
  - < 30: "young adult"
  - 30-50: "middle-aged"
  - > 50: "elderly"

## File Structure

```
data/
├── docs/                    # PDF knowledge base
│   ├── MI_Recovery_Guide.pdf
│   ├── STTC_Ischemia_Guide.pdf
│   ├── Conduction_Disturbance_Guide.pdf
│   ├── Hypertrophy_Management.pdf
│   └── General_ECG_Guide.pdf
└── vector_db/              # ChromaDB vector store (generated)

src/
├── ingest.py                # Document ingestion pipeline
├── rag_engine.py            # RAG explanation generator
└── api/routers/predict.py   # Enhanced API endpoint
```

## Usage

1. **Ingest documents:**
   ```bash
   python manage.py ingest
   # or
   make rag
   ```

2. **Use in API:**
   ```bash
   python manage.py dev
   ```

3. **Test endpoint:**
   ```bash
   curl -X POST http://localhost:8000/predict \
     -H "Content-Type: application/json" \
     -d '{
       "signal": [[...]],
       "age": 65,
       "sex": "Male"
     }'
   ```
