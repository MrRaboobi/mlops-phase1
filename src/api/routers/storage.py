import os
from fastapi import APIRouter, HTTPException

router = APIRouter()
BUCKET = os.getenv("S3_BUCKET", "")


def _check_s3_available():
    """Check if S3 client is available."""
    try:
        import boto3  # noqa: F401
        from src.utils.s3_client import read_text, write_text, exists

        return True, read_text, write_text, exists
    except ImportError:
        return False, None, None, None


@router.get("/s3/ping", tags=["Storage"])
def s3_ping():
    _check_s3_available()  # Check if available
    if not BUCKET:
        raise HTTPException(status_code=500, detail="S3_BUCKET not configured")
    return {"bucket": BUCKET, "ok": True}


@router.post("/s3/write-sample", tags=["Storage"])
def s3_write_sample():
    _, _, write_text, _ = _check_s3_available()
    if not BUCKET:
        raise HTTPException(status_code=500, detail="S3_BUCKET not configured")
    key = "samples/hello.txt"
    write_text(BUCKET, key, "hello from API")
    return {"bucket": BUCKET, "key": key, "written": True}


@router.get("/s3/read-sample", tags=["Storage"])
def s3_read_sample():
    _, read_text, _, exists = _check_s3_available()
    if not BUCKET:
        raise HTTPException(status_code=500, detail="S3_BUCKET not configured")
    key = "samples/hello.txt"
    if not exists(BUCKET, key):
        raise HTTPException(status_code=404, detail=f"{key} not found")
    content = read_text(BUCKET, key)
    return {"bucket": BUCKET, "key": key, "content": content}
