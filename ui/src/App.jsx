import { useState } from 'react'
import { FaHeartbeat, FaFileUpload, FaChartLine, FaComments } from 'react-icons/fa'
import CSVUpload from './components/CSVUpload'
import ECGVisualization from './components/ECGVisualization'
import PredictionDisplay from './components/PredictionDisplay'
import ChatWidget from './components/ChatWidget'
import PredictingScreen from './components/PredictingScreen'
import './App.css'

function App() {
  const [step, setStep] = useState('upload') // 'upload', 'predicting', 'results'
  const [predictionData, setPredictionData] = useState(null)
  const [ecgSignal, setEcgSignal] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handlePrediction = (data) => {
    console.log('[App] handlePrediction called with data:', data)
    setPredictionData(data)
    setStep('results')
    setLoading(false)
    console.log('[App] Switched to results step')
  }

  const handleSignalLoad = (signal) => {
    setEcgSignal(signal)
    // Don't change step yet - wait for predict button
  }

  const handleError = (err) => {
    setError(err)
    setLoading(false)
    // Don't reset step if we're in predicting - show error on current step
    if (step === 'predicting') {
      setStep('upload') // Go back to upload to show error
    }
  }

  const handleLoading = (isLoading) => {
    setLoading(isLoading)
    setError(null)
    if (isLoading) {
      setStep('predicting')
    }
  }

  const handlePredictClick = () => {
    console.log('[App] handlePredictClick called - switching to predicting step')
    setStep('predicting')
    setLoading(true)
  }

  const handleReset = () => {
    setStep('upload')
    setPredictionData(null)
    setEcgSignal(null)
    setError(null)
    setLoading(false)
  }

  return (
    <div className="app">
      <header className="app-header">
        <div className="header-content">
          <FaHeartbeat className="header-icon" />
          <div className="header-text">
            <h1>HEARTSIGHT</h1>
            <p>AI-Powered ECG Monitoring & Early Warning System</p>
          </div>
        </div>
      </header>

      <main className="app-main">
        <div className="container">
          {step === 'upload' && (
            <div className="upload-section">
              <CSVUpload
                onPrediction={handlePrediction}
                onSignalLoad={handleSignalLoad}
                onError={handleError}
                onPredictClick={handlePredictClick}
                fileLoaded={ecgSignal !== null}
              />
            </div>
          )}

          {step === 'predicting' && (
            <PredictingScreen />
          )}

          {step === 'results' && predictionData && (
            <div className="results-container">
              <div className="results-header">
                <button className="reset-button" onClick={handleReset}>
                  <FaFileUpload /> Upload New ECG
                </button>
                <div className="diagnosis-inline">
                  <span className="diagnosis-code-inline">{predictionData.prediction}</span>
                  <span className="diagnosis-confidence-inline">
                    {(predictionData.confidence * 100).toFixed(1)}% Confidence
                  </span>
                </div>
              </div>

              <div className="results-grid">
                {ecgSignal && (
                  <div className="visualization-section">
                    <ECGVisualization signal={ecgSignal} />
                  </div>
                )}

                <div className="chat-section">
                  <ChatWidget
                    initialDiagnosis={predictionData.prediction}
                    patientAge={predictionData.patient_metadata?.age}
                    patientSex={predictionData.patient_metadata?.sex}
                  />
                </div>

                <div className="prediction-section">
                  <PredictionDisplay data={predictionData} />
                </div>
              </div>
            </div>
          )}

          {error && (
            <div className="error-message">
              <p>{error}</p>
              <button className="retry-button" onClick={handleReset}>
                Try Again
              </button>
            </div>
          )}
        </div>
      </main>

      <footer className="app-footer">
        <p>HEARTSIGHT - MLOps/LLMOps Project | Powered by AI & Machine Learning</p>
      </footer>
    </div>
  )
}

export default App
