import { useState, useEffect } from 'react'
import { ingredientesApi } from '../api/client'

export default function Inventario() {
  const [ingredientes, setIngredientes] = useState([])
  const [form, setForm] = useState({ nombre: '', cantidad: '', unidad: '' })
  const [error, setError] = useState('')
  const [cargando, setCargando] = useState(false)

  useEffect(() => { cargar() }, [])

  async function cargar() {
    try {
      const data = await ingredientesApi.listar()
      setIngredientes(data)
    } catch (e) {
      setError(e.message)
    }
  }

  function onChange(e) {
    setForm(f => ({ ...f, [e.target.name]: e.target.value }))
    setError('')
  }

  async function agregar() {
    if (!form.nombre.trim() || !form.cantidad.trim()) {
      setError('Nombre y cantidad son obligatorios')
      return
    }
    setCargando(true)
    try {
      await ingredientesApi.crear({
        nombre: form.nombre.trim(),
        cantidad: form.cantidad.trim(),
        unidad: form.unidad.trim() || null,
      })
      setForm({ nombre: '', cantidad: '', unidad: '' })
      await cargar()
    } catch (e) {
      setError(e.message)
    } finally {
      setCargando(false)
    }
  }

  async function eliminar(id) {
    try {
      await ingredientesApi.eliminar(id)
      setIngredientes(prev => prev.filter(i => i.id !== id))
    } catch (e) {
      setError(e.message)
    }
  }

  return (
    <div className="card">
      <div className="card-title">📦 Mi inventario de ingredientes</div>

      {error && <div className="msg msg-error">{error}</div>}

      <div className="form-row">
        <input className="input" name="nombre" placeholder="Ingrediente (ej: Pollo)"
          value={form.nombre} onChange={onChange} style={{ flex: 2 }} />
        <input className="input sm" name="cantidad" placeholder="Cantidad"
          value={form.cantidad} onChange={onChange} />
        <input className="input sm" name="unidad" placeholder="Unidad (ej: g)"
          value={form.unidad} onChange={onChange} />
        <button className="btn btn-primary" onClick={agregar} disabled={cargando}>
          + Agregar
        </button>
      </div>

      {ingredientes.length === 0
        ? <p className="empty">Sin ingredientes aún. Agrega los que tengas en casa.</p>
        : ingredientes.map(ing => (
          <div key={ing.id} className="ing-item">
            <span>
              🥗 <span className="ing-nombre">{ing.nombre}</span>
              <span className="ing-cantidad">— {ing.cantidad} {ing.unidad || ''}</span>
            </span>
            <button className="btn-danger" onClick={() => eliminar(ing.id)}>✕</button>
          </div>
        ))
      }
    </div>
  )
}
