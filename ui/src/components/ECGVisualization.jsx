import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts'
import './ECGVisualization.css'

function ECGVisualization({ signal }) {
  if (!signal || signal.length === 0) {
    return <p>No signal data available</p>
  }

  // Extract Lead I (channel 0) and Lead II (channel 1) for visualization
  const chartData = signal.map((row, index) => ({
    time: index,
    'Lead I': row[0] || 0,
    'Lead II': row[1] || 0,
  }))

  // Downsample if too many points (for performance)
  const maxPoints = 2000
  const step = Math.max(1, Math.floor(chartData.length / maxPoints))
  const sampledData = chartData.filter((_, i) => i % step === 0)

  return (
    <div className="ecg-visualization">
      <div className="ecg-chart-container">
        <h3>Lead I (Channel 1)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={sampledData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="time"
              label={{ value: 'Time (samples)', position: 'insideBottom', offset: -5 }}
            />
            <YAxis
              label={{ value: 'Amplitude (mV)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="Lead I"
              stroke="#667eea"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="ecg-chart-container">
        <h3>Lead II (Channel 2)</h3>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={sampledData} margin={{ top: 5, right: 30, left: 20, bottom: 5 }}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis
              dataKey="time"
              label={{ value: 'Time (samples)', position: 'insideBottom', offset: -5 }}
            />
            <YAxis
              label={{ value: 'Amplitude (mV)', angle: -90, position: 'insideLeft' }}
            />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="Lead II"
              stroke="#764ba2"
              strokeWidth={2}
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </div>

      <div className="ecg-info">
        <p><strong>Total Samples:</strong> {signal.length}</p>
        <p><strong>Channels:</strong> 12 (showing Lead I and Lead II)</p>
      </div>
    </div>
  )
}

export default ECGVisualization
