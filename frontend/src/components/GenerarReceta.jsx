import { useState } from 'react'
import { recetasApi } from '../api/client'

export default function GenerarReceta({ onGenerada }) {
  const [cargando, setCargando] = useState(false)
  const [exito, setExito] = useState('')
  const [error, setError] = useState('')

  async function generar() {
    setCargando(true)
    setExito('')
    setError('')
    try {
      const receta = await recetasApi.generar()
      setExito(`Receta generada: ${receta.nombre_plato}`)
      onGenerada()
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  return (
    <div className="card generar-center">
      <div className="card-title" style={{ justifyContent: 'center' }}>✨ Generar receta con IA</div>
      <p className="generar-sub">
        El sistema analizará tu inventario y creará una receta personalizada
      </p>
      <button className="btn btn-primary" onClick={generar} disabled={cargando}>
        {cargando ? 'Generando...' : 'Generar Receta'}
      </button>
      {exito && <div className="msg msg-success" style={{ marginTop: '.9rem' }}>{exito}</div>}
      {error && <div className="msg msg-error" style={{ marginTop: '.9rem' }}>{error}</div>}
    </div>
  )
}
