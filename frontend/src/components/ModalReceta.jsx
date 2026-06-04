import { useState, useEffect } from 'react'
import { recetasApi, calificacionesApi } from '../api/client'

export default function ModalReceta({ recetaId, onCerrar }) {
  const [receta, setReceta] = useState(null)
  const [calificacion, setCalificacion] = useState(null)
  const [error, setError] = useState('')

  useEffect(() => {
    cargar()
    // Cerrar con Escape
    const onKey = (e) => { if (e.key === 'Escape') onCerrar() }
    window.addEventListener('keydown', onKey)
    return () => window.removeEventListener('keydown', onKey)
  }, [recetaId])

  async function cargar() {
    try {
      const [r, c] = await Promise.allSettled([
        recetasApi.obtener(recetaId),
        calificacionesApi.obtener(recetaId),
      ])
      if (r.status === 'fulfilled') setReceta(r.value)
      if (c.status === 'fulfilled') setCalificacion(c.value)
    } catch (e) {
      setError(e.message)
    }
  }

  async function calificar(estrellas) {
    try {
      const cal = await calificacionesApi.calificar(recetaId, { estrellas })
      setCalificacion(cal)
    } catch (e) {
      setError(e.message)
    }
  }

  if (!receta) return (
    <div className="modal-overlay" onClick={onCerrar}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onCerrar}>✕</button>
        <p style={{ color: '#888' }}>Cargando...</p>
      </div>
    </div>
  )

  const ingredientes = JSON.parse(receta.ingredientes_json)
  const pasos = JSON.parse(receta.pasos_preparacion)

  return (
    <div className="modal-overlay" onClick={onCerrar}>
      <div className="modal-box" onClick={e => e.stopPropagation()}>
        <button className="modal-close" onClick={onCerrar}>✕</button>

        <h2>{receta.nombre_plato}</h2>
        <p style={{ color: '#666', fontSize: '.88rem', marginBottom: '.25rem' }}>
          ⏱ {receta.tiempo_estimado} &nbsp;|&nbsp; Dificultad: {receta.nivel_dificultad}
        </p>

        {error && <div className="msg msg-error">{error}</div>}

        <h3>Ingredientes</h3>
        <ul>
          {ingredientes.map((ing, i) => (
            <li key={i}>{ing.nombre}: {ing.cantidad} {ing.unidad || ''}</li>
          ))}
        </ul>

        <h3>Preparación</h3>
        <ol>
          {pasos.map((paso, i) => (
            <li key={i}>{paso}</li>
          ))}
        </ol>

        <h3>Calificación</h3>
        {calificacion
          ? <p>
              <span className="stars">{'★'.repeat(calificacion.estrellas)}{'☆'.repeat(5 - calificacion.estrellas)}</span>
              {calificacion.comentario && <span style={{ marginLeft: '.5rem', fontSize: '.88rem', color: '#666' }}>{calificacion.comentario}</span>}
            </p>
          : <p style={{ fontSize: '.85rem', color: '#999' }}>Sin calificación aún</p>
        }

        <div className="rating-btns">
          {[1, 2, 3, 4, 5].map(n => (
            <button key={n} onClick={() => calificar(n)} title={`${n} estrella${n > 1 ? 's' : ''}`}>
              {'★'.repeat(n)}
            </button>
          ))}
        </div>
      </div>
    </div>
  )
}
