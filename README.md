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
├── database.py                  # Modelos ORM (compartilhado)
├── seed.py                      # Dados iniciais
├── firms_alerts.py              # Integração NASA FIRMS
├── gfw_alerts.py                # Integração GFW
├── requirements.txt             # Dependências
└── .env                         # Variáveis de ambiente
```

---

## 🔧 Funcionalidades Principais

### 1. Mapa Interativo (`mapa.html`)
- Visualização de alertas de queimadas (FIRMS)
- Visualização de alertas de desmatamento (GFW)
- Filtros por período (7, 14, 30 dias)
- Reportes da comunidade
- Clusters de alertas próximos

### 2. Sistema de Reportes
- Usuários reportam queimadas com foto
- Validação por múltiplos reportes
- Níveis: Alerta → Suspeito → Confirmado

### 3. Gerenciamento de Usuários
- Cadastro com dados pessoais
- Autenticação JWT
- Tipos: Normal (0) e Especial/Admin (1)
- Perfil com foto e edição de dados

### 4. Painel Administrativo
- Gerenciar usuários
- Visualizar estatísticas
- Acesso restrito a admins

---

## 🚀 Como Executar

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

# Iniciar servidor
python app.py
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

| Usuário | Senha | Tipo |
|---------|-------|------|
| admin | admin | Administrador (1) |

---

## 📄 Documentação Adicional

- [Requisitos Funcionais e Não Funcionais](REQUISITOS.md)
- [Regras de Negócio](REGRAS_NEGOCIO.md)
- [Segurança](SEGURANCA.md)
- [Banco de Dados](BANCO_DADOS.md)
- [Arquitetura e Tecnologias](ARQUITETURA.md)

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
