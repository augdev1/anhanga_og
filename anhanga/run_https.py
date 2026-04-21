"""
Executa o servidor Flask com HTTPS para permitir acesso à câmera via IP/redes.
"""
import ssl
import os
from app import create_app

def create_self_signed_cert():
    """Gera certificado SSL auto-assinado se não existir."""
    cert_dir = os.path.join(os.path.dirname(__file__), 'certs')
    cert_file = os.path.join(cert_dir, 'server.crt')
    key_file = os.path.join(cert_dir, 'server.key')

    if not os.path.exists(cert_file) or not os.path.exists(key_file):
        print("🔐 Gerando certificado SSL auto-assinado...")
        os.makedirs(cert_dir, exist_ok=True)

        # Usar OpenSSL para gerar certificado
        from subprocess import run, PIPE

        # Comando para gerar certificado auto-assinado
        cmd = [
            'openssl', 'req', '-x509', '-newkey', 'rsa:2048',
            '-keyout', key_file,
            '-out', cert_file,
            '-days', '365',
            '-nodes', '-subj', '/CN=anhanga.local/O=ANHANGA/C=BR'
        ]

        try:
            result = run(cmd, capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ Certificado gerado em: {cert_dir}")
                print("   - server.crt (certificado)")
                print("   - server.key (chave privada)")
            else:
                print("❌ Erro ao gerar certificado:", result.stderr)
                return None, None
        except FileNotFoundError:
            print("❌ OpenSSL não encontrado. Instale o OpenSSL:")
            print("   Windows: https://slproweb.com/products/Win32OpenSSL.html")
            print("   Ou use o WSL: wsl openssl ...")
            return None, None

    return cert_file, key_file

if __name__ == '__main__':
    import socket

    # Obter IP local
    hostname = socket.gethostname()
    local_ip = socket.getaddrinfo(hostname, None, socket.AF_INET)[0][4][0]

    print("=" * 60)
    print("🌿 ANHANGÁ - Servidor HTTPS")
    print("=" * 60)
    print(f"\n📡 IP deste computador: {local_ip}")
    print(f"🔗 URL para acessar na rede: https://{local_ip}:5000")
    print("\n⚠️  Importante:")
    print("   - O navegador vai mostrar 'Não seguro' (normal para certificado auto-assinado)")
    print("   - Clique em 'Avançado' → 'Prosseguir para...'")
    print("   - A câmera vai funcionar em qualquer dispositivo da rede!")
    print("\n" + "=" * 60)

    # Criar certificado
    cert, key = create_self_signed_cert()

    if cert and key:
        # Rodar com HTTPS
        ssl_context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ssl_context.load_cert_chain(cert, key)

        app = create_app()
        app.run(host='0.0.0.0', port=5000, ssl_context=ssl_context, debug=True)
    else:
        print("\n🔄 Fallback para HTTP (sem câmera em outros dispositivos)")
        app = create_app()
        app.run(host='0.0.0.0', port=5000, debug=True)
