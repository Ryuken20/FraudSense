import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import api from '../api'
import RiskBadge from '../components/RiskBadge'

export default function Investigations() {
  const [cases, setCases] = useState([])
  const navigate = useNavigate()

  useEffect(() => { api.get('/cases').then(r => setCases(r.data)).catch(console.error) }, [])

  return (
    <div className="animate-in">
      <div style={{ marginBottom: '32px', borderLeft: '3px solid var(--red)', paddingLeft: '16px' }}>
        <div style={{ fontFamily: 'var(--mono)', fontSize: '22px', color: 'white', letterSpacing: '2px' }}>ACTIVE_INVESTIGATIONS</div>
        <div style={{ fontFamily: 'var(--mono)', fontSize: '12px', color: 'rgba(255,51,102,0.6)', marginTop: '4px' }}>
          {cases.length} FRAUD CASES FLAGGED — SELECT CASE FOR FULL REPORT
        </div>
      </div>

      <div className="card">
        <table>
          <thead>
            <tr>
              {['CASE_ID','TXN_ID','RISK_SCORE','THREAT_LEVEL','ACTION','STATUS'].map(h => <th key={h}>{h}</th>)}
            </tr>
          </thead>
          <tbody>
            {cases.length === 0 ? (
              <tr><td colSpan={6} style={{ textAlign: 'center', padding: '48px', fontFamily: 'var(--mono)', color: 'rgba(0,255,136,0.3)', letterSpacing: '2px' }}>
                [ NO CASES FOUND ]
              </td></tr>
            ) : cases.map((c, i) => (
              <tr key={c.id} onClick={() => navigate(`/case/${c.transaction_id}`)}
                style={{ cursor: 'pointer' }} className="animate-in">
                <td style={{ color: 'var(--blue)' }}>CASE-{String(c.id).padStart(4,'0')}</td>
                <td style={{ color: 'white' }}>TXN-{String(c.transaction_id).padStart(4,'0')}</td>
                <td style={{ color: c.risk_score > 0.15 ? 'var(--red)' : 'var(--yellow)', fontWeight: 700 }}>
                  {Number(c.risk_score).toFixed(4)}
                </td>
                <td><RiskBadge level={c.risk_score > 0.15 ? 'HIGH' : c.risk_score > 0.05 ? 'MEDIUM' : 'LOW'} /></td>
                <td>
                  <span style={{
                    fontFamily: 'var(--mono)', fontSize: '10px', letterSpacing: '1px', padding: '3px 10px', borderRadius: '2px',
                    background: c.action_taken === 'block' ? 'rgba(255,51,102,0.1)' : 'rgba(255,204,0,0.1)',
                    color: c.action_taken === 'block' ? 'var(--red)' : 'var(--yellow)',
                    border: `1px solid ${c.action_taken === 'block' ? 'rgba(255,51,102,0.3)' : 'rgba(255,204,0,0.3)'}`,
                  }}>
                    {c.action_taken?.toUpperCase()}
                  </span>
                </td>
                <td style={{ color: 'var(--green)', fontFamily: 'var(--mono)', fontSize: '11px' }}>VIEW_REPORT →</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
