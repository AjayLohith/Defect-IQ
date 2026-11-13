import { useState, useEffect } from 'react'

export default function App() {
  const [health, setHealth] = useState(null)
  const [role, setRole] = useState('QUALITY_ENGINEER')

  useEffect(() => {
    fetch('/api/v1/health')
      .then((res) => res.json())
      .then((data) => setHealth(data))
      .catch((err) => console.error('API health check error:', err))
  }, [])

  return (
    <div className="container">
      <header style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', paddingBottom: '1rem', borderBottom: '1px solid var(--border-color)' }}>
        <div>
          <h1 style={{ fontSize: '1.5rem', fontWeight: 'bold' }}>TraceFlow // Manufacturing Defect Traceability</h1>
          <p style={{ color: 'var(--text-secondary)', fontSize: '0.875rem' }}>Deterministic defect-traceability & quality assurance engine</p>
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '1rem' }}>
          <label style={{ fontSize: '0.875rem', color: 'var(--text-secondary)' }}>Demo Role:</label>
          <select 
            value={role} 
            onChange={(e) => setRole(e.target.value)}
            style={{ padding: '0.5rem', borderRadius: '4px', background: 'var(--bg-secondary)', color: 'var(--text-primary)', border: '1px solid var(--border-color)' }}
          >
            <option value="PLANT_OPERATOR">Plant Operator</option>
            <option value="QUALITY_ENGINEER">Maintenance/Quality Engineer</option>
            <option value="PRODUCTION_PLANNER">Production Planner</option>
            <option value="IT_ADMIN">OT/IT Administrator</option>
          </select>
        </div>
      </header>

      <main style={{ marginTop: '2rem' }}>
        <div style={{ background: 'var(--bg-secondary)', padding: '1.5rem', borderRadius: '8px', border: '1px solid var(--border-color)' }}>
          <h2 style={{ fontSize: '1.25rem', marginBottom: '1rem' }}>System Foundation Status</h2>
          <p>Scaffold initialized successfully. Ready for Phase 3 schema contracts and generator foundation.</p>
          <div style={{ marginTop: '1rem', padding: '1rem', background: 'var(--bg-tertiary)', borderRadius: '4px', fontFamily: 'monospace', fontSize: '0.875rem' }}>
            API Status: {health ? JSON.stringify(health) : 'Connecting to API...'}
          </div>
        </div>
      </main>
    </div>
  )
}

