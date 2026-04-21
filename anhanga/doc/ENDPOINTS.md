# Checklist de Endpoints - Anhangua API

## Base URL

| Modo | URL | Uso |
|------|-----|-----|
| HTTP Local | `http://localhost:5000` | Desenvolvimento local (câmera funciona) |
| HTTPS Rede | `https://IP-DO-PC:5000` | Acesso de outros dispositivos (requer `run_https.py`) |

---

## AUTENTICAÇÃO

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| POST | `/auth/register` | Registro de novo usuário | ✅ SQLite |
| POST | `/auth/login` | Login (retorna token JWT) | ✅ SQLite |
| POST | `/auth/logout` | Logout (invalida token) | ✅ SQLite |
| GET | `/auth/me` | Dados do usuário logado | ✅ SQLite |
| POST | `/auth/validate-recovery` | Validar dados para recuperação de senha | ✅ SQLite |
| POST | `/auth/reset-password` | Redefinir senha após validação | ✅ SQLite |

**POST `/auth/register` - Payload:**
```json
{
  "name": "João Silva",
  "username": "joao.silva",
  "email": "joao@email.com",
  "password": "senha12345",
  "data_nasc": "01/01/2000",
  "telefone": "11999999999"
}
```

**POST `/auth/login` - Payload:**
```json
{
  "username": "joao.silva",
  "password": "senha12345"
}
```

**Resposta:**
```json
{
  "status": "ok",
  "token": "abc123...",
  "user": {
    "username": "joao.silva",
    "name": "João Silva",
    "user_type": 1
  }
}
```

**POST `/auth/validate-recovery` - Payload:**
```json
{
  "email": "joao@email.com",
  "nome": "João Silva",
  "data_nasc": "01/01/2000"
}
```

**Resposta:**
```json
{
  "status": "ok",
  "username": "joao.silva"
}
```

**POST `/auth/reset-password` - Payload:**
```json
{
  "username": "joao.silva",
  "new_password": "novasenha123"
}
```

**Resposta:**
```json
{
  "status": "ok",
  "message": "Senha redefinida com sucesso"
}
```

**Notas:**
- Usuários tipo 0 (Pendente) não conseguem fazer login
- Senha mínima: 8 caracteres
- Idade mínima: 12 anos
- Todos os campos são obrigatórios no cadastro
- Recuperação de senha requer email, nome e data de nascimento corretos

---

## ALERTAS (Dados de APIs Externas - Implementados)

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| GET | `/alertas/mapa` | Alertas FIRMS + GFW para mapa (GeoJSON) | ✅ Implementado |
| GET | `/alertas/tile` | Alertas GFW por tile (lat/lng/zoom) | ⚠️ Stub |
| GET | `/alertas/amazonas` | Alertas GFW para Amazônia (últimos N dias) | ⚠️ Stub |
| GET | `/alertas/amazonas.geojson` | Alertas GFW em formato GeoJSON | ⚠️ Stub |
| GET | `/alertas/amazonas/clusterizado` | Alertas GFW clusterizados | ⚠️ Stub |
| GET | `/alertas/landsat` | Dados Landsat (focos de calor) | ⚠️ Stub |
| GET | `/alertas/firms` | Dados FIRMS (focos de calor) | ✅ Implementado |
| GET | `/alertas/bbox` | Alertos filtrados por bounding box | ⚠️ Stub |

**Parâmetros comuns:**
- `days=14` - Últimos N dias
- `confidence=high` - Filtro de confiança (low/medium/high)
- `bbox=-60.0,-3.0,-59.0,-2.0` - Bounding box (minLon,minLat,maxLon,maxLat)
- `limit=1000` - Limite de resultados
- `eps_km=1.0` - Raio do cluster em km (para endpoints clusterizados)
- `min_samples=1` - Mínimo de pontos por cluster

---

## IA / MODELOS (Teachable Machine)

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| GET | `/models/model.json` | Arquivo do modelo TensorFlow.js | ✅ Estático |
| GET | `/models/metadata.json` | Metadados do modelo | ✅ Estático |
| GET | `/models/weights.bin` | Pesos do modelo | ✅ Estático |
| GET | `/models/labels.txt` | Classes do modelo | ✅ Estático |

**Nota**: Modelos são servidos estaticamente de `/models/`. O processamento de IA é feito 100% no cliente (browser) via TensorFlow.js.

---

## REPORTES (CRUD em SQLite)

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| POST | `/reportar/queimada` | Criar novo reporte de queimada | ✅ SQLite |
| POST | `/api/reportes` | Receber reportes externos (TUPA) | ✅ SQLite |
| GET | `/reportar/lista` | Listar reportes recentes | ✅ SQLite |
| GET | `/reportar/queimadas/todos` | Listar todos os reportes | ✅ SQLite |
| GET | `/reportar/queimadas/mapa` | Reportes em formato GeoJSON | ✅ SQLite |

**POST `/api/reportes` - Integração com TUPA:**
- Recebe reportes externos do sistema TUPA
- Não requer autenticação
- Envia notificação para TUPA após salvar (opcional)

**Payload:**
```json
{
  "latitude": -3.119,
  "longitude": -60.021,
  "imagem": "data:image/jpeg;base64,...",  // opcional
  "usuario": "tupa_joao",  // opcional (string ou int)
  "fonte": "tupa",
  "nivel": 1  // 1=alerta, 2=suspeito, 3=confirmado
}
```

**Resposta:**
```json
{"status": "ok"}
```

