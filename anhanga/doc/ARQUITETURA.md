# Arquitetura do Sistema - ANHANGÁ

## 🏗️ Visão Geral da Arquitetura

```
┌─────────────────────────────────────────────────────────────────┐
│                        CLIENTE (Browser)                         │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐         │
│  │  mapa.html   │  │ reportar.html│  │  perfil.html │         │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘         │
│         │                 │                 │                  │
│  ┌──────────────────────────────────────────────────┐         │
│  │              JavaScript (ES6+)                   │         │
│  │  ┌─────────────┐  ┌─────────────┐  ┌──────────┐ │         │
│  │   Leaflet   │  │    Fetch    │  │LocalStorage│         │
│  │   (Mapas)   │  │   (API)     │  │ (Auth)   │ │         │
│  │  └─────────────┘  └─────────────┘  └──────────┘ │         │
│  │  ┌─────────────┐  ┌──────────────────────────┐ │         │
│  │  │ TensorFlow  │  │   Teachable Machine    │ │         │
│  │  │    .js      │  │    (Modelos de IA)     │ │         │
│  │  └─────────────┘  └──────────────────────────┘ │         │
│  └───────────────────────┬──────────────────────────┘         │
└──────────────────────────┼────────────────────────────────────┘
                           │ HTTP/JSON
┌──────────────────────────┼────────────────────────────────────┐
│                      SERVIDOR                                  │
│  ┌───────────────────────┴──────────────────┐                  │
│  │           Flask Application             │                  │
│  │              (Porta 5000)               │                  │
│  │  ┌─────────────────────────────────────┐│                  │
│  │  │           Blueprints                ││                  │
│  │  │  ┌──────────┐ ┌──────────┐         ││                  │
│  │  │  │  Routes  │ │   API    │         ││                  │
│  │  │  │ (Views)  │ │(Endpoints)│        ││                  │
│  │  │  └────┬─────┘ └────┬─────┘         ││                  │
│  │  └───────┼──────────┼───────────────││                  │
│  │          │          │                 ││                  │
│  │  ┌───────┴──────────┴───────────────┐││                  │
│  │  │        SQLAlchemy ORM             │││                  │
│  │  │        ┌──────────┐              │││                  │
│  │  │        │  Models  │              │││                  │
│  │  │        └────┬─────┘              │││                  │
│  │  └─────────────┼────────────────────│││                  │
│  └───────────────┼──────────────────────┘│                  │
│                  │                       │                  │
│  ┌───────────────┴───────────────────────┴──────────┐        │
│  │              SQLite Database                    │        │
│  │  (instance/app.db)                              │        │
│  └─────────────────────────────────────────────────┘        │
│                                                              │
│  ┌─────────────────────────────────────────────────────────┐ │
│  │               External APIs                            │ │
│  │  ┌───────────┐  ┌───────────┐  ┌───────────┐          │ │
│  │  │NASA FIRMS│  │    GFW    │  │Teachable  │          │ │
│  │  │(Fires)   │  │(Deforest) │  │  Machine  │          │ │
│  │  └───────────┘  └───────────┘  └───────────┘          │ │
│  └─────────────────────────────────────────────────────────┘ │
└────────────────────────────────────────────────────────────────┘
```

---

## Padrão Arquitetural

### MVC Simplificado

```
┌─────────────────────────────────────┐
│            Model (Models)            │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │  User   │ │ Report  │ │  Token │ │
│  └─────────┘ └─────────┘ └────────┘ │
│       ↓                               │
│  SQLAlchemy ORM                       │
│       ↓                               │
│  SQLite Database                      │
└─────────────────────────────────────┘
            ↑↓
┌─────────────────────────────────────┐
│          View (Templates)            │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │  mapa   │ │ login   │ │perfil  │ │
│  │ .html   │ │ .html   │ │.html   │ │
│  └─────────┘ └─────────┘ └────────┘ │
│  (Jinja2 + TailwindCSS)             │
└─────────────────────────────────────┘
            ↑↓
┌─────────────────────────────────────┐
│       Controller (Routes)          │
│  ┌─────────┐ ┌─────────┐ ┌────────┐ │
│  │  Auth   │ │ Alerts  │ │ Reports│ │
│  │ Routes  │ │ Routes  │ │ Routes │ │
│  └─────────┘ └─────────┘ └────────┘ │
│  (Flask Blueprints)                 │
└─────────────────────────────────────┘
```

---

## Camadas do Sistema

