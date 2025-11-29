import { useState } from 'react'
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
    console.log('✅ [App] handlePrediction called with data:', data)
    setPredictionData(data)
    setStep('results')
    setLoading(false)
    console.log('✅ [App] Switched to results step')
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
    console.log('🔄 [App] handlePredictClick called - switching to predicting step')
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
        <h1>❤️ HEARTSIGHT</h1>
        <p>AI-Powered ECG Monitoring & Early Warning System</p>
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
            <>
              <div className="results-header">
                <button className="reset-button" onClick={handleReset}>
                  ← Upload New ECG
                </button>
                <h2>Analysis Complete</h2>
              </div>

              <div className="diagnosis-banner">
                <h1 className="diagnosis-message">
                  {predictionData.prediction === 'NORM'
                    ? '✅ You are Normal'
                    : `⚠️ You have ${predictionData.prediction}`}
                </h1>
                <p className="diagnosis-subtitle">
                  Confidence: {(predictionData.confidence * 100).toFixed(1)}%
                </p>
              </div>

              {ecgSignal && (
                <div className="visualization-section">
                  <h2>ECG Signal Visualization</h2>
                  <ECGVisualization signal={ecgSignal} />
                </div>
              )}

              <div className="prediction-section">
                <PredictionDisplay data={predictionData} />
              </div>

              <div className="chat-section">
                <ChatWidget
                  initialDiagnosis={predictionData.prediction}
                  patientAge={predictionData.patient_metadata?.age}
                  patientSex={predictionData.patient_metadata?.sex}
                />
              </div>
            </>
          )}

          {error && (
            <div className="error-message">
              <p>❌ {error}</p>
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
