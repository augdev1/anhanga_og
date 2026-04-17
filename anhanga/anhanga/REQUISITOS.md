# Requisitos do Sistema ANHANGÁ

## 📋 Requisitos Funcionais (RF)

### RF001 - Autenticação de Usuários
- **Descrição**: O sistema deve permitir login de usuários registrados
- **Entrada**: Username e senha
- **Processamento**: Validação no banco de dados
- **Saída**: Token JWT + dados do usuário
- **Prioridade**: Alta

### RF002 - Cadastro de Usuários
- **Descrição**: Permitir novo registro com dados pessoais
- **Campos obrigatórios**: Nome, username, senha
- **Campos opcionais**: Email, telefone, data de nascimento, foto
- **Validações**: Username único, senha mínima 6 caracteres
- **Prioridade**: Alta

### RF003 - Gerenciamento de Perfil
- **Descrição**: Usuário pode visualizar e editar seus dados
- **Funcionalidades**:
  - Alterar foto de perfil
  - Atualizar dados pessoais
  - Alterar senha
- **Prioridade**: Média

### RF004 - Visualização de Alertas no Mapa
- **Descrição**: Exibir alertas de queimadas e desmatamento
- **Fontes**: NASA FIRMS, Global Forest Watch
- **Filtros**: Período (7, 14, 30 dias)
- **Região**: Amazônia Legal (fixo)
- **Prioridade**: Alta

### RF005 - Reporte de Queimadas
- **Descrição**: Usuários podem reportar queimadas
- **Campos**: Localização (lat/lon), foto opcional
- **Validação**: Geolocalização ou clique no mapa
- **Prioridade**: Alta

### RF006 - Níveis de Alerta Comunitário
- **Descrição**: Classificação automática baseada em reportes
- **Regras**:
  - 1 reporte → Alerta
  - 2 reportes → Suspeito
  - 3+ reportes → Confirmado
- **Raio de agrupamento**: 1km
- **Prioridade**: Alta

### RF007 - Painel Administrativo
- **Descrição**: Gerenciamento de usuários (apenas admin)
- **Funcionalidades**:
  - Listar todos os usuários
  - Promover/rebaixar tipo de usuário
  - Resetar senhas
- **Prioridade**: Média

### RF008 - Dashboard de Insights
- **Descrição**: Estatísticas e visualizações
- **Métricas**:
  - Total de alertas por fonte
  - Reportes da comunidade
  - Heatmap de ocorrências
- **Prioridade**: Média

### RF009 - Filtros de Alertas
- **Descrição**: Permitir filtrar visualização no mapa
- **Opções**:
  - Por período (dias)
  - Por tipo (queimada/desmatamento)
  - Por fonte (FIRMS/GFW/Comunidade)
- **Prioridade**: Média

### RF010 - Menu de Usuário
- **Descrição**: Dropdown com opções do usuário logado
- **Itens**: Meu Perfil, Painel Admin (se aplicável), Sair
- **Prioridade**: Baixa

---

## 🔧 Requisitos Não Funcionais (RNF)

### RNF001 - Performance
- **Tempo de resposta**: APIs < 3 segundos
- **Carregamento do mapa**: < 5 segundos
- **Limite de alertas**: Máximo 300 por requisição
- **Prioridade**: Alta

### RNF002 - Segurança
- **Autenticação**: JWT com expiração
- **Senhas**: Armazenadas com hash (SHA-256)
- **Proteção**: Todas as páginas internas exigem login
- **Tokens**: 24 caracteres aleatórios
- **Prioridade**: Alta

### RNF003 - Usabilidade
- **Interface**: Responsiva (mobile/desktop)
- **Tema**: Dark mode fixo
- **Idioma**: Português (pt-BR)
- **Acessibilidade**: Contrastes adequados
- **Prioridade**: Média

### RNF004 - Disponibilidade
- **Uptime**: 99% (meta)
- **Fallback**: Dados de exemplo se APIs falharem
- **Cache**: Não implementado (futuro)
- **Prioridade**: Média

### RNF005 - Escalabilidade
- **Usuários simultâneos**: Até 100 (SQLite)
- **Dados**: Rotação de alertas (últimos 30 dias)
- **Imagens**: Base64 no banco (limite 2MB)
- **Prioridade**: Baixa

### RNF006 - Compatibilidade
- **Navegadores**: Chrome, Firefox, Edge, Safari
- **Mobile**: iOS Safari, Chrome Android
- **Resolução mínima**: 360x640 (mobile)
- **Prioridade**: Média

### RNF007 - Manutenibilidade
- **Código**: Modular e documentado
- **Padrão**: MVC simplificado
- **Logs**: Console para debugging
- **Testes**: Não implementado (futuro)
- **Prioridade**: Média

### RNF008 - Confiabilidade
- **Backup**: Copiar arquivo `instance/app.db`
- **Recovery**: Reset via `seed.py`
- **Validação**: Dados de entrada sanitizados
- **Prioridade**: Média

### RNF009 - Integrações
- **FIRMS API**: Timeout 30s, retry 1x
- **GFW API**: Timeout 30s, fallback para dados de exemplo
- **Formato**: GeoJSON para todos os alertas
- **Prioridade**: Alta

### RNF010 - Regulatório
- **LGPD**: Dados pessoais mínimos, opt-in implícito
- **Termos**: Não implementado (futuro)
- **Cookies**: Apenas localStorage para tokens
- **Prioridade**: Baixa

---

## 📊 Matriz de Prioridades

| ID | Requisito | Prioridade | Status |
|----|-----------|------------|--------|
| RF001 | Autenticação | Alta | ✅ Implementado |
| RF002 | Cadastro | Alta | ✅ Implementado |
| RF003 | Perfil | Média | ✅ Implementado |
| RF004 | Mapa de Alertas | Alta | ✅ Implementado |
| RF005 | Reporte | Alta | ✅ Implementado |
| RF006 | Níveis de Alerta | Alta | ✅ Implementado |
| RF007 | Admin | Média | ✅ Implementado |
| RF008 | Insights | Média | ✅ Implementado |
| RF009 | Filtros | Média | ✅ Implementado |
| RF010 | Menu Usuário | Baixa | ✅ Implementado |

---

## 🎯 Critérios de Aceitação

### Gerais
1. Sistema deve funcionar offline com dados de exemplo
2. Todas as funcionalidades devem ser testáveis via API
3. Interface deve ser intuitiva sem necessidade de manual

### Específicos
- **Mapa**: Carregar em < 5s com até 300 marcadores
- **Reporte**: Processar em < 3s incluindo upload de foto
- **Login**: Autenticar em < 2s
- **Cadastro**: Validar e criar em < 3s

---

## 📝 Notas

- Sistema desenvolvido para escala pequena/média
- SQLite adequado para até ~10.000 usuários
- Para escala maior, considerar PostgreSQL + Redis
- APIs externas podem ter limites de requisição (verificar contratos)
