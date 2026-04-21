# Regras de Negócio - ANHANGÁ

## 🎯 RN001 - Classificação de Alertas Comunitários

### Descrição
Reportes de queimadas são classificados automaticamente baseado na quantidade de reportes próximos.

### Regra
```
IF count_reportes = 1 THEN
    nivel = "alerta"
    cor = "amarelo (#ebc165)"
    
ELSEIF count_reportes = 2 THEN
    nivel = "suspeito"
    cor = "laranja (#fb923c)"
    
ELSEIF count_reportes >= 3 THEN
    nivel = "confirmado"
    cor = "vermelho (#dc2626)"
```

### Raio de Agrupamento
- **Distância máxima**: 1km (0.01 graus)
- **Lógica**: Reportes dentro do raio contam para o mesmo ponto

### Exemplo
```
Usuário A reporta em (-3.1234, -60.5678) → Alerta
Usuário B reporta em (-3.1235, -60.5679) → Suspeito (mesmo raio)
Usuário C reporta em (-3.1233, -60.5677) → Confirmado
```

---

## 👥 RN002 - Tipos de Usuário e Aprovação

### Níveis de Acesso

| Tipo | Valor | Nome | Permissões |
|------|-------|------|------------|
| **Pendente** | 0 | Pendente | Não pode fazer login nem reportar |
| **Ativo** | 1 | Ativo | Reportar, visualizar mapa, editar perfil, monitoramento |
| **Especial** | 2 | Especial | Tudo do ativo + reportes confirmam imediatamente |

### Admin
- Apenas usuário com **username="admin"** pode acessar painel administrativo
- Admin pode aprovar usuários pendentes (0 → 1)
- Admin pode promover usuários ativos (1 → 2)
- Admin pode rebaixar usuários especiais (2 → 1)

### Fluxo de Aprovação
```
Cadastro → PENDENTE (tipo 0) → Admin Aprova → ATIVO (tipo 1) → Admin Promove → ESPECIAL (tipo 2)
              ↓
       Não pode fazer login
```

### Transições de Status
| Ação | De | Para | Quem pode |
|------|-----|------|-----------|
| Cadastro | - | Pendente (0) | Qualquer pessoa |
| Aprovação | Pendente (0) | Ativo (1) | Admin |
| Promoção | Ativo (1) | Especial (2) | Admin |
| Rebaixamento | Especial (2) | Ativo (1) | Admin |

---

## 🔐 RN003 - Autenticação e Sessão

### Login
1. Username é convertido para lowercase
2. Senha comparada diretamente (SHA-256 não implementado ainda)
3. Token JWT gerado (24 caracteres aleatórios)
4. Token armazenado em localStorage

### Proteção de Rotas
- Todas as páginas internas verificam `localStorage.getItem("ANHANGA_TOKEN")`
- Se não existir, redireciona para `login.html`
- API verifica header `Authorization: Bearer <token>`

### Expiração
- Tokens não expiram automaticamente (sessão persistente)
- Logout limpa localStorage

---

## 🗺️ RN004 - Fontes de Alertas

