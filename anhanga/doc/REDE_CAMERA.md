# 📡 Como Usar a Câmera em Outros Dispositivos na Rede

## O Problema

Navegadores modernos **só permitem acesso à câmera** em:
- ✅ `http://localhost` ou `http://127.0.0.1` (desenvolvimento local)
- ✅ `https://` (qualquer IP/domínio, com SSL)
- ❌ `http://192.168.x.x` (IP da rede) - **BLOQUEADO** 🔒

Para acessar de outro celular/tablet/computador na mesma rede WiFi, você precisa de **HTTPS**.

---

## 🚀 Opção 1: HTTPS com Certificado Auto-Assinado (Recomendado)

### Passo 1: Instalar OpenSSL (Windows)
1. Baixe: https://slproweb.com/products/Win32OpenSSL.html
2. Escolha "Win64 OpenSSL Light"
3. Instale com as opções padrão
4. Adicione ao PATH se perguntar

### Passo 2: Executar
```bash
python run_https.py
```

Ou clique duplo em: `run_network.bat` → escolha opção 2

### Passo 3: Acessar do Outro Dispositivo
1. No navegador do outro dispositivo, digite:
   ```
   https://IP-DO-SEU-PC:5000
   ```
   Exemplo: `https://192.168.1.10:5000`

2. O navegador vai avisar "Não seguro" - isso é **NORMAL** para certificados auto-assinados
   - Chrome: Clique em "Avançado" → "Prosseguir para 192.168.x.x"
   - Firefox: Clique em "Avançado" → "Aceitar risco e continuar"

3. A câmera vai funcionar! 🎉

---

## 🔄 Opção 2: Flag de Segurança do Chrome (Apenas Teste)

⚠️ **Só use em desenvolvimento**, desative depois!

### No Windows:
1. Feche todos os Chrome/Edge
2. Abra CMD e execute:
```cmd
cd "C:\Program Files\Google\Chrome\Application"
chrome.exe --unsafely-treat-insecure-origin-as-secure="http://SEU-IP:5000" --user-data-dir="C:\temp-chrome-dev"
```

Substitua `SEU-IP` pelo IP do computador (ex: `192.168.1.10`)

### Acessar:
- Outro dispositivo: `http://SEU-IP:5000` (sem https!)

---

## 📱 Opção 3: ngrok (Tunnel para Internet)

Se quiser acessar de **qualquer lugar** (não só da rede local):

### 1. Instalar ngrok
```bash
# Windows (com PowerShell)
choco install ngrok
# ou baixe em https://ngrok.com/download
```

### 2. Criar conta gratuita
- https://ngrok.com/
- Pegue seu authtoken

### 3. Configurar
```bash
ngrok authtoken SEU_TOKEN_AQUI
```

### 4. Criar tunnel
```bash
# Terminal 1 - Rode o servidor local normal
python app.py

# Terminal 2 - Crie o tunnel
ngrok http 5000
```

### 5. Acessar
O ngrok vai gerar uma URL tipo:
```
https://abc123-def.ngrok.io
```

Use essa URL em qualquer dispositivo - já vem com HTTPS! ✅

---

## 🔧 Resumo Rápido

| Método | Quando Usar | Dificuldade |
|--------|-------------|-------------|
| `run_https.py` | Rede local, dispositivos confiáveis | ⭐⭐ Médio |
| Flag do Chrome | Teste rápido, dev only | ⭐ Fácil |
| ngrok | Acesso remoto, compartilhar | ⭐⭐⭐ Mais configuração |

---

## 💡 Dicas

### Descobrir seu IP:
```cmd
ipconfig
```
Procure por "Endereço IPv4" na conexão Wi-Fi ou Ethernet

### Firewall Windows
Se não conseguir acessar, libere a porta 5000:
```cmd
netsh advfirewall firewall add rule name="ANHANGA" dir=in action=allow protocol=TCP localport=5000
```

### Mesma Rede
- Computador e celular precisam estar no **mesmo WiFi**
- Não funciona via dados móveis do celular

---

## ❓ Troubleshooting

### "Não seguro" / Certificado inválido
- **Solução:** Aceite o risco no navegador (Avançar → Prosseguir)
- Isso é normal para certificados auto-assinados

### Câmera não aparece no celular
- Verifique se deu permissão no navegador do celular
- Tente atualizar a página (F5)

### Conexão recusada
- Verifique se o firewall está bloqueando
- Confirme que está usando o IP correto

---

**Recomendação:** Use `run_https.py` para testes em rede local. É a opção mais simples que funciona! 🎯