### 1. Apresentação (Presentation Layer)

**Arquivos**: `app/templates/*.html`

| Componente | Tecnologia | Responsabilidade |
|------------|------------|------------------|
| Estrutura | HTML5 | Semântica e acessibilidade |
| Estilos | TailwindCSS (CDN) | Design responsivo e temas |
| Ícones | Material Symbols | Interface visual |
| Lógica | JavaScript ES6+ | Interatividade |
| Mapas | Leaflet.js | Visualização geoespacial |
| IA | TensorFlow.js | Classificação de imagem |
| ML | Teachable Machine | Modelos treináveis |

**Características**:
- SPA-like (Single Page Application) sem framework JS
- Comunicação via Fetch API
- Estado no localStorage (token)
- Sem SSR (Server-Side Rendering)

---

### 2. Aplicação (Application Layer)

**Arquivos**: `app/routes.py`, `app/__init__.py`

| Componente | Tecnologia | Responsabilidade |
|------------|------------|------------------|
| Framework | Flask | Roteamento e requisições |
| BluePrints | Flask Blueprint | Modularização de rotas |
| CORS | flask-cors | Permissões cross-origin |
| Sessão | localStorage (cliente) | Estado de autenticação |

**Endpoints Principais**:
```
/api/auth/*         → Autenticação
/api/user/*         → Perfil e usuários
/api/alertas/*      → Alertas FIRMS/GFW
/api/reportar/*     → Reportes comunitários
```

---

### 3. Domínio (Domain Layer)

**Arquivos**: `database.py`, `app/models.py`

| Entidade | Atributos Principais |
|----------|---------------------|
| User | username, name, email, password_hash, user_type, data_nasc, telefone, foto_url |
| Report | lat, lon, nivel, count, is_confirmation, created_at |
| AuthToken | token, username, created_at |
| ActivityLog | username, action, details, ip_address, created_at |

**Regras de Negócio**:
- Classificação de reportes (alerta→suspeito→confirmado)
- Tipos de usuário (0=pendente, 1=ativo, 2=especial)
- Fluxo de aprovação de usuários (pendente→ativo→especial)
- Validação de coordenadas (Amazônia apenas)
- Log de atividades (login, logout, reportes)

---

### 4. Infraestrutura (Infrastructure Layer)

**Banco de Dados**:
- SQLite (desenvolvimento)
- SQLAlchemy ORM (abstração)

**APIs Externas**:
```
NASA FIRMS → firms_alerts.py → fetch_firms_alerts()
GFW        → gfw_alerts.py   → get_alerts_amazon()
```

**Arquivos Estáticos**:
- `uploads/` → Fotos de reportes
- `instance/` → Banco SQLite
- `models/` → Modelos Teachable Machine (model.json, weights.bin, metadata.json)

---

## Fluxo de Dados

### Cenário 1: Login com Validação e Log

```
Usuário
   ↓ (POST /api/auth/login)
Flask Routes
   ↓ (valida credenciais)
SQLAlchemy
   ↓ (SELECT users)
SQLite
   ↓ (retorna dados)
SQLAlchemy
   ↓ (verifica user_type != 0)
Flask Routes
   ↓ (gera token)
SQLAlchemy
   ↓ (INSERT activity_logs: login)
SQLite
   ↓ (salva log)
Flask Routes
   ↓ (JSON: {token, user})
JavaScript
   ↓ (localStorage.setItem)
Browser
```

### Cenário 2: Carregar Mapa

```
Usuário clica "Atualizar"
   ↓
JavaScript (fetch)
   ↓ (GET /api/alertas/mapa?days=7)
Flask Routes
   ↓ (chama integrações)
firms_alerts.py + gfw_alerts.py
   ↓ (requests HTTP)
NASA FIRMS API + GFW API
   ↓ (JSON GeoJSON)
Integrações
   ↓ (normaliza dados)
Flask Routes
   ↓ (JSON)
JavaScript
   ↓ (Leaflet.js)
Mapa renderizado
```

### Cenário 3: Monitoramento Admin - Usuários Online
```
Admin abre painel
   ↓
JavaScript (fetch)
   ↓ (GET /api/admin/online-users)
Flask Routes
   ↓ (verifica username="admin")
SQLAlchemy
   ↓ (SELECT auth_tokens + activity_logs)
SQLite
   ↓ (retorna usuários com token recente)
SQLAlchemy
   ↓ (exclui logouts recentes)
Flask Routes
   ↓ (JSON: {users, count})
JavaScript
   ↓ (renderiza lista com fotos)
Painel Admin
```

