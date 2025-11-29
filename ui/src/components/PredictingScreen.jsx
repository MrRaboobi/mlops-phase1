import { useState, useEffect } from 'react'
import './PredictingScreen.css'

function PredictingScreen() {
  const [elapsedTime, setElapsedTime] = useState(0)
  const [currentStep, setCurrentStep] = useState(0)

  const steps = [
    { name: 'Extracting features from ECG signal', icon: '📊' },
    { name: 'Running ML model prediction', icon: '🤖' },
    { name: 'Retrieving medical guidelines', icon: '📚' },
    { name: 'Generating AI explanation', icon: '💡' },
  ]

  useEffect(() => {
    const timer = setInterval(() => {
      setElapsedTime((prev) => prev + 1)
    }, 1000)

    // Simulate step progression (every 3 seconds)
    const stepTimer = setInterval(() => {
      setCurrentStep((prev) => {
        if (prev < steps.length - 1) {
          return prev + 1
        }
        return prev
      })
    }, 3000)

    return () => {
      clearInterval(timer)
      clearInterval(stepTimer)
    }
  }, [])

  const formatTime = (seconds) => {
    const mins = Math.floor(seconds / 60)
    const secs = seconds % 60
    return `${mins}:${secs.toString().padStart(2, '0')}`
  }

  return (
    <div className="predicting-screen">
      <div className="predicting-content">
        <div className="spinner">⏳</div>
        <h2>Predicting (Please Wait)...</h2>
        <p className="timer">⏱️ Elapsed time: {formatTime(elapsedTime)}</p>
        <p className="predicting-description">
          Analyzing your ECG signal with AI model and generating personalized explanation
        </p>

        <div className="steps-container">
          {steps.map((step, index) => (
            <div
              key={index}
              className={`step-item ${index <= currentStep ? 'active' : 'pending'}`}
            >
              <span className="step-icon">
                {index < currentStep ? '✅' : index === currentStep ? '⏳' : '⏸️'}
              </span>
              <span className="step-name">{step.name}</span>
            </div>
          ))}
        </div>

        <p className="predicting-hint">
          This may take 30-60 seconds. Please don't close this page.
        </p>
      </div>
    </div>
  )
}

export default PredictingScreen