### NASA FIRMS (Queimadas)
- **Endpoint**: `/api/alertas/landsat` (usando FIRMS como proxy)
- **Tipo**: Queimadas ativas
- **Cor no mapa**: Vermelho (#ef4444)
- **Dados**: Temperatura, confiança, FRP (potência radiativa)
- **Atualização**: Near real-time (3-6 horas)

### Global Forest Watch (Desmatamento)
- **Endpoint**: `/api/alertas/unificado` (inclui GFW)
- **Tipo**: Desmatamento (GLAD, RADD, etc)
- **Cor no mapa**: Laranja/Marrom (#f59e0b)
- **Dados**: Data do alerta, confiança, tipo de perda
- **Atualização**: Semanal

### Reportes Comunitários
- **Endpoint**: `/api/reportar/*`
- **Tipo**: Queimadas reportadas por usuários
- **Cor no mapa**: Variável (alerta/suspeito/confirmado)
- **Dados**: Localização, foto, usuário, timestamp

---

## 📍 RN005 - Limites Geográficos

### Região Válida
- **Nome**: Amazônia Legal
- **Latitude**: -20.0 a 10.0
- **Longitude**: -74.0 a -44.0

### Validações
1. Reportes fora da Amazônia são rejeitados
2. APIs sempre consultam apenas essa região
3. Mapa inicia centrado na Amazônia Brasileira

### Países Cobertos
- Brasil (Amazônia Legal)
- Peru
- Colômbia
- Venezuela
- Equador
- Bolívia
- Guianas

---

## 📸 RN006 - Upload de Fotos

### Reportes
- **Formato**: JPG, PNG
- **Tamanho máximo**: 5MB
- **Armazenamento**: Arquivo no servidor (pasta uploads)
- **Validação**: Apenas imagens, verificação MIME

### Perfil
- **Formato**: Base64
- **Tamanho máximo**: 2MB
- **Armazenamento**: Banco de dados (campo foto_url)
- **Validação**: Crop opcional (não implementado)

---

## 🎨 RN007 - Cores e Visualização

### Paleta Principal
```css
--bg-primary: #001710
--bg-surface: #0c3026
--text-primary: #98d3b7
--accent-primary: #98d3b7
--alert-fire: #ef4444
--alert-deforestation: #f59e0b
--alert-warning: #ebc165
--alert-suspect: #fb923c
--alert-confirmed: #dc2626
```

### Cores por Tipo
| Tipo | Hex | Uso |
|------|-----|-----|
| Queimada FIRMS | #ef4444 | Alertas de fogo |
| Desmatamento GFW | #f59e0b | Perda de vegetação |
| Alerta | #ebc165 | 1 reporte |
| Suspeito | #fb923c | 2 reportes |
| Confirmado | #dc2626 | 3+ reportes |

---

## 📊 RN008 - Limites do Sistema

### Banco de Dados
- **Máximo usuários**: ~10.000 (SQLite limit)
- **Máximo reportes**: ~100.000
- **Tamanho foto perfil**: 2MB
- **Tamanho foto reporte**: 5MB

### APIs Externas
- **FIRMS**: Máximo 500 alertas/requisição
- **GFW**: Máximo 1000 alertas/requisição
- **Timeout**: 30 segundos
- **Retry**: 1 tentativa em caso de falha

### Frontend
- **Marcadores no mapa**: Máximo 300 visíveis
- **Filtro de dias**: 7, 14, ou 30 dias
- **Cache**: Não implementado (futuro)

---

## 🔄 RN009 - Workflows

### Cadastro de Usuário
```
1. Usuário preenche formulário (nome, email, data nasc., telefone, username, senha, foto)
2. Sistema valida:
   - Todos campos obrigatórios preenchidos
   - Idade mínima 12 anos
   - Senha mínimo 8 caracteres
   - Username único
   - Email único
3. Sistema cria registro no banco com tipo=0 (PENDENTE)
4. Mensagem: "Cadastro realizado! Aguarde aprovação do admin."
5. Usuário aguarda aprovação (não pode fazer login)
```

### Aprovação de Usuário (Admin)
```
1. Admin acessa painel administrativo
2. Visualiza lista de usuários pendentes
3. Clica em "Aprovar" no usuário desejado
4. Sistema altera tipo: 0 (Pendente) → 1 (Ativo)
5. Usuário pode fazer login e usar o sistema
```

### Reporte de Queimada - Usuário Tipo 1 (Ativo)
```
1. Usuário clica no mapa ou usa geolocalização
2. Sistema calcula coordenadas
3. Usuário anexa foto
4. NOVO REPORTE → Status: ALERTA (amarelo)
5. 1ª CONFIRMAÇÃO (outro usuário tipo 1) → Status: SUSPEITO (laranja)
6. 2ª CONFIRMAÇÃO (outro usuário tipo 1) → Status: CONFIRMADO (vermelho)

Restrições:
- Cada usuário tipo 1 só pode reportar/confirmar 1 vez por localidade (raio 500m)
- Não pode confirmar próprio reporte
```

### Reporte de Queimada - Usuário Tipo 2 (Especial)
```
1. Usuário clica no mapa ou usa geolocalização
2. Sistema calcula coordenadas
3. Usuário anexa foto
4. NOVO REPORTE → Status: CONFIRMADO imediatamente (vermelho)

Vantagens:
- Não precisa de confirmações de outros usuários
- Ao confirmar reporte de outros, vai direto para CONFIRMADO
```

### Promoção de Usuário
```
1. Admin acessa painel administrativo
2. Visualiza lista de usuários ativos (tipo 1)
3. Clica em "Promover" no usuário desejado
4. Sistema altera tipo: 1 (Ativo) → 2 (Especial)
5. Usuário passa a ter poderes de confirmação imediata
```

### Monitoramento de Usuários Online (Admin)
```
1. Admin acessa painel administrativo
2. Visualiza quadro "Usuários Online":
   - Foto, nome e username
   - Indicador de status online
   - Tempo desde última atividade
3. Visualiza quadro "Atividades Recentes":
   - Login/logout
   - Reportes criados
   - Confirmações realizadas
4. Sistema atualiza automaticamente a cada 30 segundos
5. Usuários que fazem logout saem da lista imediatamente
```

---

## ⚠️ RN010 - Tratamento de Erros

### APIs Externas Falham
- Usar dados de exemplo (mock)
- Logar erro no console
- Não bloquear interface

### Token Inválido
- Redirecionar para login
- Limpar localStorage
- Mensagem: "Sessão expirada"

### Banco Indisponível
- Mostrar erro 500
- Sugerir recarregar página
- Logar stack trace

### Geolocalização Negada
- Permitir clique manual no mapa
- Mostrar mensagem informativa
- Não bloquear funcionalidade

---

## 📈 RN011 - Métricas e KPIs

### Sistema
- Total de usuários registrados
- Total de reportes
- Média de reportes por usuário
- Alertas ativos (últimos 30 dias)

### Performance
- Tempo médio de resposta API: < 3s
- Tempo de carregamento do mapa: < 5s
- Taxa de erro de APIs externas: < 10%

### Negócio
- Percentual de reportes confirmados
- Usuários ativos (reportaram nos últimos 30 dias)
- Cobertura geográfica dos reportes

---

## 📝 RN012 - Validações de Dados

### Cadastro de Usuário (Obrigatórios)
| Campo | Validação |
|-------|-----------|
| **Nome** | 2-120 caracteres |
| **Email** | Formato válido, único no sistema |
| **Data nascimento** | Formato AAAA-MM-DD, idade mínima 12 anos |
| **Telefone** | Mínimo 8 caracteres |
| **Username** | 3-80 caracteres, alfanumérico + underscore, único |
| **Senha** | Mínimo 8 caracteres |
| **Foto** | Base64 ou URL, obrigatória |

### Login
- Username convertido para lowercase
- Usuários tipo 0 (Pendente) são bloqueados: "Cadastro pendente de aprovação"

### Reporte
- **Latitude**: -90 a 90 (deve estar na Amazônia)
- **Longitude**: -180 a 180 (deve estar na Amazônia)
- **Foto**: JPG/PNG, máximo 5MB
- **Raio de agrupamento**: 500m (0.0045 graus)
- **Restrição**: Usuário tipo 0 não pode reportar

---

## 🏛️ RN013 - Governança

### Responsabilidades
- **Desenvolvedor**: Manter código, corrigir bugs
- **Admin**: Gerenciar usuários, validar reportes críticos
- **Usuário**: Reportar queimadas, manter dados atualizados

### Compliance
- Dados pessoais mínimos coletados
- Localização apenas para reportes
- Fotos podem conter metadados GPS
- Sem compartilhamento com terceiros