**POST `/reportar/queimada` - Regras por Tipo de Usuário:**

| Tipo Usuário | Novo Reporte | Confirmação | Raio |
|--------------|--------------|-------------|------|
| **0 (Pendente)** | ❌ Bloqueado | ❌ Bloqueado | - |
| **1 (Ativo)** | ALERTA → SUSPEITO → CONFIRMADO | Incrementa contador | 500m |
| **2 (Especial)** | CONFIRMADO imediato | CONFIRMADO imediato | 500m |

- Query params: `lat`, `lon`
- Form-data: `file` (imagem)
- Header: `Authorization: Bearer <token>`
- Retorna: nível (alerta/suspeito/confirmado)

**Restrições:**
- Cada usuário só pode reportar/confirmar 1 vez por localidade (raio 500m)
- Usuário não pode confirmar próprio reporte
- Usuário tipo 0 (Pendente) recebe erro 403

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
| GET | `/monitoramento.html` | `monitoramento.html` | Análise de câmera com IA |
| GET | `/filtros.html` | `mapa.html` | Filtros (redireciona) |
| GET | `/insights.html` | `insights.html` | Insights/relatórios |
| GET | `/reportar.html` | `reportar.html` | Formulário de reporte |

---

## ADMIN (Gerenciamento - Apenas username="admin")

| Método | Endpoint | Descrição | Status |
|--------|----------|-----------|--------|
| GET | `/admin/users` | Listar todos os usuários | ✅ SQLite |
| POST | `/admin/users/{id}/approve` | Aprovar usuário pendente (0→1) | ✅ SQLite |
| POST | `/admin/users/{id}/promote` | Promover ativo para especial (1→2) | ✅ SQLite |
| POST | `/admin/users/{id}/demote` | Rebaixar especial para ativo (2→1) | ✅ SQLite |
| GET | `/admin/reports` | Listar todos os reportes de queimada | ✅ SQLite |
| DELETE | `/admin/reports/{id}` | Deletar um reporte de queimada | ✅ SQLite |
| GET | `/admin/online-users` | Usuários online (últimos 30min) | ✅ SQLite |
| GET | `/admin/activities` | Atividades recentes do sistema | ✅ SQLite |

**Acesso:** Apenas usuário com `username="admin"` pode acessar

**Respostas:**
```json
// GET /admin/reports
{
  "status": "ok",
  "count": 10,
  "reports": [
    {
      "id": 1,
      "user_id": 2,
      "username": "joao",
      "latitude": -3.119,
      "longitude": -60.021,
      "nivel": "alerta",
      "count": 1,
      "created_at": "2025-01-15T10:30:00",
      "photo_url": "photo123.jpg"
    }
  ]
}

// DELETE /admin/reports/{id}
{
  "status": "ok",
  "message": "Reporte deletado com sucesso"
}

// GET /admin/online-users
{
  "status": "ok",
  "count": 3,
  "users": [
    {
      "username": "joao",
      "name": "João Silva",
      "foto_url": "data:image/jpeg;base64,...",
      "last_activity": "2025-01-15T10:30:00"
    }
  ]
}

// GET /admin/activities
{
  "status": "ok",
  "count": 20,
  "activities": [
    {
      "id": 1,
      "username": "joao",
      "action": "login",
      "details": "Login realizado com sucesso",
      "created_at": "2025-01-15T10:30:00"
    }
  ]
}
```

---

## Banco de Dados SQLite

**Tabelas:**
- `users` - Usuários cadastrados (id, username, email, name, password_hash, user_type, data_nasc, telefone, foto_url, created_at)
- `auth_tokens` - Tokens ativos (id, token, username, name, created_at, expires_at)
- `reports` - Reportes de queimada (id, lat, lon, user_id, username, filename, nivel, count, is_confirmation, created_at)
- `activity_logs` - Log de atividades (id, username, action, details, ip_address, user_agent, created_at)

**Tipos de Usuário (user_type):**
- `0` = Pendente (não pode fazer login)
- `1` = Ativo (pode reportar e usar o sistema)
- `2` = Especial (reportes confirmam imediatamente)

**Local:** `instance/app.db`

---

## Legenda

- ✅ Implementado - Funcionalidade completa
- ✅ Estático - Arquivos servidos diretamente
- ✅ SQLite - Persiste no banco SQLite
- ⚠️ Stub - Retorna dados de exemplo (implementar APIs reais)
- 🔴 Não implementado

---

## Notas Importantes

### HTTPS para Câmera
Para usar a funcionalidade de câmera em dispositivos da rede (não localhost):
1. Use `python run_https.py` para iniciar com SSL
2. Acesse via `https://IP-DO-PC:5000`
3. Aceite o certificado auto-assinado no navegador

Ver documentação completa: [REDE_CAMERA.md](REDE_CAMERA.md)

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

# Testar registro (todos campos obrigatórios)
curl -X POST http://127.0.0.1:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Teste","email":"teste@teste.com","data_nasc":"2000-01-01","telefone":"11999999999","username":"teste","password":"senha12345","foto_url":"data:image/jpeg;base64,AAA"}'

# Testar admin - aprovar usuário
curl -X POST "http://127.0.0.1:5000/api/admin/users/2/approve" \
  -H "Authorization: Bearer <ADMIN_TOKEN>"

# Testar reporte (com token)
curl -X POST "http://127.0.0.1:8000/reportar/queimada?lat=-3.0&lon=-60.0" \
  -H "Authorization: Bearer <TOKEN>"
```
