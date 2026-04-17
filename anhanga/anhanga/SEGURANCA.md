# Segurança - ANHANGÁ

## 🔐 Visão Geral

O sistema ANHANGÁ implementa segurança em múltiplas camadas, desde autenticação até proteção de dados pessoais, seguindo princípios de defesa em profundidade.

---

## 🛡️ Requisitos de Segurança

### RS001 - Autenticação

#### Mecanismo
- **Tipo**: Token-based (JWT simplificado)
- **Geração**: `secrets.token_urlsafe(24)`
- **Armazenamento**: 
  - Cliente: localStorage ("ANHANGA_TOKEN")
  - Servidor: Tabela `auth_tokens` no SQLite
- **Validação**: Bearer token em header HTTP

#### Fluxo
```
1. POST /api/auth/login
2. Servidor valida credenciais
3. Servidor gera token único
4. Retorna token + dados do usuário
5. Cliente armazena no localStorage
6. Requisições subsequentes incluem Authorization: Bearer <token>
```

#### Proteção
- Tokens de 24 caracteres (192 bits de entropia)
- Não há expiração automática (sessão persistente)
- Logout invalida token no cliente (não no servidor)

---

### RS002 - Autorização

#### Níveis de Acesso

| Papel | Valor | Permissões |
|-------|-------|------------|
| **Anônimo** | - | Apenas visualizar login/cadastro |
| **Usuário** | 0 | Mapa, reportar, perfil |
| **Admin** | 1 | Tudo + painel administrativo |

#### Proteção de Rotas
```python
# Frontend (JavaScript)
if (!token) {
    window.location.href = "login.html";
}

# Backend (Flask)
@token_required  # decorador opcional
```

#### Verificações
- Todas as páginas internas verificam token no localStorage
- APIs verificam header Authorization
- Admin pages verificam user_type = 1

---

### RS003 - Senhas

#### Armazenamento
- **Método atual**: Plain text (⚠️ Não recomendado para produção)
- **Campo**: `users.password_hash`
- **Migração recomendada**: bcrypt ou Argon2

#### Requisitos
- Mínimo 6 caracteres
- Sem complexidade obrigatória
- Username + senha devem ser únicos juntos

#### Melhorias Futuras
```python
# Implementar bcrypt
from flask_bcrypt import Bcrypt
bcrypt = Bcrypt(app)

# Hash
password_hash = bcrypt.generate_password_hash(senha).decode('utf-8')

# Verificar
bcrypt.check_password_hash(user.password_hash, senha)
```

---

### RS004 - Proteção contra Ataques Comuns

#### SQL Injection
- **Proteção**: SQLAlchemy ORM (parametrização automática)
- **Uso**: Nunca concatena strings SQL
- **Exemplo seguro**:
```python
db_session.query(UserORM).filter(UserORM.username == username).first()
```

#### XSS (Cross-Site Scripting)
- **Proteção**: Escape automático no Jinja2 (Flask)
- **Cuidados**: Sanitizar dados inseridos no DOM via JS
- **Exemplo**:
```javascript
// Evitar innerHTML com dados de usuário
element.textContent = userInput;  // Seguro
element.innerHTML = userInput;    // Perigoso
```

#### CSRF (Cross-Site Request Forgery)
- **Status**: Não implementado (sessão é token-based)
- **Justificativa**: APIs usam autenticação Bearer, não cookies
- **Risco**: Baixo para este caso de uso

#### Clickjacking
- **Proteção**: X-Frame-Options (pode ser adicionado)
```python
@app.after_request
def after_request(response):
    response.headers['X-Frame-Options'] = 'SAMEORIGIN'
    return response
```

---

### RS005 - Dados Pessoais (LGPD)

#### Coleta Mínima
| Dado | Obrigatório | Uso |
|------|-------------|-----|
| Username | Sim | Identificação |
| Nome | Sim | Display |
| Senha | Sim | Autenticação |
| Email | Não | Contato |
| Telefone | Não | Contato |
| Data nascimento | Não | Perfil |
| Foto | Não | Perfil |
| Localização | Apenas reportes | Geolocalização |

#### Consentimento
- Implícito no uso do sistema
- Termos de uso não implementados (futuro)

#### Retenção
- Dados mantidos indefinidamente
- Usuário pode solicitar exclusão (manual - admin)

#### Compartilhamento
- **Não** compartilhamos dados com terceiros
- APIs externas recebem apenas coordenadas (anônimas)

---

