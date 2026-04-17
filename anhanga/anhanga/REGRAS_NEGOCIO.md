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

## 👥 RN002 - Tipos de Usuário

### Níveis de Acesso

| Tipo | Valor | Permissões |
|------|-------|------------|
| **Normal** | 0 | Reportar, visualizar mapa, editar perfil |
| **Especial/Admin** | 1 | Tudo do normal + painel administrativo |

### Transições
- Admin pode promover usuário normal para especial
- Apenas usuário "admin" (hardcoded) pode acessar painel inicialmente
- Novos usuários registrados são sempre tipo 0

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
1. Usuário preenche formulário
2. Sistema valida username único
3. Sistema cria registro no banco
4. Sistema cria token automático
5. Usuário é redirecionado para mapa
```

### Reporte de Queimada
```
1. Usuário clica no mapa ou usa geolocalização
2. Sistema calcula coordenadas
3. Usuário anexa foto opcional
4. Sistema conta reportes próximos (1km)
5. Sistema classifica nível (alerta/suspeito/confirmado)
6. Sistema salva no banco
7. Marcador aparece no mapa
```

### Promoção de Usuário
```
1. Admin acessa painel administrativo
2. Seleciona usuário da lista
3. Altera tipo de 0 para 1
4. Sistema atualiza banco
5. Usuário recebe acesso imediato ao painel
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

### Usuário
- **Username**: 3-50 caracteres, alfanumérico + underscore
- **Nome**: 2-100 caracteres
- **Senha**: Mínimo 6 caracteres
- **Email**: Formato válido (opcional)
- **Telefone**: Formato livre (opcional)
- **Data nascimento**: Data válida, maior de 13 anos

### Reporte
- **Latitude**: -90 a 90 (deve estar na Amazônia)
- **Longitude**: -180 a 180 (deve estar na Amazônia)
- **Foto**: JPG/PNG, máximo 5MB

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
