from fastapi import APIRouter

router = APIRouter()


@router.get("/health", tags=["System"])
def health_check():
    """
    Health check endpoint to verify the API is running.
    """
    return {"status": "healthy", "message": "API is operational"}
