import { useState } from 'react'
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Brush } from 'recharts'
import { FaChartLine } from 'react-icons/fa'
import './ECGVisualization.css'

// Standard 12-lead ECG mapping: channel-0 to channel-11 maps to I, II, III, aVR, aVL, aVF, V1, V2, V3, V4, V5, V6
const LEAD_NAMES = ['I', 'II', 'III', 'aVR', 'aVL', 'aVF', 'V1', 'V2', 'V3', 'V4', 'V5', 'V6']

function ECGVisualization({ signal }) {
  const [selectedLeads, setSelectedLeads] = useState([0, 1]) // Default to Lead I and II

  if (!signal || signal.length === 0) {
    return <p className="no-data">No signal data available</p>
  }

  // Prepare chart data with selected leads
  // signal is an array where each element is [channel-0, channel-1, ..., channel-11]
  const chartData = signal.map((row, index) => {
    const dataPoint = { time: index }
    selectedLeads.forEach(leadIndex => {
      // Map channel index directly to lead name
      dataPoint[LEAD_NAMES[leadIndex]] = row[leadIndex] || 0
    })
    return dataPoint
  })

  // Downsample if too many points (for performance)
  const maxPoints = 2000
  const step = Math.max(1, Math.floor(chartData.length / maxPoints))
  const sampledData = chartData.filter((_, i) => i % step === 0)

  const colors = ['#2563eb', '#dc2626', '#16a34a', '#ea580c', '#9333ea', '#0891b2', '#f59e0b', '#10b981', '#3b82f6', '#8b5cf6', '#ec4899', '#06b6d4']

  const toggleLead = (leadIndex) => {
    setSelectedLeads(prev => {
      if (prev.includes(leadIndex)) {
        return prev.length > 1 ? prev.filter(i => i !== leadIndex) : prev
      } else {
        return prev.length < 4 ? [...prev, leadIndex] : prev
      }
    })
  }

  return (
    <div className="ecg-visualization">
      <div className="ecg-header">
        <h3>
          <FaChartLine className="header-icon" />
          ECG Signal Visualization
        </h3>
        <div className="lead-selector">
          <span className="selector-label">Select Leads:</span>
          {LEAD_NAMES.map((lead, index) => (
            <button
              key={index}
              className={`lead-button ${selectedLeads.includes(index) ? 'active' : ''}`}
              onClick={() => toggleLead(index)}
            >
              {lead}
            </button>
          ))}
        </div>
      </div>

      <div className="ecg-chart-wrapper">
        <ResponsiveContainer width="100%" height={280}>
          <LineChart data={sampledData} margin={{ top: 10, right: 30, left: 20, bottom: 40 }}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e5e7eb" />
            <XAxis
              dataKey="time"
              label={{ value: 'Time (samples)', position: 'insideBottom', offset: -5 }}
              stroke="#6b7280"
              tick={{ fill: '#6b7280', fontSize: 12 }}
            />
            <YAxis
              label={{ value: 'Amplitude (mV)', angle: -90, position: 'insideLeft' }}
              stroke="#6b7280"
              tick={{ fill: '#6b7280', fontSize: 12 }}
            />
            <Tooltip
              contentStyle={{
                backgroundColor: '#fff',
                border: '1px solid #e5e7eb',
                borderRadius: '6px',
                padding: '8px'
              }}
            />
            <Legend
              wrapperStyle={{ paddingTop: '10px' }}
              iconType="line"
            />
            {selectedLeads.map((leadIndex, idx) => (
              <Line
                key={leadIndex}
                type="monotone"
                dataKey={LEAD_NAMES[leadIndex]}
                stroke={colors[leadIndex % colors.length]}
                strokeWidth={2}
                dot={false}
                activeDot={{ r: 4 }}
              />
            ))}
            <Brush dataKey="time" height={20} stroke="#2563eb" />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="ecg-info">
        <div className="info-item">
          <span className="info-label">Total Samples:</span>
          <span className="info-value">{signal.length.toLocaleString()}</span>
        </div>
        <div className="info-item">
          <span className="info-label">Channels:</span>
          <span className="info-value">12</span>
        </div>
        <div className="info-item">
          <span className="info-label">Displaying:</span>
          <span className="info-value">
            {selectedLeads.map(i => LEAD_NAMES[i]).join(', ')}
          </span>
        </div>
      </div>
    </div>
  )
}

export default ECGVisualization
