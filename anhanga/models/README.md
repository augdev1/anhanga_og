# Modelos Teachable Machine

Esta pasta contém os modelos de machine learning exportados do [Teachable Machine](https://teachablemachine.withgoogle.com/).

## 📁 Estrutura

```
models/
├── README.md           # Este arquivo
├── model.json          # Arquitetura do modelo
├── weights.bin         # Pesos treinados
├── metadata.json       # Labels e configurações
└── labels.txt          # Lista de classes (opcional)
```

## 🚀 Como Usar

### 1. Treinar no Teachable Machine
1. Acesse: https://teachablemachine.withgoogle.com/
2. Crie um projeto "Image Project"
3. Adicione classes:
   - `queimada` - Fotos de áreas queimadas
   - `floresta` - Fotos de vegetação saudável
   - `solo_exposto` - Áreas desmatadas
4. Treine o modelo
5. Clique em "Export Model" → "Download" → escolha "TensorFlow.js"

### 2. Colocar Arquivos na Pasta
Extraia o arquivo ZIP e copie para esta pasta:
- `model.json`
- `weights.bin`
- `metadata.json`

### 3. Testar no Monitoramento
1. Acesse a página de Monitoramento
2. O modelo será carregado automaticamente
3. Ative a câmera para análise em tempo real

## 📝 Formato do labels.txt (opcional)

```
queimada
floresta
solo_exposto
```

## 🔧 API Flask para Modelos

O backend pode servir os arquivos do modelo via endpoint:
```
GET /api/models/<arquivo>
```

## 📊 Classes Recomendadas

| Classe | Descrição | Cor no Mapa |
|--------|-----------|-------------|
| `queimada` | Áreas ativas ou recentemente queimadas | Vermelho |
| `floresta` | Vegetação densa e saudável | Verde |
| `solo_exposto` | Áreas desmatadas, terra nua | Marrom |
| `agua` | Rios, lagos, alagados | Azul |

## ⚠️ Limitações

- Modelo treinado em imagens específicas pode não generalizar
- Iluminação e ângulo afetam a precisão
- Use análise por cor como fallback
