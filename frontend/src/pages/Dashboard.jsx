import { useEffect, useState } from 'react'
import { AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts'
import api from '../api'
import StatCard from '../components/StatCard'
import TransactionTable from '../components/TransactionTable'

export default function Dashboard() {
  const [stats, setStats] = useState(null)
  const [txns, setTxns] = useState([])
  const [error, setError] = useState(null)
  const [tick, setTick] = useState(0)

  const load = async () => {
    try {
      const [s, t] = await Promise.all([api.get('/stats'), api.get('/transactions')])
      setStats(s.data)
      setTxns(t.data)
      setError(null)
    } catch (e) { setError('Cannot reach API — is backend running?') }
  }

  useEffect(() => { load(); const i = setInterval(() => { load(); setTick(t => t+1) }, 5000); return () => clearInterval(i) }, [])

  const pieData = stats ? [
    { name: 'FRAUD', value: stats.fraud_detected },
    { name: 'CLEAN', value: stats.total_transactions - stats.fraud_detected }
  ] : []

  const areaData = [...txns].reverse().map(tx => ({ id: `#${tx.id}`, score: Number(tx.anomaly_score) }))

  const CustomTooltip = ({ active, payload }) => {
    if (!active || !payload?.length) return null
    return (
      <div style={{ background: '#040d12', border: '1px solid var(--border)', padding: '8px 14px', fontFamily: 'var(--mono)', fontSize: '12px', color: 'var(--green)' }}>
        {payload[0].name}: {payload[0].value}
      </div>
    )
  }

  return (
    <div className="animate-in">
      {/* Header */}
      <div style={{ marginBottom: '32px', borderLeft: '3px solid var(--green)', paddingLeft: '16px' }}>
        <div style={{ fontFamily: 'var(--mono)', fontSize: '22px', color: 'white', letterSpacing: '2px' }}>
          FRAUD DETECTION TERMINAL
        </div>
        <div style={{ fontFamily: 'var(--mono)', fontSize: '12px', color: 'rgba(0,255,136,0.5)', marginTop: '4px' }}>
          LIVE MONITOR — AUTO REFRESH 5s — TICK_{String(tick).padStart(4,'0')}
        </div>
      </div>

      {/* Error */}
      {error && (
        <div style={{ fontFamily: 'var(--mono)', fontSize: '12px', color: 'var(--red)', background: 'rgba(255,51,102,0.08)', border: '1px solid rgba(255,51,102,0.3)', padding: '12px 20px', borderRadius: '2px', marginBottom: '24px' }}>
          ▲ ERROR: {error}
        </div>
      )}

      {/* Stat Cards */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4,1fr)', gap: '16px', marginBottom: '24px' }}>
        <StatCard label="TOTAL_SCANNED"   value={stats?.total_transactions ?? 0} icon="◈" color="var(--blue)"   glowClass="glow-blue" sub="transactions logged" />
        <StatCard label="FRAUD_DETECTED"  value={stats?.fraud_detected ?? 0}     icon="⚠" color="var(--red)"    glowClass="glow-red"  sub="anomalies found" />
        <StatCard label="FRAUD_RATE"      value={stats ? `${stats.fraud_rate}%` : '0%'} icon="%" color="var(--yellow)" glowClass="glow-yellow" sub="of total volume" />
        <StatCard label="ACCOUNTS_BLOCKED" value={stats?.blocked ?? 0}           icon="⊘" color="var(--green)"  glowClass="glow-green" sub="access denied" />
      </div>

      {/* Charts */}
      <div style={{ display: 'grid', gridTemplateColumns: '1fr 2fr', gap: '16px', marginBottom: '24px' }}>
        {/* Pie */}
        <div className="card" style={{ padding: '24px' }}>
          <div className="label" style={{ marginBottom: '20px' }}>THREAT_DISTRIBUTION</div>
          <ResponsiveContainer width="100%" height={200}>
            <PieChart>
              <Pie data={pieData} cx="50%" cy="50%" innerRadius={55} outerRadius={80} dataKey="value" paddingAngle={3}>
                <Cell fill="var(--red)" />
                <Cell fill="var(--green)" />
              </Pie>
              <Tooltip content={<CustomTooltip />} />
            </PieChart>
          </ResponsiveContainer>
          <div style={{ display: 'flex', justifyContent: 'center', gap: '24px', marginTop: '8px' }}>
            {[['FRAUD', 'var(--red)'], ['CLEAN', 'var(--green)']].map(([l, c]) => (
              <div key={l} style={{ display: 'flex', alignItems: 'center', gap: '6px', fontFamily: 'var(--mono)', fontSize: '11px', color: c }}>
                <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: c }} /> {l}
              </div>
            ))}
          </div>
        </div>

        {/* Area */}
        <div className="card" style={{ padding: '24px' }}>
          <div className="label" style={{ marginBottom: '20px' }}>ANOMALY_SCORE_TIMELINE</div>
          <ResponsiveContainer width="100%" height={200}>
            <AreaChart data={areaData}>
              <defs>
                <linearGradient id="scoreGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%"  stopColor="var(--green)" stopOpacity={0.3} />
                  <stop offset="95%" stopColor="var(--green)" stopOpacity={0} />
                </linearGradient>
              </defs>
              <XAxis dataKey="id" tick={{ fontFamily: 'var(--mono)', fontSize: 10, fill: 'rgba(0,255,136,0.4)' }} />
              <YAxis tick={{ fontFamily: 'var(--mono)', fontSize: 10, fill: 'rgba(0,255,136,0.4)' }} />
              <Tooltip content={<CustomTooltip />} />
              <Area type="monotone" dataKey="score" stroke="var(--green)" strokeWidth={2} fill="url(#scoreGrad)" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Table */}
      <div className="card" style={{ padding: '24px' }}>
        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '20px' }}>
          <div className="label">TRANSACTION_LOG</div>
          <div style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: 'rgba(0,255,136,0.4)' }}>
            {txns.length} RECORDS — <span style={{ color: 'var(--green)' }}>CLICK FRAUD ROW FOR REPORT</span>
          </div>
        </div>
        <TransactionTable transactions={txns} />
      </div>
    </div>
  )
}
