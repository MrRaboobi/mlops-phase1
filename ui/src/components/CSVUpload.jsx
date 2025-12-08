import { useState, useRef } from 'react'
import axios from 'axios'
import Papa from 'papaparse'
import { FaFileUpload, FaCheckCircle, FaUser, FaVenusMars } from 'react-icons/fa'
import './CSVUpload.css'

const API_BASE = import.meta.env.VITE_API_URL || 'http://localhost:8000'

function CSVUpload({ onPrediction, onSignalLoad, onError, onPredictClick, fileLoaded }) {
  const [isDragging, setIsDragging] = useState(false)
  const [patientAge, setPatientAge] = useState('')
  const [patientSex, setPatientSex] = useState('')
  const [signalArray, setSignalArray] = useState(null)
  const [fileName, setFileName] = useState('')
  const fileInputRef = useRef(null)

  const handleDragOver = (e) => {
    e.preventDefault()
    setIsDragging(true)
  }

  const handleDragLeave = (e) => {
    e.preventDefault()
    setIsDragging(false)
  }

  const handleDrop = (e) => {
    e.preventDefault()
    setIsDragging(false)
    const file = e.dataTransfer.files[0]
    if (file && file.name.endsWith('.csv')) {
      handleFile(file)
    } else {
      onError('Please upload a CSV file')
    }
  }

  const handleFileSelect = (e) => {
    const file = e.target.files[0]
    if (file) {
      handleFile(file)
    }
  }

  const handleFile = async (file) => {
    try {
      // Don't set loading - just parse file, wait for Predict button
      onError(null)

      // Parse CSV file
      const text = await file.text()
      Papa.parse(text, {
        header: true,
        skipEmptyLines: true,
        complete: async (results) => {
          try {
            // Extract signal data
            const data = results.data
            if (data.length === 0) {
              throw new Error('CSV file is empty')
            }

            // Get column names
            const columns = Object.keys(data[0])
            console.log('CSV columns:', columns)

            // Find channel columns - look for common patterns
            // PTB-XL format: I, II, III, aVR, aVL, aVF, V1, V2, V3, V4, V5, V6
            // Or: channel-0, channel-1, etc.
            // Or: just numeric columns
            const channelCols = columns.filter(col => {
              const lowerCol = col.toLowerCase()
              if (lowerCol === 'ecg_id' || lowerCol === 'target' || lowerCol === 'id') return false
              // Check if it's a numeric column
              const val = data[0][col]
              if (val === null || val === undefined || val === '') return false
              const numVal = parseFloat(val)
              return !isNaN(numVal)
            })

            // If we found standard lead names, use them in order
            const leadOrder = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']
            let sortedChannels = channelCols

            // Check if we have standard lead names
            const hasStandardLeads = leadOrder.some(lead => channelCols.includes(lead))
            if (hasStandardLeads) {
              sortedChannels = leadOrder.filter(lead => channelCols.includes(lead))
              // Add any remaining numeric columns
              const remaining = channelCols.filter(col => !leadOrder.includes(col))
              sortedChannels = [...sortedChannels, ...remaining]
            } else if (channelCols.some(col => col.toLowerCase().startsWith('channel-'))) {
              // Handle channel-0, channel-1, etc. format
              sortedChannels = channelCols.sort((a, b) => {
                const aMatch = a.match(/channel-(\d+)/i)
                const bMatch = b.match(/channel-(\d+)/i)
                if (aMatch && bMatch) {
                  return parseInt(aMatch[1]) - parseInt(bMatch[1])
                }
                return a.localeCompare(b)
              })
            } else {
              // Sort channel columns if they have numbers
              sortedChannels = channelCols.sort((a, b) => {
                const aNum = parseInt(a.match(/\d+/)?.[0] || '999')
                const bNum = parseInt(b.match(/\d+/)?.[0] || '999')
                return aNum - bNum
              })
            }

            console.log('Selected channels:', sortedChannels)

            // Extract signal array
            let signalArray
            if (columns.includes('ecg_id')) {
              const ecgId = data[0].ecg_id
              const patientData = data.filter(row => row.ecg_id == ecgId)
              signalArray = patientData.map(row =>
                sortedChannels.map(col => parseFloat(row[col]) || 0)
              )
            } else {
              signalArray = data.map(row =>
                sortedChannels.map(col => parseFloat(row[col]) || 0)
              )
            }

            // Ensure we have 12 channels
            if (signalArray.length > 0) {
              if (signalArray[0].length < 12) {
                signalArray = signalArray.map(row => [
                  ...row,
                  ...Array(12 - row.length).fill(0)
                ])
              } else if (signalArray[0].length > 12) {
                signalArray = signalArray.map(row => row.slice(0, 12))
              }
            }

            // Validate we have data
            if (signalArray.length === 0) {
              throw new Error('No signal data found in CSV')
            }

            if (signalArray[0].length === 0) {
              throw new Error('No channel data found in CSV. Expected 12 ECG channels.')
            }

            console.log('Extracted signal shape:', signalArray.length, 'x', signalArray[0].length)

            // Store signal - DON'T trigger prediction yet
            setSignalArray(signalArray)
            setFileName(file.name)
            onSignalLoad(signalArray)
            console.log('[CSVUpload] CSV file loaded successfully. Ready for prediction.')
          } catch (err) {
            console.error('CSV processing error:', err)
            onError(err.message || 'Failed to process ECG data')
            setSignalArray(null)
          }
        },
        error: (error) => {
          console.error('CSV parsing error:', error)
          onError(`CSV parsing error: ${error.message}`)
          setSignalArray(null)
        }
      })
    } catch (err) {
      console.error('File read error:', err)
      onError(err.message || 'Failed to read file')
      setSignalArray(null)
    }
  }

  const handlePredict = async () => {
    console.log('[CSVUpload] handlePredict called')

    if (!signalArray) {
      console.error('[CSVUpload] No signal array available')
      onError('Please upload a CSV file first')
      return
    }

    console.log('[CSVUpload] Preparing to send prediction request...')
    console.log('   Signal shape:', signalArray.length, 'x', signalArray[0]?.length)
    console.log('   Age:', patientAge || 'not provided')
    console.log('   Sex:', patientSex || 'not provided')

    // Trigger predict click to show predicting screen
    console.log('[CSVUpload] Showing predicting screen...')
    onPredictClick()

    try {
      // Prepare request payload
      const payload = {
        signal: signalArray,
        age: patientAge ? parseInt(patientAge) : null,
        sex: patientSex || null,
      }

      console.log('[CSVUpload] Sending POST request to:', `${API_BASE}/predict`)
      const requestStartTime = Date.now()

      // Send to API with timeout
      const response = await axios.post(`${API_BASE}/predict`, payload, {
        timeout: 60000 // 60 second timeout (should be enough with fallback)
      })

      const requestTime = ((Date.now() - requestStartTime) / 1000).toFixed(2)
      console.log(`[CSVUpload] Request completed in ${requestTime}s`)
      console.log('[CSVUpload] Prediction response received:', response.data)

      // Validate response
      if (!response.data.prediction) {
        throw new Error('Invalid response from server: missing prediction')
      }

      console.log('[CSVUpload] Calling onPrediction with results...')
      onPrediction(response.data)
    } catch (err) {
      const requestTime = requestStartTime ? ((Date.now() - requestStartTime) / 1000).toFixed(2) : 'unknown'
      console.error(`[CSVUpload] Prediction error after ${requestTime}s:`, err)
      console.error('   Error details:', {
        message: err.message,
        response: err.response?.data,
        status: err.response?.status
      })

      const errorMessage = err.response?.data?.detail || err.response?.data?.message || err.message || 'Failed to get prediction from ML model'
      onError(errorMessage)
      // Reset to upload step on error
      console.log('[CSVUpload] Error occurred, resetting...')
    }
  }

  return (
    <div className="csv-upload">
      <div className="upload-header">
        <h2>ECG Data Upload</h2>
        <p className="upload-description">
          Upload your ECG CSV file and provide patient information for analysis
        </p>
      </div>

      <div
        className={`drop-zone ${isDragging ? 'dragging' : ''} ${fileLoaded ? 'file-loaded' : ''}`}
        onDragOver={handleDragOver}
        onDragLeave={handleDragLeave}
        onDrop={handleDrop}
        onClick={() => !fileLoaded && fileInputRef.current?.click()}
      >
        <input
          ref={fileInputRef}
          type="file"
          accept=".csv"
          onChange={handleFileSelect}
          style={{ display: 'none' }}
        />
        <div className="drop-zone-content">
          {fileLoaded ? (
            <>
              <FaCheckCircle className="upload-icon success" />
              <p className="drop-zone-text">{fileName}</p>
              <p className="drop-zone-hint">File loaded successfully</p>
            </>
          ) : (
            <>
              <FaFileUpload className="upload-icon" />
              <p className="drop-zone-text">
                {isDragging ? 'Drop CSV file here' : 'Click or drag CSV file to upload'}
              </p>
              <p className="drop-zone-hint">
                Supported format: CSV with ECG signal data (12 channels)
              </p>
            </>
          )}
        </div>
      </div>

      <div className="patient-info">
        <h3>
          <FaUser className="info-icon" />
          Patient Information
          <span className="optional-label">(Optional)</span>
        </h3>
        <div className="input-row">
          <div className="input-group">
            <label htmlFor="age">Age</label>
            <input
              id="age"
              type="number"
              value={patientAge}
              onChange={(e) => setPatientAge(e.target.value)}
              placeholder="Enter age"
              min="0"
              max="120"
            />
          </div>
          <div className="input-group">
            <label htmlFor="sex">
              <FaVenusMars className="label-icon" />
              Sex
            </label>
            <select
              id="sex"
              value={patientSex}
              onChange={(e) => setPatientSex(e.target.value)}
            >
              <option value="">Select...</option>
              <option value="Male">Male</option>
              <option value="Female">Female</option>
            </select>
          </div>
        </div>
      </div>

      {fileLoaded && (
        <div className="predict-button-container">
          <button
            className="predict-button"
            onClick={handlePredict}
          >
            Analyze ECG
          </button>
        </div>
      )}
    </div>
  )
}

export default CSVUpload
