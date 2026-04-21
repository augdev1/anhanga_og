# ANHANGÁ - Sistema de Monitoramento Ambiental

## 📋 Visão Geral

O **ANHANGÁ** é um sistema web para monitoramento ambiental da Amazônia, focado em detectar e reportar queimadas e desmatamentos em tempo real. O sistema integra dados de satélites (NASA FIRMS, Global Forest Watch) com reportes da comunidade.

---

## 🎯 Objetivos

- Monitorar queimadas e desmatamentos na Amazônia Legal
- Permitir reportes colaborativos da comunidade
- Visualizar alertas em mapa interativo
- Gerenciar usuários com diferentes níveis de acesso

---

## 🏗️ Arquitetura do Sistema

### Tecnologias Principais

| Camada | Tecnologia |
|--------|------------|
| **Backend** | Python 3.12+ |
| **Frontend** | HTML5 + TailwindCSS + JavaScript |
| **Framework Web** | Flask (porta 5000) |
| **API** | Flask Routes (integrado) |
| **Banco de Dados** | SQLite + SQLAlchemy ORM |
| **Mapas** | Leaflet.js |
| **Ícones** | Material Symbols |

### APIs Externas Integradas

- **NASA FIRMS** - Alertas de queimadas em tempo real
- **Global Forest Watch (GFW)** - Alertas de desmatamento
- **Teachable Machine (TensorFlow.js)** - Análise de imagem por IA

---

## 📁 Estrutura do Projeto

```
ANHANGA/
├── app/
│   ├── __init__.py              # Configuração Flask
│   ├── models.py                # Modelos SQLAlchemy
│   ├── routes.py                # Rotas e endpoints API
│   └── templates/               # Templates HTML
│       ├── admin.html           # Painel administrativo
│       ├── index.html           # Página inicial
│       ├── insights.html        # Dashboard analítico
│       ├── login.html           # Autenticação
│       ├── mapa.html            # Mapa principal (core)
│       ├── monitoramento.html   # Monitoramento em tempo real
│       ├── perfil.html          # Perfil do usuário
│       ├── register.html        # Cadastro
│       └── reportar.html        # Reportar queimada
├── instance/
│   └── app.db                   # Banco SQLite
├── config.py                    # Configurações
├── firms_alerts.py              # API NASA
├── gfw_alerts.py                # API GFW
├── models/                      # Modelos Teachable Machine
│   ├── README.md               # Documentação dos modelos
│   ├── labels.txt              # Classes do modelo
│   └── *.json, *.bin           # Arquivos do modelo
├── run_https.py                # Servidor HTTPS para rede
├── run_network.bat             # Script fácil de execução
├── seed.py                      # Dados iniciais
├── app.py                      # Entry point
├── requirements.txt            # Dependências
├── .env                        # Secrets (não commitar)
└── docs/                       # Documentação
```

---

## Funcionalidades Principais

### 1. Mapa Interativo (`mapa.html`)
- Visualização de alertas de queimadas (FIRMS)
- Visualização de alertas de desmatamento (GFW)
- Filtros por período (7, 14, 30 dias)
- Reportes da comunidade
- Clusters de alertas próximos

### 2. Análise por IA (`monitoramento.html`)
- Detecção de queimadas via câmera em tempo real
- Integração com **Teachable Machine** (TensorFlow.js)
- Modelos treináveis para classificação de imagem
- Fallback por análise de cores (sem modelo)
- Suporte a múltiplas classes: queimada, floresta, solo exposto, água, nuvem
- Análise contínua ou frame único

### 3. Sistema de Reportes
- Usuários reportam queimadas com foto e localização
- Validação colaborativa por múltiplos usuários
- Níveis: Alerta (1) → Suspeito (2) → Confirmado (3+)
- Raio de agrupamento: 500m
- Usuário tipo 2 (Especial) confirma imediatamente

### 4. Gerenciamento de Usuários com Aprovação
- **Cadastro com validações:** idade mínima 12 anos, senha 8+, foto obrigatória
- **Fluxo de aprovação:**
  - Novo usuário → Tipo 0 (Pendente) → Aguarda aprovação
  - Admin aprova → Tipo 1 (Ativo) → Pode usar o sistema
  - Admin promove → Tipo 2 (Especial) → Confirma imediatamente
- **Recuperação de senha:** Validar email, nome e data de nascimento para redefinir
- **Perfil**: Foto, dados pessoais, edição
- Autenticação JWT com bloqueio de pendentes

