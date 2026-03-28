export default function StatCard({ label, value, sub, color = 'var(--green)', glowClass = 'glow-green', icon }) {
  return (
    <div className={`card bracket ${glowClass}`} style={{ padding: '24px', animationDelay: '0.1s' }}>
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
        <div>
          <div className="label" style={{ marginBottom: '14px', color }}>{label}</div>
          <div style={{ fontFamily: 'var(--mono)', fontSize: '38px', color, lineHeight: 1, letterSpacing: '-1px' }}>
            {value ?? '—'}
          </div>
          {sub && <div style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: 'rgba(160,180,176,0.5)', marginTop: '8px' }}>{sub}</div>}
        </div>
        <div style={{ fontSize: '28px', opacity: 0.6 }}>{icon}</div>
      </div>
      {/* Bottom bar */}
      <div style={{ height: '2px', background: `${color}22`, marginTop: '20px', borderRadius: '1px', position: 'relative' }}>
        <div style={{ position: 'absolute', left: 0, top: 0, height: '100%', width: '60%', background: color, borderRadius: '1px' }} />
      </div>
    </div>
  )
}
