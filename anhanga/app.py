import os
from dotenv import load_dotenv
from app import create_app

# Carregar variáveis de ambiente do arquivo .env
load_dotenv()

# Run seed to create admin user
import seed
seed.seed()

app = create_app()

if __name__ == "__main__":
    # Flask acessível na rede (outros dispositivos)
    app.run(host="0.0.0.0", debug=True, port=5000)