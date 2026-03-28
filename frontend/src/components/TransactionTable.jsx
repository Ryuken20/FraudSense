import { useNavigate } from 'react-router-dom'
import RiskBadge from './RiskBadge'

export default function TransactionTable({ transactions = [] }) {
  const navigate = useNavigate()

  if (!transactions.length) return (
    <div style={{ padding: '48px', textAlign: 'center', fontFamily: 'var(--mono)', color: 'rgba(0,255,136,0.3)', fontSize: '13px', letterSpacing: '2px' }}>
      [ NO TRANSACTIONS RECORDED ]
    </div>
  )

  return (
    <div style={{ overflowX: 'auto' }}>
      <table>
        <thead>
          <tr>
            {['TXN_ID','USER','AMOUNT','LOCATION','RISK','SCORE','ACTION','TIME'].map(h => (
              <th key={h}>{h}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {transactions.map((tx, i) => (
            <tr key={tx.id}
              onClick={() => tx.is_fraud && navigate(`/case/${tx.id}`)}
              style={{ cursor: tx.is_fraud ? 'pointer' : 'default', animationDelay: `${i * 0.05}s` }}
              className="animate-in">
              <td style={{ color: 'var(--blue)' }}>#{String(tx.id).padStart(4,'0')}</td>
              <td style={{ color: 'white' }}>{tx.user_id}</td>
              <td style={{ color: tx.amount > 50000 ? 'var(--red)' : 'var(--green)', fontWeight: 700 }}>
                ${Number(tx.amount).toLocaleString()}
              </td>
              <td>{tx.location}</td>
              <td><RiskBadge level={tx.risk_level || (tx.is_fraud ? 'HIGH' : 'LOW')} /></td>
              <td style={{ color: tx.anomaly_score > 0.1 ? 'var(--red)' : 'var(--green)' }}>
                {Number(tx.anomaly_score).toFixed(4)}
              </td>
              <td>
                <span style={{
                  fontFamily: 'var(--mono)', fontSize: '10px', letterSpacing: '1px',
                  padding: '3px 10px', borderRadius: '2px',
                  background: tx.is_fraud ? (tx.anomaly_score > 0.15 ? 'rgba(255,51,102,0.1)' : 'rgba(255,204,0,0.1)') : 'rgba(0,255,136,0.08)',
                  color: tx.is_fraud ? (tx.anomaly_score > 0.15 ? 'var(--red)' : 'var(--yellow)') : 'var(--green)',
                  border: `1px solid ${tx.is_fraud ? (tx.anomaly_score > 0.15 ? 'rgba(255,51,102,0.3)' : 'rgba(255,204,0,0.3)') : 'rgba(0,255,136,0.2)'}`,
                }}>
                  {tx.is_fraud ? (tx.anomaly_score > 0.15 ? 'BLOCK' : 'MONITOR') : 'CLEAR'}
                </span>
              </td>
              <td style={{ color: 'rgba(160,180,176,0.5)', fontSize: '11px' }}>
                {new Date(tx.timestamp).toLocaleTimeString('en-US', { hour12: false })}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  )
}