### 5. Painel Administrativo (Apenas username="admin")
- **Gerenciamento de usuários:**
  - Visualizar todos os usuários por tipo (Pendente/Ativo/Especial)
  - Aprovar usuários pendentes (0 → 1)
  - Promover usuários ativos (1 → 2)
  - Rebaixar usuários especiais (2 → 1)
- **Gerenciamento de reportes:**
  - Listar todos os reportes de queimada (alerta, suspeito, confirmado)
  - Deletar reportes de queimada
  - Visualizar usuário, nível, fonte, data e localização de cada reporte
- **Monitoramento em tempo real:**
  - Usuários online (foto, nome, tempo de atividade)
  - Atividades recentes (login, logout, reportes, confirmações, deleções)
  - Atualização automática a cada 30 segundos
- Estatísticas do sistema

### 6. Integração com Sistemas Externos (TUPA)
- **Endpoint POST `/api/reportes`:**
  - Recebe reportes externos do sistema TUPA
  - Não requer autenticação
  - Salva reportes com campo `fonte` indicando origem
  - Envia notificação de volta para TUPA após salvar
- **Campo `fonte` na tabela reports:**
  - Identifica a origem do reporte (comunidade, tupa, etc.)
  - Permite filtrar e rastrear reportes por sistema
  - Exibido no painel admin para transparência

---

## Acesso em Rede (Outros Dispositivos)

Para acessar de celulares/tablets na mesma rede WiFi:

### Opção 1: HTTPS (Recomendado)
```bash
python run_https.py
```
- Acesse: `https://IP-DO-SEU-PC:5000`
- Aceite o certificado auto-assinado no navegador
- Câmera funciona em qualquer dispositivo!

### Opção 2: Script Interativo
```bash
run_network.bat  # Windows
```
Escolha opção 2 para iniciar com HTTPS.

**Importante**: Navegadores exigem HTTPS para acessar câmera em IPs que não sejam localhost.

---

## Como Executar

### 1. Instalação
```bash
# Criar ambiente virtual
python -m venv venv

# Ativar
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependências
pip install -r requirements.txt
```

### 2. Configuração
```bash
# Criar arquivo .env
cp .env.example .env

# Editar com suas chaves de API
GFW_API_TOKEN=sua_chave_aqui
FIRMS_API_KEY=sua_chave_aqui
```

### 3. Inicialização
```bash
# Resetar banco (opcional - primeira vez)
rm instance/app.db

# Iniciar servidor (localhost apenas)
python app.py

# OU: Iniciar com HTTPS (para acesso em rede)
python run_https.py
```

### 4. Acesso
- Frontend: http://localhost:5000
- API: http://localhost:5000/api/

---

## 📊 Dados e Limites

### Região Monitorada
- **Amazônia Legal** (fixo)
- Latitude: -20° a 10°
- Longitude: -74° a -44°

### Limites do Sistema
- Máximo 300 alertas FIRMS por requisição
- Máximo 1000 alertas GFW por requisição
- Fotos de perfil: base64, máximo 2MB
- Sessão: token JWT no localStorage

---

## 👥 Usuários Padrão

| Usuário | Senha | Tipo | Descrição |
|---------|-------|------|-----------|
| admin | admin12345 | Ativo (1) | Único acesso ao painel admin |

**Nota:** O usuário admin é criado automaticamente pelo `seed.py` com todos os campos obrigatórios preenchidos.

---

## 📄 Documentação Adicional

- [Requisitos Funcionais e Não Funcionais](REQUISITOS.md)
- [Regras de Negócio](REGRAS_NEGOCIO.md) - Detalhes do fluxo de aprovação e reportes
- [Segurança](SEGURANCA.md)
- [Banco de Dados](BANCO_DADOS.md) - Estrutura das tabelas e relacionamentos
- [Arquitetura e Tecnologias](ARQUITETURA.md)
- [Câmera em Rede](REDE_CAMERA.md)
- [Endpoints da API](ENDPOINTS.md) - Documentação completa dos endpoints

---

## 📝 Licença

Projeto desenvolvido para fins educacionais e ambientais.

---

## 🤝 Contribuição

1. Fork o projeto
2. Crie sua branch (`git checkout -b feature/nova-funcionalidade`)
3. Commit suas mudanças (`git commit -m 'Adiciona nova funcionalidade'`)
4. Push para a branch (`git push origin feature/nova-funcionalidade`)
5. Abra um Pull Request
