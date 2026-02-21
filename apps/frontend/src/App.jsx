import { useState, useEffect } from 'react'
import './App.css'

function App() {
  const [count, setCount] = useState(0)
  const [podName, setPodName] = useState('Loading...')
  const [error, setError] = useState(null)

  // This matches your Tailscale DNS setup
  const API_URL = "http://devops-backend.tail3b5424.ts.net/api/counter"
  const fetchCounter = () => {
    fetch(API_URL)
      .then(res => {
        if (!res.ok) throw new Error("Backend unreachable")
        return res.json()
      })
      .then(data => {
        setCount(data.total_hits)
        setPodName(data.served_by)
        setError(null)
      })
      .catch(err => {
        console.error(err)
        setError("Error: Backend is offline or CORS is blocked")
      })
  }

  // Fetch once when the page loads
  useEffect(() => {
    fetchCounter()
  }, [])

  return (
    <div className="container">
      <h1>🚀 DevOps Ashdod: Final Project</h1>
      <div className="card">
        <h2>Global Hit Counter (Live ✅)</h2>
        {error ? (
          <p className="error">{error}</p>
        ) : (
          <>
            <div className="counter-value">{count}</div>
            <p>Served by K8s Pod: <code>{podName}</code></p>
            <button onClick={fetchCounter}>
              Click to Refresh Counter
            </button>
          </>
        )}
      </div>
      <p className="footer">React + Python + Redis + Kubernetes</p>
    </div>
  )
}

export default App
