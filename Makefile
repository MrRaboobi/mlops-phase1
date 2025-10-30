
---

### **Content for Makefile**

Minimal commands (we’ll expand as we go on):

```makefile
dev:
	uvicorn src.api.main:app --reload

test:
	pytest -v

lint:
	ruff check .
	black --check .

format:
	black .

docker:
	docker build -t ecg-app .

clean:
	rm -rf __pycache__ .pytest_cache

run:
	docker run -p 8000:8000 ecg-app

check:
	pre-commit run --all-files