### Cenário 4: Análise de Câmera com IA
```
Usuário clica "Iniciar Câmera"
   ↓
JavaScript (getUserMedia)
   ↓
Acesso ao dispositivo de vídeo
   ↓
Captura frame → Canvas
   ↓
TensorFlow.js (model.predict)
   ↓
Classificação (queimada/floresta/etc)
   ↓
Atualização da UI com resultado
   ↓
Overlay visual no vídeo
```

### Cenário 4: Reportar Queimada

```
Usuário preenche formulário
   ↓
JavaScript (FormData)
   ↓ (POST /api/reportar/queimada)
Flask Routes
   ↓ (valida e conta próximos)
SQLAlchemy
   ↓ (INSERT + SELECT count)
SQLite
   ↓ (confirma)
SQLAlchemy
   ↓ (retorna nível)
Flask Routes
   ↓ (JSON: {nivel, count})
JavaScript
   ↓ (atualiza mapa)
Usuário vê confirmação
```

---

## Stack Tecnológico

### Backend

| Componente | Versão | Uso |
|------------|--------|-----|
| Python | 3.12+ | Linguagem principal |
| Flask | 3.1.3 | Framework web |
| Flask-SQLAlchemy | 3.1.1 | ORM |
| SQLAlchemy | 2.0+ | Abstração BD |
| python-dotenv | 1.0+ | Variáveis ambiente |
| requests | 2.32.3 | Chamadas HTTP |
| flask-cors | 4.0+ | CORS headers |

### Frontend

| Componente | Versão | Uso |
|------------|--------|-----|
| HTML5 | - | Estrutura |
| TailwindCSS | 3.4+ (CDN) | CSS utility |
| JavaScript | ES6+ | Lógica cliente |
| Leaflet | 1.9+ | Mapas |
| Material Symbols | - | Ícones |
| Chart.js | 4.4+ (CDN) | Gráficos (insights) |
| TensorFlow.js | 4.x | Classificação de imagem |
| Teachable Machine | latest | Modelos customizados |

### Ferramentas

| Ferramenta | Uso |
|------------|-----|
| Git | Versionamento |
| VS Code | IDE |
| SQLite Browser | Visualização BD |
| Postman/Insomnia | Teste de APIs |

---

## Estrutura de Diretórios

```
ANHANGA/
├── app/                          # Aplicação Flask
│   ├── __init__.py              # Factory app
│   ├── models.py                # Modelos SQLAlchemy
│   ├── routes.py                # Rotas e APIs
│   └── templates/               # Views HTML
│       ├── admin.html           # Painel admin
│       ├── index.html           # Landing
│       ├── insights.html        # Dashboard
│       ├── login.html           # Auth
│       ├── mapa.html            # Mapa principal
│       ├── monitoramento.html   # Monitor real-time
│       ├── perfil.html          # Perfil usuário
│       ├── register.html        # Cadastro
│       └── reportar.html        # Reporte
│
├── instance/                    # Dados voláteis
│   └── app.db                   # SQLite
│
├── uploads/                     # Arquivos (fotos)
│   └── *.jpg, *.png
│
├── venv/                        # Ambiente virtual
│
├── config.py                    # Config Flask
├── database.py                  # Modelos ORM (shared)
├── firms_alerts.py             # API NASA
├── gfw_alerts.py               # API GFW
├── seed.py                     # Dados iniciais
├── app.py                      # Entry point
├── requirements.txt            # Dependências
├── .env                        # Secrets (não commitar)
│
└── docs/                       # Documentação
    ├── README.md
    ├── REQUISITOS.md
    ├── REGRAS_NEGOCIO.md
    ├── SEGURANCA.md
    ├── BANCO_DADOS.md
    └── ARQUITETURA.md
```

---

## Padrões de Projeto

### 1. Repository Pattern
```python
# database.py
class UserRepository:
    def get_by_id(self, id): ...
    def create(self, data): ...
    def update(self, id, data): ...
    def delete(self, id): ...
```

### 2. Factory Pattern
```python
# app/__init__.py
def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    db.init_app(app)
    return app
```

### 3. Blueprint Pattern
```python
# app/routes.py
bp = Blueprint('main', __name__)

@bp.route('/api/endpoint')
def endpoint(): ...

# app/__init__.py
app.register_blueprint(bp)
```

