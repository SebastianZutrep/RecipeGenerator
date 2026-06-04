import { useState } from 'react'
import { Navigate } from 'react-router-dom'
import { useAuth } from '../context/AuthContext'

export default function Login() {
  const { usuario, login, registro } = useAuth()
  const [tab, setTab] = useState('login')
  const [form, setForm] = useState({ nombre: '', email: '', password: '' })
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  if (usuario) return <Navigate to="/" replace />

  function onChange(e) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
    setError('')
  }

  async function handleSubmit() {
    setCargando(true)
    setError('')
    try {
      if (tab === 'login') {
        await login(form.email, form.password)
      } else {
        if (!form.nombre.trim()) { setError('El nombre es obligatorio'); setCargando(false); return }
        await registro(form.nombre, form.email, form.password)
      }
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  function onKey(e) { if (e.key === 'Enter') handleSubmit() }

  return (
    <div className="login-wrapper">
      <div className="login-card">
        <div className="login-logo">🍽</div>
        <div className="login-title">Generador de Recetas</div>

        <div className="tabs">
          <button className={`tab ${tab === 'login' ? 'active' : ''}`} onClick={() => setTab('login')}>
            Iniciar sesión
          </button>
          <button className={`tab ${tab === 'registro' ? 'active' : ''}`} onClick={() => setTab('registro')}>
            Registrarse
          </button>
        </div>

        {error && <div className="msg msg-error">{error}</div>}

        {tab === 'registro' && (
          <input className="input" style={{ width: '100%', marginBottom: '.7rem' }}
            name="nombre" placeholder="Nombre completo"
            value={form.nombre} onChange={onChange} onKeyDown={onKey} />
        )}
        <input className="input" style={{ width: '100%', marginBottom: '.7rem' }}
          name="email" type="email" placeholder="Email"
          value={form.email} onChange={onChange} onKeyDown={onKey} />
        <input className="input" style={{ width: '100%', marginBottom: '1rem' }}
          name="password" type="password" placeholder="Contraseña"
          value={form.password} onChange={onChange} onKeyDown={onKey} />

        <button className="btn btn-primary" style={{ width: '100%' }}
          onClick={handleSubmit} disabled={cargando}>
          {cargando ? 'Cargando...' : tab === 'login' ? 'Entrar' : 'Crear cuenta'}
        </button>
      </div>
    </div>
  )
}
