# Checklist de Endpoints - Anhangua API

## Base URL
- FastAPI: `http://127.0.0.1:8000`
- Flask: `http://127.0.0.1:5000`

---

## AUTHENTICAÇÃO

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| POST | `/auth/login` | Login de usuário (retorna token) | ✅ SQLite |
| POST | `/auth/login-test` | Endpoint de teste (mesmo que login) | ✅ SQLite |
| POST | `/auth/register` | Cadastro de novo usuário | ✅ SQLite |
| GET | `/auth/me` | Retorna dados do usuário logado | ✅ SQLite |
| POST | `/auth/logout` | Invalida o token atual | ✅ SQLite |

**Payloads:**
```json
// POST /auth/login
{"username": "admin", "password": "123456"}

// POST /auth/register  
{"name": "João Silva", "username": "joao", "password": "senha123"}

// Headers para endpoints protegidos
Authorization: Bearer <token>
```

---

## ALERTAS (Dados de APIs Externas)

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| GET | `/alertas/tile` | Alertas GFW por tile (lat/lng/zoom) | ⚠️ Stub |
| GET | `/alertas/amazonas` | Alertas GFW para Amazônia (últimos N dias) | ⚠️ Stub |
| GET | `/alertas/amazonas.geojson` | Alertas GFW em formato GeoJSON | ⚠️ Stub |
| GET | `/alertas/amazonas/clusterizado` | Alertas GFW clusterizados | ⚠️ Stub |
| GET | `/alertas/landsat` | Dados Landsat (focos de calor) | ⚠️ Stub |
| GET | `/alertas/firms` | Dados FIRMS (focos de calor) | ⚠️ Stub |
| GET | `/alertas/bbox` | Alertos filtrados por bounding box | ⚠️ Stub |

**Parâmetros comuns:**
- `days=14` - Últimos N dias
- `confidence=high` - Filtro de confiança (low/medium/high)
- `bbox=-60.0,-3.0,-59.0,-2.0` - Bounding box (minLon,minLat,maxLon,maxLat)
- `limit=1000` - Limite de resultados

---

## MAPA (Alertas Agregados)

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| GET | `/alertas/mapa` | Alertas para renderização no mapa (GeoJSON) | ⚠️ Stub |
| GET | `/alertas/mapa/clusters` | Clusters de alertas para mapa | ⚠️ Stub |
| GET | `/alertas/unificado` | Alertas unificados (GFW + FIRMS + Landsat) | ⚠️ Stub |

**Parâmetros:**
- `days=14`
- `confidence=high`
- `start_date=2024-01-01`
- `end_date=2024-01-31`
- `limit=1000`
- `eps_km=1.0` - Raio do cluster em km
- `min_samples=1` - Mínimo de pontos por cluster

---

## REPORTES (CRUD em SQLite)

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| POST | `/reportar/queimada` | Criar novo reporte de queimada | ✅ SQLite |
| GET | `/reportar/lista` | Listar reportes recentes | ✅ SQLite |

**POST `/reportar/queimada`:**
- Query params: `lat`, `lon`
- Form-data: `file` (imagem opcional)
- Header: `Authorization: Bearer <token>` (opcional)
- Retorna: nível (alerta/suspeito/confirmado) baseado em reportes próximos

**GET `/reportar/lista`:**
- Query params: `limit=50`
- Retorna lista com timestamp, localização, usuário, nível

---

## TEMPLATES (Flask - Porta 5000)

| Método | Endpoint | Template | Descrição |
|--------|----------|----------|-----------|
| GET | `/` | `index.html` | Redireciona para login |
| GET | `/login.html` | `login.html` | Página de login |
| GET | `/register.html` | `register.html` | Página de cadastro |
| GET | `/mapa.html` | `mapa.html` | Mapa de alertas |
| GET | `/monitoramento.html` | `monitoramento.html` | Dashboard |
| GET | `/filtros.html` | `mapa.html` | Filtros (redireciona) |
| GET | `/insights.html` | `insights.html` | Insights/relatórios |
| GET | `/reportar.html` | `reportar.html` | Formulário de reporte |

---

## Banco de Dados SQLite

**Tabelas:**
- `users` - Usuários cadastrados (id, username, email, name, password_hash, created_at)
- `auth_tokens` - Tokens ativos (id, token, username, name, created_at, expires_at)
- `reports` - Reportes de queimada (id, lat, lon, user_id, username, filename, nivel, count, created_at)

**Local:** `instance/app.db`

---

## Legenda

- ✅ SQLite - Persiste no banco SQLite
- ⚠️ Stub - Retorna dados de exemplo (implementar APIs reais)
- 🔴 Não implementado

---

## Comandos para Testar

```bash
# Ativar venv
.\venv\Scripts\Activate.ps1

# Iniciar servidor
python app.py

# Testar login
curl -X POST http://127.0.0.1:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"username":"admin","password":"123456"}'

# Testar registro
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Teste","username":"teste","password":"senha123"}'

# Testar reporte (com token)
curl -X POST "http://127.0.0.1:8000/reportar/queimada?lat=-3.0&lon=-60.0" \
  -H "Authorization: Bearer <TOKEN>"
```