---

## Fluxo de Deploy

### Desenvolvimento
```bash
# 1. Clone
git clone <repo>
cd anhanga

# 2. Ambiente
python -m venv venv
venv\Scripts\activate

# 3. Dependências
pip install -r requirements.txt

# 4. Configuração
cp .env.example .env
# editar .env

# 5. Banco
python seed.py

# 6. Executar
python app.py
# Acesse: http://localhost:5000
```

### Produção (Recomendado)
```bash
# 1. Variáveis de ambiente
export FLASK_ENV=production
export SECRET_KEY=<chave_secreta>

# 2. WSGI Server
gunicorn -w 4 -b 0.0.0.0:5000 "app:create_app()"

# 3. HTTPS com Certificado Auto-Assinado
# Para desenvolvimento em rede local:
python run_https.py

# 4. Reverse Proxy (Nginx)
server {
    listen 80;
    server_name anhanga.com;
    
    location / {
        proxy_pass http://127.0.0.1:5000;
        proxy_set_header Host $host;
    }
}

# 4. HTTPS (Let's Encrypt)
certbot --nginx -d anhanga.com
```

---

## 📊 Diagrama de Sequência - Reporte

```
┌─────────┐    ┌──────────┐    ┌─────────┐    ┌──────────┐    ┌────────┐
│ Usuário │    │ Frontend │    │  Flask  │    │ SQLAlchemy│    │SQLite  │
└────┬────┘    └────┬─────┘    └────┬────┘    └────┬─────┘    └───┬────┘
     │              │               │               │              │
     │ ────────────>│               │               │              │
     │  Preenche     │               │               │              │
     │  formulário   │               │               │              │
     │              │               │               │              │
     │              │ ─────────────>│               │              │
     │              │  POST /report │               │              │
     │              │  + FormData   │               │              │
     │              │               │               │              │
     │              │               │ ─────────────>│              │
     │              │               │  Query próximos│              │
     │              │               │               │              │
     │              │               │               │ ────────────>│
     │              │               │               │  SELECT count│
     │              │               │               │ <────────────│
     │              │               │               │              │
     │              │               │ <─────────────│              │
     │              │               │  Retorna count│              │
     │              │               │               │              │
     │              │               │ ─────────────>│              │
     │              │               │  INSERT report│              │
     │              │               │               │              │
     │              │               │               │ ────────────>│
     │              │               │               │  INSERT      │
     │              │               │               │ <────────────│
     │              │               │               │              │
     │              │               │ <─────────────│              │
     │              │               │  Confirmação  │              │
     │              │               │               │              │
     │              │ <─────────────│               │              │
     │              │  JSON {nivel, │               │              │
     │              │  count}       │               │              │
     │              │               │               │              │
     │ <────────────│               │               │              │
     │  Exibe confir-│               │               │              │
     │  mação        │               │               │              │
     │              │               │               │              │
```

---

## 🔧 Configurações

### config.py
```python
class Config:
    SECRET_KEY = os.getenv('SECRET_KEY', 'dev-secret')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///instance/app.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False

class DevelopmentConfig(Config):
    DEBUG = True

class ProductionConfig(Config):
    DEBUG = False
    # SECRET_KEY deve vir de variável ambiente
```

### .env (exemplo)
```bash
# Flask
SECRET_KEY=super-secret-key-here
FLASK_ENV=development

# APIs
GFW_API_TOKEN=your_gfw_token_here
FIRMS_API_KEY=your_firms_key_here

# Banco (opcional)
DATABASE_URL=sqlite:///instance/app.db
```

---

## 📈 Escalabilidade

### Limites Atuais (SQLite)
- Usuários: ~10,000
- Concorrência: Leitura alta, escrita baixa
- Tamanho: ~1GB (incluindo fotos)

### Migração Futura
```
SQLite → PostgreSQL (banco)
Single → Gunicorn + Nginx (servidor)
Local → CDN (assets)
```

---

## 🎓 Decisões Arquiteturais

### Por que Flask?
- Leve e flexível
- Ótimo para MVPs e protótipos
- Ecossistema Python maduro

### Por que SQLite?
- Zero configuração
- Portátil (single file)
- Adequado para < 100k usuários

### Por que não React/Vue?
- Overkill para o escopo
- Server-side rendering com Jinja2
- Menos complexidade

### Por que Leaflet?
- Open source
- Leve (~40KB)
- API intuitiva
- Excelente documentação
