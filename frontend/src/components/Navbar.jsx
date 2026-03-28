import { NavLink } from 'react-router-dom'
import { useState, useEffect } from 'react'
import api from '../api'

export default function Navbar() {
  const [online, setOnline] = useState(false)
  const [time, setTime] = useState(new Date())

  useEffect(() => {
    api.get('/').then(() => setOnline(true)).catch(() => setOnline(false))
    const t = setInterval(() => setTime(new Date()), 1000)
    return () => clearInterval(t)
  }, [])

  const links = [
    { to: '/',               label: '// DASHBOARD' },
    { to: '/investigations', label: '// CASES' },
    { to: '/reports',        label: '// REPORTS' },
  ]

  return (
    <nav style={{
      background: 'rgba(2,4,8,0.95)',
      borderBottom: '1px solid rgba(0,255,136,0.2)',
      padding: '0 36px',
      display: 'flex',
      alignItems: 'center',
      justifyContent: 'space-between',
      height: '56px',
      position: 'sticky', top: 0, zIndex: 100,
      backdropFilter: 'blur(10px)'
    }}>
      {/* Logo */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
        <div style={{ fontFamily: 'var(--mono)', fontSize: '18px', color: 'var(--green)', letterSpacing: '3px' }}>
          FRAUD<span style={{ color: 'white' }}>SENSE</span>
        </div>
        <div style={{ fontFamily: 'var(--mono)', fontSize: '10px', color: 'rgba(0,255,136,0.4)', letterSpacing: '2px', borderLeft: '1px solid var(--border)', paddingLeft: '16px' }}>
          AI DETECTION v2.0
        </div>
      </div>

      {/* Links */}
      <div style={{ display: 'flex', gap: '4px' }}>
        {links.map(({ to, label }) => (
          <NavLink key={to} to={to} end={to === '/'}
            style={({ isActive }) => ({
              fontFamily: 'var(--mono)',
              fontSize: '12px',
              letterSpacing: '1px',
              padding: '6px 16px',
              textDecoration: 'none',
              color: isActive ? 'var(--green)' : 'rgba(160,180,176,0.6)',
              borderBottom: isActive ? '2px solid var(--green)' : '2px solid transparent',
              transition: 'all 0.2s'
            })}>
            {label}
          </NavLink>
        ))}
      </div>

      {/* Status */}
      <div style={{ display: 'flex', alignItems: 'center', gap: '20px' }}>
        <div style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: 'rgba(0,255,136,0.4)' }}>
          {time.toLocaleTimeString('en-US', { hour12: false })}
        </div>
        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
          <div style={{
            width: '7px', height: '7px', borderRadius: '50%',
            background: online ? 'var(--green)' : 'var(--red)',
            animation: 'pulse 2s infinite',
            boxShadow: online ? '0 0 8px var(--green)' : '0 0 8px var(--red)'
          }} />
          <span style={{ fontFamily: 'var(--mono)', fontSize: '11px', color: online ? 'var(--green)' : 'var(--red)', letterSpacing: '1px' }}>
            {online ? 'API_ONLINE' : 'API_OFFLINE'}
          </span>
        </div>
      </div>
    </nav>
  )
}
