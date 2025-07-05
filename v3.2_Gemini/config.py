# video_analyzer/v4/config.py
import os
from dotenv import load_dotenv

load_dotenv() # Carrega as variáveis do .env

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    print("AVISO: Variável de ambiente OPENAI_API_KEY não configurada. As funcionalidades de IA podem não funcionar.")