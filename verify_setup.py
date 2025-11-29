"""Quick verification script to check if everything is set up correctly."""

from pathlib import Path

print("=" * 60)
print("HEARTSIGHT Setup Verification")
print("=" * 60)

checks = []

# Check 1: Model exists
model_path = Path("mlruns/models/heartsight_xgb_v1")
checks.append(("Model registered in MLflow", model_path.exists()))

# Check 2: Vector DB exists
vector_db = Path("data/vector_db")
checks.append(
    ("Vector database exists", vector_db.exists() and any(vector_db.iterdir()))
)

# Check 3: Sample CSV exists
sample_csv = Path("sample_upload_TEST_PATIENT.csv")
checks.append(("Sample CSV file exists", sample_csv.exists()))

# Check 4: .env file exists
env_file = Path(".env")
checks.append((".env file exists", env_file.exists()))

# Check 5: PDFs exist
docs_dir = Path("data/docs")
pdfs = list(docs_dir.glob("*.pdf")) if docs_dir.exists() else []
checks.append(("PDF documents exist", len(pdfs) >= 5))

# Check 6: Frontend exists
ui_dir = Path("ui")
checks.append(("Frontend directory exists", ui_dir.exists()))

# Check 7: RAG engine exists
rag_engine = Path("src/rag_engine.py")
checks.append(("RAG engine exists", rag_engine.exists()))

# Check 8: Training script exists
train_script = Path("src/pipeline/train.py")
checks.append(("Training script exists", train_script.exists()))

# Print results
print("\nVerification Results:")
print("-" * 60)
all_passed = True
for name, passed in checks:
    status = "✅" if passed else "❌"
    print(f"{status} {name}")
    if not passed:
        all_passed = False

print("-" * 60)
if all_passed:
    print("\n🎉 ALL CHECKS PASSED! System is ready to run.")
    print("\nNext steps:")
    print("1. Start backend: python manage.py dev")
    print("2. Start frontend: python manage.py ui")
    print("3. Open http://localhost:3000 in your browser")
else:
    print("\n⚠️  Some checks failed. Please review the issues above.")
print("=" * 60)
