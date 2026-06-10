# 🍽️ Proyecto Recetas

> Aplicación web full-stack para generación inteligente de recetas a partir del inventario de ingredientes del usuario, potenciada por un modelo de lenguaje (LLM).

---

## 📋 Tabla de Contenidos

- [Descripción](#descripción)
- [Características](#características)
- [Arquitectura](#arquitectura)
- [Tecnologías](#tecnologías)
- [Estructura del Proyecto](#estructura-del-proyecto)
- [Diagrama Entidad-Relación](#diagrama-entidad-relación)
- [Requisitos Previos](#requisitos-previos)
- [Instalación y Configuración](#instalación-y-configuración)
- [Variables de Entorno](#variables-de-entorno)
- [Uso](#uso)
- [Endpoints de la API](#endpoints-de-la-api)
- [Pruebas](#pruebas)
- [Despliegue con Docker](#despliegue-con-docker)
- [Contribución](#contribución)

---

## Descripción

**Proyecto Recetas** es una aplicación web full-stack desarrollada con **FastAPI** y **MySQL** que permite a los usuarios gestionar su inventario de ingredientes y generar recetas personalizadas mediante inteligencia artificial. La integración con **OpenRouter (Mistral 7B)** permite obtener recetas detalladas con pasos de preparación adaptadas exactamente a los ingredientes disponibles.

Este proyecto fue desarrollado como trabajo académico para la asignatura de Tecnologías Web, demostrando competencias en desarrollo full-stack, autenticación segura, integración de LLMs y buenas prácticas de ingeniería de software.

---

## Características

- 🔐 **Autenticación JWT** — Registro e inicio de sesión seguro con tokens de acceso.
- 🥕 **Gestión de inventario** — CRUD completo de ingredientes con cantidades.
- 🤖 **Generación de recetas con IA** — Recetas creadas por Mistral 7B (vía OpenRouter) basadas en los ingredientes del usuario.
- ⭐ **Sistema de calificaciones** — Los usuarios pueden calificar y comentar recetas generadas.
- 🖥️ **Interfaz web** — Plantillas HTML renderizadas con Jinja2.
- 🐳 **Containerización** — Despliegue completo con Docker y docker-compose.
- ✅ **Suite de pruebas** — 25 tests automatizados con pytest y SQLite en memoria.

---

## Arquitectura

```
Cliente (Navegador)
       │
       ▼
 FastAPI (Backend)
  ├── Rutas / Controllers
  ├── Servicios (lógica de negocio)
  ├── Modelos SQLAlchemy
  └── Integración OpenRouter API
       │
       ├──► MySQL (Producción)
       └──► SQLite  (Tests)
```

El backend sigue un patrón por capas: los **routers** reciben las peticiones HTTP, los **servicios** contienen la lógica de negocio y los **modelos** gestionan la persistencia a través de SQLAlchemy.

---

## Tecnologías

| Capa | Tecnología |
|------|-----------|
| Backend | Python 3.11+, FastAPI |
| ORM | SQLAlchemy |
| Base de datos (prod) | MySQL 8 |
| Base de datos (test) | SQLite (en memoria) |
| Autenticación | JWT (python-jose), bcrypt 4.0.1 |
| Frontend | Jinja2 (HTML templates) |
| LLM | OpenRouter API — Mistral 7B |
| Contenedores | Docker, docker-compose |
| Testing | pytest, httpx |

---

## Estructura del Proyecto

```
proyecto-recetas/
├── app/
│   ├── main.py                 # Punto de entrada de la aplicación
│   ├── database.py             # Configuración de la base de datos
│   ├── models.py               # Modelos SQLAlchemy
│   ├── schemas.py              # Schemas Pydantic
│   ├── auth.py                 # Lógica de autenticación JWT
│   ├── routers/
│   │   ├── usuarios.py         # Endpoints de autenticación
│   │   ├── ingredientes.py     # Endpoints de inventario
│   │   ├── recetas.py          # Endpoints de generación de recetas
│   │   └── calificaciones.py   # Endpoints de calificaciones
│   ├── services/
│   │   └── llm_service.py      # Integración con OpenRouter/Mistral
│   └── templates/              # Plantillas Jinja2
│       ├── base.html
│       ├── login.html
│       ├── registro.html
│       ├── inventario.html
│       └── recetas.html
├── tests/
│   ├── conftest.py             # Fixtures de pytest (SQLite)
│   ├── test_usuarios.py
│   ├── test_ingredientes.py
│   ├── test_recetas.py
│   └── test_calificaciones.py
├── .env.example                # Plantilla de variables de entorno
├── docker-compose.yml
├── Dockerfile
└── requirements.txt
```

---

## Diagrama Entidad-Relación

El sistema maneja cuatro entidades principales:

```
usuarios (1) ──────────────────── (N) ingredientes
    │                                    nombre
    │  nombre                            cantidad
    │  correo                            usuario_id
    │  contrasena_hash                   creado_en
    │  creado_en
    │
    │ (1)
    │
    ▼ (N)
recetas ──────────────── (1:1) calificaciones
    nombre_plato                  estrellas
    ingredientes_json             comentario
    pasos_preparacion             usuario_id
    usuario_id                    receta_id
    creado_en                     creado_en
```

> **Notas de cardinalidad:**
> - `usuarios → recetas`: 1:N — un usuario puede tener muchas recetas.
> - `recetas → calificaciones`: 1:1 — cada receta tiene como máximo una calificación (`uselist=False`).
> - `usuarios → calificaciones`: 1:N — un usuario puede calificar múltiples recetas.

---

## Requisitos Previos

- Python 3.11 o superior
- Docker y docker-compose (para despliegue containerizado)
- MySQL 8+ (si se ejecuta sin Docker)
- Cuenta en [OpenRouter](https://openrouter.ai/) para la API key del LLM

---

## Instalación y Configuración

### Opción A — Con Docker (recomendado)

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/proyecto-recetas.git
cd proyecto-recetas

# 2. Copiar y configurar las variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 3. Levantar los servicios
docker-compose up --build
```

La aplicación estará disponible en `http://localhost:8000`.

---

### Opción B — Entorno local

```bash
# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/proyecto-recetas.git
cd proyecto-recetas

# 2. Crear y activar entorno virtual
python -m venv venv
source venv/bin/activate        # Linux/macOS
venv\Scripts\activate           # Windows

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales

# 5. Ejecutar la aplicación
uvicorn app.main:app --reload
```

> ⚠️ **Nota importante:** Este proyecto requiere `bcrypt==4.0.1` de forma fija en `requirements.txt` para evitar incompatibilidades de versión con `passlib`. No actualices esta dependencia sin verificar compatibilidad.

---

## Variables de Entorno

Crea un archivo `.env` en la raíz del proyecto basado en `.env.example`:

```env
# Base de datos
DATABASE_URL=mysql+pymysql://usuario:contraseña@localhost:3306/recetas_db

# Seguridad JWT
SECRET_KEY=tu_clave_secreta_muy_larga_y_aleatoria
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# OpenRouter / LLM
OPENROUTER_API_KEY=sk-or-v1-...
OPENROUTER_MODEL=mistralai/mistral-7b-instruct
```

---

## Uso

Una vez levantada la aplicación:

1. **Regístrate** en `/registro` con tu nombre, correo y contraseña.
2. **Inicia sesión** en `/login` para obtener tu token de acceso.
3. **Agrega ingredientes** a tu inventario en `/ingredientes`.
4. **Genera una receta** en `/recetas` — la IA analizará tu inventario y creará una receta personalizada.
5. **Califica la receta** con estrellas y un comentario opcional.

La documentación interactiva de la API está disponible en:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

---

## Endpoints de la API

### Autenticación

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/usuarios/registro` | Registrar nuevo usuario |
| `POST` | `/api/usuarios/login` | Iniciar sesión (retorna JWT) |
| `GET` | `/api/usuarios/me` | Perfil del usuario autenticado |

### Ingredientes

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `GET` | `/api/ingredientes/` | Listar ingredientes del usuario |
| `POST` | `/api/ingredientes/` | Agregar ingrediente |
| `PUT` | `/api/ingredientes/{id}` | Actualizar ingrediente |
| `DELETE` | `/api/ingredientes/{id}` | Eliminar ingrediente |

### Recetas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/recetas/generar` | Generar receta con IA |
| `GET` | `/api/recetas/` | Listar recetas del usuario |
| `GET` | `/api/recetas/{id}` | Detalle de una receta |
| `DELETE` | `/api/recetas/{id}` | Eliminar receta |

### Calificaciones

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| `POST` | `/api/calificaciones/` | Calificar una receta |
| `GET` | `/api/calificaciones/{receta_id}` | Ver calificación de una receta |
| `PUT` | `/api/calificaciones/{receta_id}` | Actualizar calificación |

Todos los endpoints (excepto registro y login) requieren el header:
```
Authorization: Bearer <token>
```

---

## Pruebas

El proyecto incluye **25 tests automatizados** que se ejecutan sobre una base de datos SQLite en memoria, sin necesidad de tener MySQL instalado.

```bash
# Ejecutar todos los tests
pytest

# Con reporte de cobertura
pytest --cov=app --cov-report=term-missing

# Tests de un módulo específico
pytest tests/test_recetas.py -v
```

Los tests cubren:
- Registro e inicio de sesión de usuarios
- Operaciones CRUD de ingredientes
- Generación y eliminación de recetas (con mock del LLM)
- Sistema de calificaciones
- Manejo de errores y validaciones

---

## Despliegue con Docker

El `docker-compose.yml` levanta dos servicios:

```yaml
services:
  db:        # MySQL 8 con volumen persistente
  web:       # FastAPI con uvicorn
```

```bash
# Producción
docker-compose up -d

# Ver logs
docker-compose logs -f web

# Detener servicios
docker-compose down

# Detener y eliminar volúmenes (reset de DB)
docker-compose down -v
```

---

## Contribución

Este proyecto es de carácter académico. Si deseas proponer mejoras:

1. Haz un fork del repositorio.
2. Crea una rama descriptiva: `git checkout -b feature/nombre-mejora`
3. Realiza tus cambios y haz commit: `git commit -m "feat: descripción del cambio"`
4. Abre un Pull Request con una descripción clara.

---

<div align="center">

Desarrollado con ❤️ como proyecto académico — Tecnologías Web

</div>
