import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Navbar from './components/Navbar'
import Dashboard from './pages/Dashboard'
import Investigations from './pages/Investigations'
import CaseDetail from './pages/CaseDetail'
import Reports from './pages/Reports'
import './index.css'

export default function App() {
  return (
    <Router>
      <div style={{ minHeight: '100vh', display: 'flex', flexDirection: 'column' }}>
        <Navbar />
        <main style={{ flex: 1, padding: '28px 36px', maxWidth: '1400px', width: '100%', margin: '0 auto' }}>
          <Routes>
            <Route path="/"               element={<Dashboard />} />
            <Route path="/investigations" element={<Investigations />} />
            <Route path="/case/:id"       element={<CaseDetail />} />
            <Route path="/reports"        element={<Reports />} />
          </Routes>
        </main>
      </div>
    </Router>
  )
}
