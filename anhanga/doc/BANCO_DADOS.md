# Banco de Dados - ANHANGÁ

## 📊 Visão Geral

- **Tipo**: SQLite (relacional)
- **ORM**: SQLAlchemy
- **Arquivo**: `instance/app.db`
- **Local**: Servidor (arquivo local)

---

## Modelo Entidade-Relacionamento

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│     users       │     │  auth_tokens    │     │    reports      │
├─────────────────┤     ├─────────────────┤     ├─────────────────┤
│ PK id           │◄────│ PK id           │     │ PK id           │
│   username      │     │   token         │     │   lat           │
│   name          │     │   username      │────►│   lon           │
│   password_hash │     │   created_at    │     │   user_id       │────┐
│   email         │     └─────────────────┘     │   username      │    │
│   telefone      │                             │   filename      │    │
│   data_nasc     │     ┌─────────────────┐     │   nivel         │    │
│   foto_url      │     │  activity_logs  │     │   count         │    │
│   user_type     │     ├─────────────────┤     │   is_conf.      │    │
│   created_at    │     │ PK id           │     │   created_at    │    │
└─────────────────┘     │   username      │◄────┘                  │    │
                        │   action        │     └──────────────────┘    │
                        │   details       │                             │
                        │   ip_address    │                             │
                        │   user_agent    │                             │
                        │   created_at    │                             │
                        └─────────────────┘                             │
                                                                        │
┌─────────────────┐                                                      │
│  report_votes   │◄─────────────────────────────────────────────────────┘
├─────────────────┤
│ PK id           │
│   report_id     │
│   user_id       │
│   vote_type     │
│   created_at    │
└─────────────────┘
```

---

## Entidades

### 1. users
Tabela principal de usuários do sistema.

| Campo | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| **id** | INTEGER | Identificador único | PK, AUTOINCREMENT |
| **username** | VARCHAR(50) | Nome de usuário | UNIQUE, NOT NULL |
| **name** | VARCHAR(100) | Nome completo | NOT NULL |
| **password_hash** | VARCHAR(255) | Senha (atualmente plain) | NOT NULL |
| **email** | VARCHAR(100) | Email | UNIQUE, NULL |
| **telefone** | VARCHAR(20) | Telefone | NULL |
| **data_nasc** | DATE | Data de nascimento | NULL |
| **foto_url** | TEXT | Foto em base64 | NULL |
| **user_type** | INTEGER | 0=pendente, 1=ativo, 2=especial | DEFAULT 0 |
| **created_at** | DATETIME | Data de criação | DEFAULT now |

**Índices**: `idx_users_username` (UNIQUE)

---

### 2. auth_tokens
Tokens de autenticação ativos.

| Campo | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| **id** | INTEGER | Identificador | PK, AUTOINCREMENT |
| **token** | VARCHAR(100) | Token JWT | UNIQUE, NOT NULL |
| **username** | VARCHAR(50) | Usuário dono | FK → users.username |
| **created_at** | DATETIME | Data de criação | DEFAULT now |

**Índices**: `idx_tokens_token` (UNIQUE), `idx_tokens_username`

---

### 3. reports (reportes de queimada)
Reportes feitos pelos usuários e sistemas externos (ex: TUPA).

| Campo | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| **id** | INTEGER | Identificador | PK, AUTOINCREMENT |
| **lat** | FLOAT | Latitude | NOT NULL |
| **lon** | FLOAT | Longitude | NOT NULL |
| **user_id** | INTEGER | ID do usuário | FK → users.id, NULL |
| **username** | VARCHAR(50) | Username (denormalizado) | NULL |
| **filename** | VARCHAR(255) | Nome do arquivo foto | NULL |
| **nivel** | VARCHAR(20) | alerta/suspeito/confirmado | NOT NULL |
| **count** | INTEGER | Número de reportes no raio | DEFAULT 1 |
| **is_confirmation** | INTEGER | 0=reporte original, 1=confirmação | DEFAULT 0 |
| **fonte** | VARCHAR(50) | Fonte do reporte: comunidade, tupa, etc | NULL |
| **created_at** | DATETIME | Data do reporte | DEFAULT now |

**Índices**: `idx_reports_location` (lat, lon), `idx_reports_nivel`, `idx_reports_created`, `idx_reports_fonte`

---

### 4. activity_logs
Log de atividades dos usuários no sistema.

| Campo | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| **id** | INTEGER | Identificador | PK, AUTOINCREMENT |
| **username** | VARCHAR(80) | Usuário que executou a ação | NOT NULL |
| **action** | VARCHAR(50) | Tipo: login, logout, report_create, etc | NOT NULL |
| **details** | TEXT | Descrição da atividade | NULL |
| **ip_address** | VARCHAR(45) | IP do usuário | NULL |
| **user_agent** | VARCHAR(256) | Browser info | NULL |
| **created_at** | DATETIME | Data da atividade | DEFAULT now |

**Índices**: `idx_activity_username`, `idx_activity_action`, `idx_activity_created`

---

### 5. report_votes (futuro)
Votos/confirmações em reportes.

| Campo | Tipo | Descrição | Restrições |
|-------|------|-----------|------------|
| **id** | INTEGER | Identificador | PK |
| **report_id** | INTEGER | Reporte votado | FK → reports.id |
| **user_id** | INTEGER | Usuário que votou | FK → users.id |
| **vote_type** | VARCHAR(10) | up/down | NOT NULL |
| **created_at** | DATETIME | Data do voto | DEFAULT now |

**Índices**: UNIQUE(report_id, user_id)

---

## Relacionamentos

### users ↔ auth_tokens
- **Tipo**: 1:N (um usuário pode ter vários tokens)
- **Chave**: `auth_tokens.username` → `users.username`
- **Ação ON DELETE**: CASCADE (tokens removidos quando usuário é deletado)

### users ↔ reports
- **Tipo**: 1:N (um usuário pode fazer vários reportes)
- **Chave**: `reports.user_id` → `users.id`
- **Ação ON DELETE**: SET NULL (reportes ficam anônimos se usuário é removido)

### reports ↔ report_votes
- **Tipo**: 1:N (um reporte pode ter vários votos)
- **Chave**: `report_votes.report_id` → `reports.id`
- **Ação ON DELETE**: CASCADE

---

## DDL (Data Definition Language)

```sql
-- Tabela users
CREATE TABLE users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(100) NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    email VARCHAR(100) UNIQUE,
    telefone VARCHAR(20),
    data_nasc DATE,
    foto_url TEXT,
    user_type INTEGER DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE UNIQUE INDEX idx_users_username ON users(username);

