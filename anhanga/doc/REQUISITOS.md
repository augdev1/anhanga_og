# Requisitos do Sistema ANHANGÁ

## 📋 Requisitos Funcionais (RF)

### RF001 - Autenticação de Usuários
- **Descrição**: O sistema deve permitir login de usuários registrados
- **Entrada**: Username e senha
- **Processamento**: Validação no banco de dados
- **Saída**: Token JWT + dados do usuário
- **Prioridade**: Alta

### RF002 - Cadastro de Usuários com Validação
- **Descrição**: Permitir novo registro com dados pessoais e validações rigorosas
- **Campos obrigatórios**: Nome, email, data nascimento, telefone, username, senha, foto
- **Validações**:
  - Idade mínima: 12 anos
  - Senha mínima: 8 caracteres
  - Username único (case insensitive)
  - Email único
  - Todos os campos obrigatórios preenchidos
- **Resultado**: Usuário criado com tipo 0 (Pendente) - aguarda aprovação
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

### RF006 - Níveis de Alerta Comunitário por Tipo de Usuário
- **Descrição**: Classificação automática baseada em reportes e tipo de usuário
- **Usuário Tipo 1 (Ativo)**:
  - 1 reporte → Alerta
  - 2 reportes → Suspeito  
  - 3+ reportes → Confirmado
  - Cada usuário só pode reportar/confirmar 1 vez por localidade (500m)
- **Usuário Tipo 2 (Especial)**:
  - Reporte imediato → Confirmado
  - Confirmação imediata → Confirmado
- **Usuário Tipo 0 (Pendente)**: Bloqueado - não pode reportar
- **Raio de agrupamento**: 500m
- **Prioridade**: Alta

### RF007 - Painel Administrativo com Aprovação
- **Descrição**: Gerenciamento completo de usuários (apenas username="admin")
- **Funcionalidades**:
  - Listar usuários por tipo (Pendente/Ativo/Especial)
  - Aprovar usuários pendentes (0 → 1)
  - Promover usuários ativos (1 → 2)
  - Rebaixar usuários especiais (2 → 1)
  - Visualizar estatísticas (Total, Pendentes, Ativos, Especiais)
- **Prioridade**: Alta

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

### RF010 - Análise de Imagem por IA
- **Descrição**: Classificação de imagem via câmera usando IA
- **Fonte**: Teachable Machine (TensorFlow.js)
- **Funcionalidades**:
  - Carregar modelo local (`/models/`) ou via URL
  - Análise contínua ou frame único
  - Detecção de múltiplas classes (queimada, floresta, solo, água, nuvem)
  - Fallback por análise de cores (sem modelo)
- **Prioridade**: Alta

### RF011 - Câmera em Tempo Real
- **Descrição**: Acesso à câmera para análise visual
- **Requisitos**:
  - Suporte a múltiplas câmeras (seletor)
  - Permissões do navegador
  - Overlay visual com resultados
  - Captura de frames
- **Prioridade**: Alta

### RF012 - Menu de Usuário
- **Descrição**: Dropdown com opções do usuário logado
- **Itens**: Meu Perfil, Painel Admin (apenas se username="admin"), Sair
- **Prioridade**: Baixa

### RF013 - Monitoramento de Usuários Online
- **Descrição**: Admin visualiza usuários ativos no sistema
- **Funcionalidades**:
  - Lista de usuários online (últimos 30 minutos)
  - Foto, nome e tempo de atividade
  - Atualização automática a cada 30 segundos
  - Remove usuários que fizeram logout
- **Prioridade**: Média

### RF014 - Log de Atividades
- **Descrição**: Registro de ações dos usuários no sistema
- **Eventos monitorados**:
  - Login/Logout
  - Reportes criados
  - Confirmações de reportes
- **Visualização**: Painel admin mostra atividades recentes com timestamp
- **Prioridade**: Média

### RF015 - Bloqueio de Usuários Pendentes
- **Descrição**: Impedir acesso de usuários não aprovados
- **Regras**:
  - Login bloqueado para tipo 0 (Pendente)
  - Mensagem: "Cadastro pendente de aprovação"
  - Reportes bloqueados para tipo 0
- **Prioridade**: Alta

### RF016 - Gerenciamento de Reportes no Admin
- **Descrição**: Admin pode visualizar e deletar reportes de queimada
- **Funcionalidades**:
  - Listar todos os reportes (alerta, suspeito, confirmado)
  - Visualizar usuário, nível, fonte, data e localização
  - Deletar reportes específicos
  - Ação de deleção registrada no log de atividades
- **Prioridade**: Alta

### RF017 - Integração com Sistemas Externos (TUPA)
- **Descrição**: Receber reportes de sistemas externos via API
- **Endpoint**: POST /api/reportes (sem autenticação)
- **Campos**:
  - latitude, longitude (obrigatórios)
  - imagem (base64, opcional)
  - usuario (string ou int, opcional)
  - fonte (ex: "tupa")
  - nivel (1=alerta, 2=suspeito, 3=confirmado)
- **Funcionalidades**:
  - Salva reporte com campo fonte indicando origem
  - Envia notificação de volta para sistema externo
  - Trata erro se sistema externo não estiver online
- **Campo fonte**: VARCHAR(50) na tabela reports para rastrear origem
- **Prioridade**: Alta

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
- **Navegadores**: Chrome, Firefox, Edge, Safari (com suporte a getUserMedia)
- **Mobile**: iOS Safari, Chrome Android
- **Resolução mínima**: 360x640 (mobile)
- **Câmera**: HTTPS obrigatório para IPs não-localhost
- **Prioridade**: Média

### RNF011 - HTTPS para Câmera
- **Descrição**: Navegadores exigem conexão segura para MediaDevices API
- **Soluções**:
  - Desenvolvimento: `http://localhost:5000` (funciona)
  - Rede local: `https://IP:5000` com certificado auto-assinado
  - Produção: HTTPS com certificado válido (Let's Encrypt)
- **Implementação**: Scripts `run_https.py` e `run_network.bat`
- **Prioridade**: Alta

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
| RF010 | Análise IA | Alta | ✅ Implementado |
| RF011 | Câmera | Alta | ✅ Implementado |
| RF012 | Menu Usuário | Baixa | ✅ Implementado |
| RF013 | Monitoramento Online | Média | ✅ Implementado |
| RF014 | Log de Atividades | Média | ✅ Implementado |
| RF015 | Bloqueio Pendentes | Alta | ✅ Implementado |
| RF016 | Gerenciamento Reportes | Alta | ✅ Implementado |
| RF017 | Integração TUPA | Alta | ✅ Implementado |

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
