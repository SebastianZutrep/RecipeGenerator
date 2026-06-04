import { createContext, useContext, useState, useEffect } from 'react'
import { authApi } from '../api/client'

const AuthContext = createContext(null)

export function AuthProvider({ children }) {
  const [usuario, setUsuario] = useState(null)
  const [cargando, setCargando] = useState(true)

  useEffect(() => {
    const token = localStorage.getItem('token')
    if (!token) { setCargando(false); return }
    authApi.me()
      .then(setUsuario)
      .catch(() => {
        localStorage.removeItem('token')
      })
      .finally(() => setCargando(false))
  }, [])

  async function login(email, password) {
    const data = await authApi.login({ email, password })
    localStorage.setItem('token', data.access_token)
    // En vez de llamar /me, construimos el usuario con lo que tenemos
    setUsuario({ email })
  }

  async function registro(nombre, email, password) {
    await authApi.registro({ nombre, email, password })
    // Tras registrar, hacemos login directo
    await login(email, password)
  }

  function logout() {
    localStorage.removeItem('token')
    setUsuario(null)
  }

  return (
    <AuthContext.Provider value={{ usuario, cargando, login, registro, logout }}>
      {children}
    </AuthContext.Provider>
  )
}

export function useAuth() {
  return useContext(AuthContext)
}