-- Tabela auth_tokens
CREATE TABLE auth_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token VARCHAR(100) UNIQUE NOT NULL,
    username VARCHAR(50) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (username) REFERENCES users(username) ON DELETE CASCADE
);

CREATE UNIQUE INDEX idx_tokens_token ON auth_tokens(token);
CREATE INDEX idx_tokens_username ON auth_tokens(username);

-- Tabela reports
CREATE TABLE reports (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    lat FLOAT NOT NULL,
    lon FLOAT NOT NULL,
    user_id INTEGER,
    username VARCHAR(50),
    filename VARCHAR(255),
    nivel VARCHAR(20) NOT NULL,
    count INTEGER DEFAULT 1,
    is_confirmation INTEGER DEFAULT 0,
    fonte VARCHAR(50),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE SET NULL
);

CREATE INDEX idx_reports_location ON reports(lat, lon);
CREATE INDEX idx_reports_nivel ON reports(nivel);
CREATE INDEX idx_reports_created ON reports(created_at);
CREATE INDEX idx_reports_user ON reports(user_id);
CREATE INDEX idx_reports_fonte ON reports(fonte);

-- Tabela activity_logs
CREATE TABLE activity_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username VARCHAR(80) NOT NULL,
    action VARCHAR(50) NOT NULL,
    details TEXT,
    ip_address VARCHAR(45),
    user_agent VARCHAR(256),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_activity_username ON activity_logs(username);
CREATE INDEX idx_activity_action ON activity_logs(action);
CREATE INDEX idx_activity_created ON activity_logs(created_at);

-- Tabela report_votes (futuro)
CREATE TABLE report_votes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    report_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    vote_type VARCHAR(10) NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (report_id) REFERENCES reports(id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE(report_id, user_id)
);
```

---

## 🔄 DML Exemplos

### Inserir Usuário
```sql
INSERT INTO users (username, name, password_hash, email, telefone, data_nasc, foto_url, user_type)
VALUES ('joao.silva', 'João Silva', 'senha12345', 'joao@email.com', '11999999999', '2000-01-01', '', 1); -- Tipo 1 = Ativo
```

### Buscar Usuário com Token
```sql
SELECT u.* 
FROM users u
JOIN auth_tokens t ON u.username = t.username
WHERE t.token = 'abc123...';
```

### Reportes Próximos (1km ~ 0.01 graus)
```sql
SELECT * FROM reports
WHERE lat BETWEEN -3.13 AND -3.11
  AND lon BETWEEN -60.58 AND -60.56
  AND nivel IN ('alerta', 'suspeito', 'confirmado');
