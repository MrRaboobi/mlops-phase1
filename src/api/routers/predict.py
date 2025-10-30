from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class ECGInput(BaseModel):
    signal_value: float


@router.post("/predict", tags=["Model"])
def predict_ecg(input_data: ECGInput):
    result = "Normal" if input_data.signal_value < 0.5 else "Abnormal"
    return {"input_signal": input_data.signal_value, "prediction": result}
