const BASE = import.meta.env.VITE_API_URL || '/api'

function getToken() {
  return localStorage.getItem('token') || ''
}

async function request(method, path, body = null) {
  const headers = { 'Content-Type': 'application/json' }
  const token = getToken()
  if (token) headers['Authorization'] = `Bearer ${token}`

  const res = await fetch(`${BASE}${path}`, {
    method,
    headers,
    body: body ? JSON.stringify(body) : null,
  })

  if (res.status === 204) return null

  const data = await res.json()
  if (!res.ok) throw new Error(data.detail || 'Error en la solicitud')
  return data
}

// ── Auth ──────────────────────────────────────────────────────────────────────
export const authApi = {
  registro: (body) => request('POST', '/auth/registro', body),
  login:    (body) => request('POST', '/auth/login', body),
  me:       ()     => request('GET',  '/auth/me'),
}

// ── Ingredientes ──────────────────────────────────────────────────────────────
export const ingredientesApi = {
  listar:   ()         => request('GET',    '/ingredientes/'),
  crear:    (body)     => request('POST',   '/ingredientes/', body),
  actualizar:(id, body)=> request('PUT',    `/ingredientes/${id}`, body),
  eliminar: (id)       => request('DELETE', `/ingredientes/${id}`),
}

// ── Recetas ───────────────────────────────────────────────────────────────────
export const recetasApi = {
  generar:  ()   => request('POST',   '/recetas/generar'),
  listar:   ()   => request('GET',    '/recetas/'),
  obtener:  (id) => request('GET',    `/recetas/${id}`),
  eliminar: (id) => request('DELETE', `/recetas/${id}`),
}

// ── Calificaciones ────────────────────────────────────────────────────────────
export const calificacionesApi = {
  calificar: (recetaId, body) => request('POST', `/calificaciones/${recetaId}`, body),
  obtener:   (recetaId)       => request('GET',  `/calificaciones/${recetaId}`),
}
