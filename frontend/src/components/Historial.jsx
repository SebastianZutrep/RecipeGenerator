import { useState, useEffect } from 'react'
import { recetasApi } from '../api/client'

function difBadge(nivel) {
  const n = (nivel || '').toLowerCase().replace('á', 'a').replace('í', 'i')
  if (n.includes('f')) return <span className="badge badge-facil">{nivel}</span>
  if (n.includes('m')) return <span className="badge badge-medio">{nivel}</span>
  return <span className="badge badge-dificil">{nivel}</span>
}

function Estrellas({ n }) {
  if (!n) return null
  return <span className="stars">{'★'.repeat(n)}{'☆'.repeat(5 - n)}</span>
}

export default function Historial({ refresh, onVerReceta }) {
  const [recetas, setRecetas] = useState([])
  const [error, setError] = useState('')

  useEffect(() => { cargar() }, [refresh])

  async function cargar() {
    try {
      const data = await recetasApi.listar()
      setRecetas(data)
    } catch (e) {
      setError(e.message)
    }
  }

  async function eliminar(id) {
    if (!confirm('¿Eliminar esta receta?')) return
    try {
      await recetasApi.eliminar(id)
      setRecetas(prev => prev.filter(r => r.id !== id))
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="card">
      <div className="card-title">📜 Historial de recetas</div>
      {error && <div className="msg msg-error">{error}</div>}
      {recetas.length === 0
        ? <p className="empty">Aún no has generado recetas. ¡Prueba el botón de arriba!</p>
        : recetas.map(r => (
          <div key={r.id} className="receta-item">
            <div>
              <div className="receta-nombre">{r.nombre_plato}</div>
              <div className="receta-meta">
                <span>⏱ {r.tiempo_estimado}</span>
                {difBadge(r.nivel_dificultad)}
              </div>
            </div>
            <div className="receta-acciones">
              <button className="btn-outline" onClick={() => onVerReceta(r.id)}>Ver</button>
              <button className="btn-danger" onClick={() => eliminar(r.id)}>✕</button>
            </div>
          </div>
        ))
      }
    </div>
  )
}
