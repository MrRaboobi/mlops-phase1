
---

### **Content for Makefile**

Minimal commands (we’ll expand later):

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
