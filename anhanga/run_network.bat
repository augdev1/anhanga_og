@echo off
chcp 65001 >nul
echo ============================================
echo 🌿 ANHANGÁ - Servidor para Rede
echo ============================================
echo.

:: Obter IP local
for /f "tokens=2 delims=[]" %%a in ('ping -4 -n 1 %computername% ^| findstr [') do set LOCAL_IP=%%a
echo 📡 IP deste computador: %LOCAL_IP%
echo.

echo Escolha como rodar:
echo [1] HTTP (localhost apenas, câmera local apenas)
echo [2] HTTPS (para acessar de outros dispositivos)
echo.
set /p choice="Opção (1 ou 2): "

if "%choice%"=="1" (
    echo.
    echo 🚀 Iniciando HTTP em localhost:5000...
    python -c "from app import create_app; app = create_app(); app.run(host='127.0.0.1', port=5000, debug=True)"
) else if "%choice%"=="2" (
    echo.
    echo 🔐 Iniciando HTTPS para rede...
    echo URL para acessar: https://%LOCAL_IP%:5000
    echo.
    python run_https.py
) else (
    echo Opção inválida!
    pause
)