### RS006 - Upload de Arquivos

#### Fotos de Reporte
- **Validação MIME**: Verificar magic bytes
- **Extensões**: .jpg, .jpeg, .png
- **Tamanho**: Máximo 5MB
- **Armazenamento**: Pasta `uploads/` no servidor
- **Renomeação**: Timestamp + random para evitar conflitos

#### Fotos de Perfil
- **Formato**: Base64 (data URL)
- **Tamanho**: Máximo 2MB
- **Armazenamento**: Banco de dados (campo foto_url)
- **Validação**: Verificar prefixo "data:image/"

#### Prevenção
- Não executar arquivos uploadados
- Sanitizar nomes de arquivo
- Limitar total de arquivos por usuário (futuro)

---

### RS007 - Comunicação

#### HTTP vs HTTPS
- **Desenvolvimento**: HTTP (localhost)
- **Produção recomendada**: HTTPS com certificado TLS
- **HSTS**: Adicionar header Strict-Transport-Security

#### CORS (Cross-Origin Resource Sharing)
- **Configuração atual**: Permissivo para desenvolvimento
- **Produção**: Restringir origins permitidos
```python
CORS(app, origins=["https://anhanga.com"])
```

---

### RS008 - Logs e Monitoramento

#### Logs Atuais
- Console do servidor Flask
- Console do browser (cliente)
- Erros de API no terminal

#### Dados Logados
- Tentativas de login (sucesso/falha)
- Erros de API externa
- Stack traces em caso de exceção

#### NÃO Logado
- Senhas (mesmo em hash)
- Tokens completos (apenas partial)
- Dados pessoais sensíveis

#### Melhorias Futuras
- Sistema de logging estruturado (JSON)
- Alertas automáticos para erros críticos
- Dashboard de monitoramento

---

### RS009 - Backup e Recovery

#### Backup do Banco
```bash
# Copiar arquivo SQLite
cp instance/app.db backups/app_$(date +%Y%m%d).db

# Compactar
tar -czf backups/app_$(date +%Y%m%d).tar.gz instance/app.db uploads/
```

#### Recovery
1. Parar servidor
2. Substituir `instance/app.db` pelo backup
3. Reiniciar servidor

#### Frequência Recomendada
- **Banco**: Diário
- **Imagens**: Semanal
- **Retenção**: 30 dias

---

### RS010 - Segurança de APIs Externas

#### NASA FIRMS
- **Chave**: Armazenada em variável de ambiente
- **Uso**: Apenas server-side (nunca exposta ao cliente)
- **Limites**: Respeitar rate limits da API

#### Global Forest Watch
- **Token**: Opcional (alguns endpoints funcionam sem)
- **Armazenamento**: `.env` file (não commitado)

#### Gestão de Secrets
```bash
# .env (não commitar no git)
GFW_API_TOKEN=seu_token_aqui
FIRMS_API_KEY=sua_chave_aqui
SECRET_KEY=chave_secreta_flask
```

---

## 🔒 Checklist de Segurança

### Antes do Deploy
- [ ] Mover SECRET_KEY para variável de ambiente
- [ ] Implementar hash de senhas (bcrypt)
- [ ] Configurar HTTPS
- [ ] Adicionar headers de segurança
- [ ] Revisar CORS origins
- [ ] Configurar backups automáticos
- [ ] Testar proteção de rotas
- [ ] Verificar sanitização de inputs

### Manutenção Regular
- [ ] Atualizar dependências (`pip list --outdated`)
- [ ] Verificar logs por atividades suspeitas
- [ ] Testar restore de backup
- [ ] Revisar permissões de arquivos

---

## ⚠️ Riscos Conhecidos

### Alto
1. **Senhas em plain text** - Implementar hash imediatamente
2. **Tokens sem expiração** - Adicionar TTL de 24h

### Médio
1. **Sem rate limiting** - Adicionar limites por IP/usuário
2. **SQLite em produção** - Migrar para PostgreSQL para escala
3. **Sem HTTPS** - Configurar TLS antes do deploy

### Baixo
1. **Sem 2FA** - Avaliar necessidade
2. **Sem logs estruturados** - Implementar para debugging

---

## 📚 Referências

- [OWASP Top 10](https://owasp.org/www-project-top-ten/)
- [Flask Security](https://flask.palletsprojects.com/en/2.3.x/security/)
- [Python Security](https://python-security.readthedocs.io/)
- [LGPD Guia](https://www.gov.br/lgpd/pt-br)
