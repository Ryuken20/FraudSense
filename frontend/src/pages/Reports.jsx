import { useEffect, useState } from 'react'
import api from '../api'
import RiskBadge from '../components/RiskBadge'

export default function Reports() {
  const [cases, setCases] = useState([])
  const [stats, setStats] = useState(null)

  useEffect(() => {
    Promise.all([api.get('/cases'), api.get('/stats')])
      .then(([c, s]) => { setCases(c.data); setStats(s.data) })
      .catch(console.error)
  }, [])

  const exportCSV = () => {
    const rows = [['CASE_ID','TXN_ID','RISK_SCORE','ACTION']]
    cases.forEach(c => rows.push([`CASE-${c.id}`, `TXN-${c.transaction_id}`, c.risk_score, c.action_taken]))
    const blob = new Blob([rows.map(r => r.join(',')).join('\n')], { type: 'text/csv' })
    const a = document.createElement('a')
    a.href = URL.createObjectURL(blob)
    a.download = `fraudsense_audit_${Date.now()}.csv`
    a.click()
  }

  return (
    <div className="animate-in">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', marginBottom: '32px' }}>
        <div style={{ borderLeft: '3px solid var(--blue)', paddingLeft: '16px' }}>
          <div style={{ fontFamily: 'var(--mono)', fontSize: '22px', color: 'white', letterSpacing: '2px' }}>AUDIT_REPORTS</div>
          <div style={{ fontFamily: 'var(--mono)', fontSize: '12px', color: 'rgba(0,207,255,0.5)', marginTop: '4px' }}>COMPLIANCE TRAIL — FULL LOG</div>
        </div>
        <button className="btn" onClick={exportCSV}>⬇ EXPORT_CSV</button>
      </div>

      {/* Summary */}
      {stats && (
        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: '16px', marginBottom: '24px' }}>
          {[
            { label: 'TOTAL_SCANNED',    val: stats.total_transactions, color: 'var(--blue)' },
            { label: 'FRAUD_CASES',      val: stats.fraud_detected,     color: 'var(--red)' },
            { label: 'FRAUD_RATE',       val: `${stats.fraud_rate}%`,   color: 'var(--yellow)' },
            { label: 'ACCOUNTS_BLOCKED', val: stats.blocked,            color: 'var(--green)' },
          ].map(({ label, val, color }) => (
            <div key={label} className="card" style={{ padding: '20px', textAlign: 'center' }}>
              <div className="label" style={{ marginBottom: '10px', color }}>{label}</div>
              <div style={{ fontFamily: 'var(--mono)', fontSize: '32px', color }}>{val}</div>
            </div>
          ))}
        </div>
      )}

      {/* Table */}
      <div className="card">
        <div style={{ padding: '20px 24px', borderBottom: '1px solid var(--border)' }}>
          <div className="label">FULL_AUDIT_TRAIL — {cases.length} CASES</div>
        </div>
        <table>
          <thead>
            <tr>{['CASE','TRANSACTION','RISK_SCORE','THREAT','ACTION','REPORT_PREVIEW'].map(h => <th key={h}>{h}</th>)}</tr>
          </thead>
          <tbody>
            {cases.length === 0 ? (
              <tr><td colSpan={6} style={{ textAlign: 'center', padding: '48px', fontFamily: 'var(--mono)', color: 'rgba(0,255,136,0.3)', letterSpacing: '2px' }}>[ NO AUDIT RECORDS ]</td></tr>
            ) : cases.map(c => (
              <tr key={c.id}>
                <td style={{ color: 'var(--blue)' }}>CASE-{String(c.id).padStart(4,'0')}</td>
                <td>TXN-{String(c.transaction_id).padStart(4,'0')}</td>
                <td style={{ color: c.risk_score > 0.15 ? 'var(--red)' : 'var(--yellow)' }}>{Number(c.risk_score).toFixed(4)}</td>
                <td><RiskBadge level={c.risk_score > 0.15 ? 'HIGH' : c.risk_score > 0.05 ? 'MEDIUM' : 'LOW'} /></td>
                <td style={{ color: c.action_taken === 'block' ? 'var(--red)' : 'var(--yellow)', fontFamily: 'var(--mono)', fontSize: '11px' }}>
                  {c.action_taken?.toUpperCase()}
                </td>
                <td style={{ maxWidth: '280px', overflow: 'hidden', textOverflow: 'ellipsis', whiteSpace: 'nowrap', fontSize: '11px', color: 'rgba(160,180,176,0.5)' }}>
                  {c.investigation_report?.slice(0, 70)}...
                </td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  )
}