```

### Contar Reportes por Nível
```sql
SELECT nivel, COUNT(*) as total
FROM reports
WHERE created_at >= date('now', '-7 days')
GROUP BY nivel;
```

### Top Reportadores
```sql
SELECT username, COUNT(*) as total_reportes
FROM reports
GROUP BY username
ORDER BY total_reportes DESC
LIMIT 10;
```

---

## 📊 Normalização

### 1NF (Primeira Forma Normal)
✅ Todos os campos são atômicos (não há arrays/JSON nos campos principais)

### 2NF (Segunda Forma Normal)
✅ Todas as tabelas têm chave primária simples (id)
✅ Não há dependências parciais

### 3NF (Terceira Forma Normal)
✅ Não há dependências transitivas
✅ `reports.username` é denormalização intencional (performance)

### BCNF (Boyce-Codd)
✅ Todas as dependências funcionais têm superchave à esquerda

---

## 🗃️ Estratégias de Acesso

### Padrão Repository
```python
# database.py - classe de acesso
class UserRepository:
    def get_by_username(self, username):
        return db_session.query(UserORM).filter(
            UserORM.username == username
        ).first()
    
    def create(self, user_data):
        user = UserORM(**user_data)
        db_session.add(user)
        db_session.commit()
        return user
```

### Otimizações
1. **Índices compostos** para consultas frequentes
2. **Paginação** para listas grandes (LIMIT/OFFSET)
3. **Cache de usuários** em memória (para autenticação)

---

## 💾 Backup e Restore

### Backup
```bash
# Manual
cp instance/app.db backup/app_$(date +%Y%m%d_%H%M%S).db

# Automático (cron)
0 2 * * * cp /path/to/instance/app.db /backups/app_$(date +\%Y\%m\%d).db
```

### Restore
```bash
# Parar servidor
pkill -f "python app.py"

# Restaurar
cp backup/app_20240115.db instance/app.db

# Reiniciar
python app.py
```

---

## 📈 Estatísticas e Manutenção

### Análise de Uso
```sql
-- Tamanho das tabelas
SELECT 
    name,
    SUM(pgsize) as size_bytes,
    COUNT(*) as rows
FROM sqlite_dbpage
JOIN sqlite_master ON sqlite_dbpage.pgno = sqlite_master.rootpage
GROUP BY name;

-- Fragmentação (SQLite faz auto-vacuum)
PRAGMA auto_vacuum;
```

### Limpeza (Opcional)
```sql
-- Remover tokens antigos (>30 dias)
DELETE FROM auth_tokens 
WHERE created_at < date('now', '-30 days');

-- Remover reportes antigos (>1 ano)
DELETE FROM reports 
WHERE created_at < date('now', '-1 year');

-- Remover logs antigos (>90 dias)
DELETE FROM activity_logs 
WHERE created_at < date('now', '-90 days');
```

---

## 🚀 Migrações

### Alembic (Recomendado)
```bash
# Inicializar
alembic init alembic

# Criar migração
alembic revision --autogenerate -m "add campo X"

# Aplicar
alembic upgrade head

# Reverter
alembic downgrade -1
```

### Manual (Atual)
Atualmente o sistema recria o banco do zero (dev mode):
1. Deletar `instance/app.db`
2. Executar `python seed.py`

---

## ⚠️ Limitações do SQLite

| Limite | Valor | Impacto |
|--------|-------|---------|
| Tamanho máximo | 281 TB | Não é problema |
| Tabelas por join | 64 | Raro atingir |
| Colunas por tabela | 2000 | Não é problema |
| Concorrência | Leitura simultânea, escrita exclusiva | Bom para leitura |

### Quando Migrar
- > 10.000 usuários ativos simultâneos
- > 1.000.000 de reportes
- Necessidade de replicação
- Requisitos de alta disponibilidade (99.99%)

**Próximo passo**: PostgreSQL + SQLAlchemy (mesma API)
