import { useState } from 'react'
import { useAuth } from '../context/AuthContext'
import Inventario from '../components/Inventario'
import GenerarReceta from '../components/GenerarReceta'
import Historial from '../components/Historial'
import ModalReceta from '../components/ModalReceta'

export default function Dashboard() {
  const { usuario, logout } = useAuth()
  const [recetaSeleccionada, setRecetaSeleccionada] = useState(null)
  const [refreshHistorial, setRefreshHistorial] = useState(0)

  function onRecetaGenerada() {
    setRefreshHistorial(n => n + 1)
  }

  return (
    <>
      <header className="header">
        <span style={{ fontSize: '1.6rem' }}>🍽</span>
        <h1>Generador de Recetas</h1>
        <div className="nav">
          <span className="saludo">👋 {usuario?.nombre}</span>
          <button className="btn-salir" onClick={logout}>Salir</button>
        </div>
      </header>

      <div className="container">
        <Inventario />
        <GenerarReceta onGenerada={onRecetaGenerada} />
        <Historial
          refresh={refreshHistorial}
          onVerReceta={setRecetaSeleccionada}
        />
      </div>

      {recetaSeleccionada && (
        <ModalReceta
          recetaId={recetaSeleccionada}
          onCerrar={() => setRecetaSeleccionada(null)}
        />
      )}
    </>
  )
}
