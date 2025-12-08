import { useState } from 'react'
import { FaInfoCircle, FaTimes, FaChartBar } from 'react-icons/fa'
import './PredictionDisplay.css'

function PredictionDisplay({ data }) {
  const [showExplanation, setShowExplanation] = useState(false)
  const getConfidenceColor = (confidence) => {
    if (confidence >= 0.8) return '#4caf50'
    if (confidence >= 0.6) return '#ff9800'
    return '#f44336'
  }

  const getDiagnosisColor = (diagnosis) => {
    const colors = {
      'NORM': '#4caf50',
      'MI': '#f44336',
      'STTC': '#ff9800',
      'CD': '#2196f3',
      'HYP': '#9c27b0',
    }
    return colors[diagnosis] || '#666'
  }

  const getDiagnosisMessage = (diagnosis) => {
    const messages = {
      'NORM': 'Normal ECG - No abnormalities detected',
      'MI': 'Myocardial Infarction (Heart Attack) detected',
      'STTC': 'ST-T Changes (Ischemia) detected',
      'CD': 'Conduction Disturbance detected',
      'HYP': 'Hypertrophy detected',
    }
    return messages[diagnosis] || diagnosis
  }

  return (
    <>
      <div className="prediction-display">
        <div className="prediction-card">
          <div className="card-header">
            <h3>
              <FaChartBar className="header-icon" />
              Analysis Results
            </h3>
            {data.explanation && (
              <button
                className="explanation-toggle"
                onClick={() => setShowExplanation(true)}
                title="View AI Explanation"
              >
                <FaInfoCircle /> AI Explanation
              </button>
            )}
          </div>

          <div className="diagnosis-section">
            <div className="diagnosis-label-text">Diagnosis</div>
            <div className="diagnosis-value">
              <span
                className="diagnosis-badge"
                style={{ backgroundColor: getDiagnosisColor(data.prediction) }}
              >
                {data.prediction}
              </span>
              <span className="diagnosis-description">{getDiagnosisMessage(data.prediction)}</span>
            </div>
          </div>

          <div className="confidence-section">
            <div className="confidence-label">
              <span>Confidence Level</span>
              <span className="confidence-value">
                {(data.confidence * 100).toFixed(1)}%
              </span>
            </div>
            <div className="confidence-bar-container">
              <div
                className="confidence-bar-fill"
                style={{
                  width: `${data.confidence * 100}%`,
                  backgroundColor: getConfidenceColor(data.confidence)
                }}
              />
            </div>
          </div>

          {data.probabilities && (
            <div className="probabilities">
              <h4>Class Probabilities</h4>
              <div className="probabilities-list">
                {Object.entries(data.probabilities)
                  .sort(([, a], [, b]) => b - a)
                  .map(([class_name, prob]) => (
                    <div key={class_name} className="probability-item">
                      <span className="class-name">{class_name}</span>
                      <div className="probability-bar-container">
                        <div
                          className="probability-bar-fill"
                          style={{
                            width: `${prob * 100}%`,
                            backgroundColor: getDiagnosisColor(class_name)
                          }}
                        />
                      </div>
                      <span className="probability-value">{(prob * 100).toFixed(1)}%</span>
                    </div>
                  ))}
              </div>
            </div>
          )}
        </div>
      </div>

      {showExplanation && data.explanation && (
        <div className="explanation-overlay" onClick={() => setShowExplanation(false)}>
          <div className="explanation-modal" onClick={(e) => e.stopPropagation()}>
            <div className="explanation-header">
              <h3>AI Explanation</h3>
              <button
                className="close-button"
                onClick={() => setShowExplanation(false)}
                aria-label="Close"
              >
                <FaTimes />
              </button>
            </div>
            <div className="explanation-content">
              {data.explanation.split('\n').map((line, i) => (
                <p key={i}>{line}</p>
              ))}
            </div>
            {data.rag_sources !== undefined && (
              <div className="explanation-footer">
                <small>
                  Based on {data.rag_sources} medical source{data.rag_sources !== 1 ? 's' : ''}
                  {data.rag_fallback && ' (using fallback explanation)'}
                </small>
              </div>
            )}
          </div>
        </div>
      )}
    </>
  )
}

export default PredictionDisplay
