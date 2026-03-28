export default function RiskBadge({ level }) {
  const map = {
    HIGH:   { color: 'var(--red)',    bg: 'rgba(255,51,102,0.1)',  border: 'rgba(255,51,102,0.4)',  label: '▲ HIGH'   },
    MEDIUM: { color: 'var(--yellow)', bg: 'rgba(255,204,0,0.1)',   border: 'rgba(255,204,0,0.4)',   label: '● MEDIUM' },
    LOW:    { color: 'var(--green)',  bg: 'rgba(0,255,136,0.08)',  border: 'rgba(0,255,136,0.3)',   label: '▼ LOW'    },
  }
  const s = map[level?.toUpperCase()] || map.LOW
  return (
    <span style={{
      fontFamily: 'var(--mono)', fontSize: '10px', letterSpacing: '1px',
      padding: '3px 10px', borderRadius: '2px',
      background: s.bg, color: s.color,
      border: `1px solid ${s.border}`,
    }}>
      {s.label}
    </span>
  )
}
