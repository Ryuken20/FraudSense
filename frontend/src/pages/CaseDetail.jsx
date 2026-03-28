import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import api from '../api'

export default function CaseDetail() {
  const { id } = useParams()
  const navigate = useNavigate()
  const [data, setData] = useState(null)

  useEffect(() => { api.get(`/investigate/${id}`).then(r => setData(r.data)).catch(console.error) }, [id])

  if (!data) return (
    <div style={{ fontFamily: 'var(--mono)', color: 'var(--green)', padding: '48px', letterSpacing: '2px', animation: 'blink 1s infinite' }}>
      [ LOADING INVESTIGATION... ]
    </div>
  )

  if (data.message) return (
    <div style={{ fontFamily: 'var(--mono)', color: 'var(--red)', padding: '48px' }}>▲ {data.message}</div>
  )

  const riskColor = data.risk_score > 0.15 ? 'var(--red)' : data.risk_score > 0.05 ? 'var(--yellow)' : 'var(--green)'

  return (
    <div className="animate-in">
      <button onClick={() => navigate(-1)} className="btn" style={{ marginBottom: '28px', fontSize: '11px' }}>
        ← BACK_TO_LIST
      </button>

      <div style={{ marginBottom: '28px', borderLeft: '3px solid var(--red)', paddingLeft: '16px' }}>
        <div style={{ fontFamily: 'var(--mono)', fontSize: '22px', color: 'white', letterSpacing: '2px' }}>
          INVESTIGATION_REPORT
        </div>
        <div style={{ fontFamily: 'var(--mono)', fontSize: '12px', color: 'rgba(255,51,102,0.6)', marginTop: '4px' }}>
          TRANSACTION #{String(id).padStart(4,'0')} — FULL AI ANALYSIS
        </div>
      </div>

      {/* Metric cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(3,1fr)', gap: '16px', marginBottom: '24px' }}>
        {[
          { label: 'TRANSACTION_ID', value: `#${String(data.transaction_id).padStart(4,'0')}`, color: 'var(--blue)' },
          { label: 'ANOMALY_SCORE',  value: Number(data.risk_score).toFixed(4), color: riskColor },
          { label: 'ACTION_TAKEN',   value: data.action?.toUpperCase(), color: data.action === 'block' ? 'var(--red)' : 'var(--yellow)' },
        ].map(({ label, value, color }) => (
          <div key={label} className="card bracket" style={{ padding: '24px' }}>
            <div className="label" style={{ marginBottom: '12px', color }}>{label}</div>
            <div style={{ fontFamily: 'var(--mono)', fontSize: '32px', color, letterSpacing: '-1px' }}>{value}</div>
          </div>
        ))}
      </div>

      {/* Report */}
      <div className="card glow-red" style={{ padding: '28px' }}>
        <div className="label" style={{ marginBottom: '20px', color: 'var(--red)' }}>
          AI_GENERATED_INVESTIGATION_REPORT
        </div>
        <pre style={{
          fontFamily: 'var(--mono)', fontSize: '13px', lineHeight: '1.9',
          color: 'var(--text)', whiteSpace: 'pre-wrap', wordBreak: 'break-word',
          background: 'rgba(0,0,0,0.4)', padding: '20px', borderRadius: '2px',
          border: '1px solid rgba(0,255,136,0.1)',
          maxHeight: '600px', overflowY: 'auto'
        }}>
          {data.investigation_report}
        </pre>
      </div>
    </div>
  )
}
