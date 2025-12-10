from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
import numpy as np
from typing import List, Optional
from src.utils.model_loader import predict_ecg_signal
from src.monitoring.prometheus_metrics import record_prediction, set_data_drift_score
from src.monitoring.evidently_monitor import get_drift_monitor

# RAG temporarily disabled - using simple explanations

router = APIRouter()


class ECGSignalInput(BaseModel):
    """Input model for ECG signal prediction with RAG explanation.

    The signal should be a 2D array where:
    - First dimension: time steps
    - Second dimension: 12 ECG channels (I, II, III, aVR, aVL, aVF, V1-V6)
    """

    signal: List[List[float]]  # Shape: (time_steps, 12)
    ecg_id: Optional[int] = None  # Optional patient ID for tracking
    age: Optional[int] = None  # Patient age for personalized explanation
    sex: Optional[str] = (
        None  # Patient sex ("Male", "Female", or None) for personalized explanation
    )


class ECGSimpleInput(BaseModel):
    """Simple input for backward compatibility (single value)."""

    signal_value: float


@router.post("/predict", tags=["Model"])
def predict_ecg(input_data: ECGSignalInput):
    """
    Predict ECG classification using the MLflow-registered model.

    Expected input format:
    {
        "signal": [[ch1_t1, ch2_t1, ..., ch12_t1],
                   [ch1_t2, ch2_t2, ..., ch12_t2],
                   ...],
        "ecg_id": 123  # optional
    }
    """
    import time
    from datetime import datetime

    start_time = time.time()
    request_id = f"req_{int(time.time() * 1000)}"

    try:
        print("\n" + "=" * 60)
        print(
            f"🔍 PREDICTION REQUEST [{request_id}] at {datetime.now().strftime('%H:%M:%S')}"
        )
        print(
            f"   Signal: {len(input_data.signal)} x {len(input_data.signal[0]) if input_data.signal else 0}"
        )
        print(f"   Patient Age: {input_data.age if input_data.age else 'Not provided'}")
        print(f"   Patient Sex: {input_data.sex if input_data.sex else 'Not provided'}")
        print(
            "   📝 Note: Age/Sex are used for RAG explanations only, not ML model prediction"
        )
        print("=" * 60)

        # Convert to numpy array
        signal_array = np.array(input_data.signal)
        print(f"📊 Signal converted: {signal_array.shape}")

        # Validate shape
        if len(signal_array.shape) != 2:
            raise HTTPException(
                status_code=400,
                detail=f"Signal must be 2D array (time_steps, 12). Got shape: {signal_array.shape}",
            )

        if signal_array.shape[1] != 12:
            raise HTTPException(
                status_code=400,
                detail=f"Signal must have 12 channels. Got {signal_array.shape[1]} channels",
            )

        # Get prediction from XGBoost model
        print("🤖 Running ML model...")
        model_start = time.time()
        prediction = predict_ecg_signal(signal_array)
        model_time = time.time() - model_start
        predicted_class = prediction["predicted_class"]
        print(
            f"✅ Prediction: {predicted_class} (confidence: {prediction['confidence']:.1%}) in {model_time:.2f}s"
        )

        # Generate RAG explanation
        print("📚 Generating RAG explanation...")
        rag_start = time.time()
        try:
            from src.rag_engine import get_explainer

            explainer = get_explainer()
            explanation_data = explainer.generate_explanation(
                diagnosis=predicted_class,
                age=input_data.age,
                sex=input_data.sex,
            )
            rag_time = time.time() - rag_start
            print(f"   ✅ RAG explanation generated in {rag_time:.2f}s")
        except Exception as rag_error:
            rag_time = time.time() - rag_start
            print(f"   ⚠️  RAG failed ({rag_time:.2f}s): {rag_error}")
            # Fallback to simple explanation
            explanation_data = {
                "explanation": f"Your ECG shows {predicted_class}. Please consult with a cardiologist for detailed interpretation and personalized treatment recommendations.",
                "fallback": True,
            }

        # Combine prediction and explanation
        total_time = time.time() - start_time
        print("=" * 60)
        print(f"✅ COMPLETE in {total_time:.2f}s - Prediction: {predicted_class}")
        print("=" * 60 + "\n")

        # Record metrics to Prometheus
        try:
            record_prediction(
                predicted_class=predicted_class,
                confidence=prediction["confidence"],
                model_latency=model_time,
                rag_latency=rag_time,
                status="success",
                total_latency=total_time,
            )
        except Exception as metrics_error:
            print(f"⚠️  Warning: Failed to record metrics: {metrics_error}")

        # Check for data drift using Evidently
        try:
            drift_monitor = get_drift_monitor()
            drift_report = drift_monitor.check_drift(
                current_signals=[input_data.signal],
                current_predictions=[predicted_class],
                current_confidences=[prediction["confidence"]],
            )
            drift_score = drift_report.get("drift_score", 0.0)

            # Record drift score to Prometheus
            set_data_drift_score(drift_score)

            if drift_report.get("drift_detected"):
                print(f"⚠️  DATA DRIFT DETECTED! Score: {drift_score:.2f}")
                print(
                    f"   Drifted features: {drift_report.get('num_drifted_features', 0)}"
                )
                print(f"   Report: {drift_report.get('report_path', 'N/A')}")
            else:
                print(
                    f"✅ Data drift check: No drift detected (score: {drift_score:.2f})"
                )
        except Exception as drift_error:
            print(f"⚠️  Warning: Drift monitoring failed: {drift_error}")

        result = {
            "ecg_id": input_data.ecg_id,
            "signal_shape": list(signal_array.shape),
            "prediction": predicted_class,
            "confidence": prediction["confidence"],
            "probabilities": prediction["probabilities"],
            "class_index": prediction["class_index"],
            "explanation": explanation_data.get("explanation", ""),
            "patient_metadata": {
                "age": input_data.age,
                "sex": input_data.sex,
            },
        }

        return result

    except HTTPException:
        raise
    except Exception as e:
        error_detail = str(e)
        elapsed = time.time() - start_time
        print("=" * 60)
        print(f"❌ ERROR after {elapsed:.2f}s: {error_detail}")
        print("=" * 60 + "\n")
        raise HTTPException(status_code=500, detail=f"Prediction error: {error_detail}")


@router.post("/predict/simple", tags=["Model"])
def predict_ecg_simple(input_data: ECGSimpleInput):
    """
    Simple prediction endpoint for backward compatibility.
    This is a mock endpoint - use /predict for real model inference.
    """
    result = "Normal" if input_data.signal_value < 0.5 else "Abnormal"
    return {
        "input_signal": input_data.signal_value,
        "prediction": result,
        "note": "This is a mock endpoint. Use /predict for real model inference.",
    }
