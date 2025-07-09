# video_analyzer/v4/config.py
"""
Sistema de configuração avançado para NASCO Analyzer v4.0 ULTIMATE
Carrega configurações do .env e define padrões inteligentes
"""

import os
from pathlib import Path
from dotenv import load_dotenv
import streamlit as st

# Carregar variáveis de ambiente
load_dotenv()

# --- CONFIGURAÇÕES DE IA ---
OPENAI_API_KEY = os.getenv('OPENAI_API_KEY', '')
OPENAI_ORG_ID = os.getenv('OPENAI_ORG_ID', '')

# Configurações padrão de modelos
DEFAULT_GPT_MODEL = os.getenv('DEFAULT_GPT_MODEL', 'gpt-3.5-turbo')
DEFAULT_TEMPERATURE = float(os.getenv('DEFAULT_TEMPERATURE', '0.3'))

# Tokens padrão
DEFAULT_MAX_TOKENS_SUMMARY = int(
    os.getenv('DEFAULT_MAX_TOKENS_SUMMARY', '400'))
DEFAULT_MAX_TOKENS_INSIGHTS = int(
    os.getenv('DEFAULT_MAX_TOKENS_INSIGHTS', '600'))
DEFAULT_MAX_TOKENS_QUIZ = int(os.getenv('DEFAULT_MAX_TOKENS_QUIZ', '700'))

# --- CONFIGURAÇÕES DE WHISPER ---
DEFAULT_WHISPER_MODEL = os.getenv('DEFAULT_WHISPER_MODEL', 'small')
DEFAULT_WHISPER_LANGUAGE = os.getenv('DEFAULT_WHISPER_LANGUAGE', 'pt')

# --- CONFIGURAÇÕES DE SISTEMA ---
MAX_FILE_SIZE_MB = int(os.getenv('MAX_FILE_SIZE_MB', '500'))
MAX_THREADS = int(os.getenv('MAX_THREADS', '4'))
AI_REQUEST_TIMEOUT = int(os.getenv('AI_REQUEST_TIMEOUT', '120'))

# Cache
ENABLE_CACHE = os.getenv('ENABLE_CACHE', 'true').lower() == 'true'

# --- CONFIGURAÇÕES DE INTERFACE ---
DEFAULT_THEME = os.getenv('DEFAULT_THEME', 'auto')
DEBUG_MODE = os.getenv('DEBUG_MODE', 'false').lower() == 'true'

# --- CONFIGURAÇÕES AVANÇADAS ---
ENABLE_PDF_IMAGES = os.getenv('ENABLE_PDF_IMAGES', 'true').lower() == 'true'
ENABLE_SENTIMENT_ANALYSIS = os.getenv(
    'ENABLE_SENTIMENT_ANALYSIS', 'false').lower() == 'true'
ENABLE_LANGUAGE_DETECTION = os.getenv(
    'ENABLE_LANGUAGE_DETECTION', 'true').lower() == 'true'

# --- LOGGING ---
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_PATH = os.getenv('LOG_PATH', str(Path.cwd() / 'logs'))

# --- BACKUP ---
BACKUP_INTERVAL_HOURS = int(os.getenv('BACKUP_INTERVAL_HOURS', '24'))
BACKUP_PATH = os.getenv('BACKUP_PATH', str(Path.cwd() / 'backups'))

# --- TELEMETRIA ---
ENABLE_TELEMETRY = os.getenv('ENABLE_TELEMETRY', 'false').lower() == 'true'

# --- FORMATOS SUPORTADOS ---
SUPPORTED_VIDEO_FORMATS = ['.mp4', '.avi', '.mov', '.mkv',
                           '.webm', '.flv', '.m4v', '.wmv', '.3gp', '.mpg', '.mpeg']
SUPPORTED_AUDIO_FORMATS = ['.mp3', '.wav', '.m4a',
                           '.flac', '.ogg', '.aac', '.wma', '.opus']
SUPPORTED_DOCUMENT_FORMATS = ['.pdf', '.docx', '.pptx', '.txt', '.md', '.rtf']
SUPPORTED_SUBTITLE_FORMATS = ['.srt', '.vtt', '.ass', '.ssa', '.sub', '.sbv']

# --- CONFIGURAÇÕES DE QUALIDADE ---
VIDEO_QUALITY_SETTINGS = {
    'low': {'bitrate': '500k', 'fps': 24},
    'medium': {'bitrate': '1500k', 'fps': 30},
    'high': {'bitrate': '3000k', 'fps': 60}
}

AUDIO_QUALITY_SETTINGS = {
    'low': {'bitrate': '96k', 'sample_rate': 22050},
    'medium': {'bitrate': '128k', 'sample_rate': 44100},
    'high': {'bitrate': '320k', 'sample_rate': 48000}
}

# --- CONFIGURAÇÕES DE IA POR TIPO DE CONTEÚDO ---
AI_CONFIGS = {
    'video': {
        'summary_tokens': 450,
        'insights_tokens': 650,
        'quiz_tokens': 750,
        'temperature': 0.3
    },
    'audio': {
        'summary_tokens': 400,
        'insights_tokens': 600,
        'quiz_tokens': 700,
        'temperature': 0.3
    },
    'document': {
        'summary_tokens': 500,
        'insights_tokens': 700,
        'quiz_tokens': 800,
        'temperature': 0.2
    }
}

# --- CONFIGURAÇÕES DE CACHE ---
CACHE_SETTINGS = {
    'ttl_seconds': 3600,  # 1 hora
    'max_size_mb': 1024,  # 1GB
    'cleanup_interval_hours': 24
}

# --- RATE LIMITING ---
RATE_LIMITS = {
    'openai_requests_per_minute': 60,
    'whisper_requests_per_hour': 100,
    'file_processing_concurrent': 5
}

# --- CONFIGURAÇÕES DE SEGURANÇA ---
SECURITY_SETTINGS = {
    'max_upload_size_mb': MAX_FILE_SIZE_MB,
    'allowed_file_extensions': (
        SUPPORTED_VIDEO_FORMATS +
        SUPPORTED_AUDIO_FORMATS +
        SUPPORTED_DOCUMENT_FORMATS +
        SUPPORTED_SUBTITLE_FORMATS
    ),
    'scan_uploads_for_malware': False,  # Requer antivirus CLI
    'encrypt_api_keys': True
}

# --- CONFIGURAÇÕES DE PERFORMANCE ---
PERFORMANCE_SETTINGS = {
    'chunk_size_mb': 10,  # Para processamento de arquivos grandes
    'parallel_processing': True,
    'gpu_acceleration': False,  # Para Whisper e outros modelos
    'memory_limit_mb': 4096
}


def get_streamlit_config():
    """Retorna configurações otimizadas para Streamlit."""
    return {
        'theme': {
            'primaryColor': '#007bff',
            'backgroundColor': '#ffffff',
            'secondaryBackgroundColor': '#f8f9fa',
            'textColor': '#333333'
        },
        'server': {
            'maxUploadSize': MAX_FILE_SIZE_MB,
            'enableCORS': False,
            'enableWebsocketCompression': True
        },
        'browser': {
            'gatherUsageStats': ENABLE_TELEMETRY
        }
    }


def validate_config():
    """Valida configurações críticas e retorna lista de problemas."""
    issues = []

    if not OPENAI_API_KEY:
        issues.append("❌ OPENAI_API_KEY não configurada")
    elif not OPENAI_API_KEY.startswith('sk-'):
        issues.append("⚠️ OPENAI_API_KEY pode estar inválida")

    if MAX_FILE_SIZE_MB > 1000:
        issues.append("⚠️ MAX_FILE_SIZE_MB muito alto (>1GB)")

    if MAX_THREADS > 8:
        issues.append("⚠️ MAX_THREADS muito alto, pode causar problemas")

    if AI_REQUEST_TIMEOUT < 30:
        issues.append("⚠️ AI_REQUEST_TIMEOUT muito baixo")

    return issues


def get_model_costs():
    """Retorna custos estimados por modelo (USD por 1K tokens)."""
    return {
        'gpt-3.5-turbo': {'input': 0.0005, 'output': 0.0015},
        'gpt-4': {'input': 0.03, 'output': 0.06},
        'gpt-4o': {'input': 0.015, 'output': 0.03},
        'whisper': {'per_minute': 0.006}
    }


def estimate_processing_cost(content_length: int, model: str = 'gpt-3.5-turbo') -> float:
    """Estima custo de processamento baseado no comprimento do conteúdo."""
    costs = get_model_costs()

    if model not in costs:
        model = 'gpt-3.5-turbo'

    # Estimativa de tokens (aproximadamente 4 caracteres por token)
    estimated_tokens = content_length / 4

    # Custo considerando input + output
    input_cost = (estimated_tokens / 1000) * costs[model]['input']
    output_cost = (estimated_tokens * 0.3 / 1000) * \
        costs[model]['output']  # Output ~30% do input

    return input_cost + output_cost


def get_recommended_settings_for_content(content_type: str, content_size: int) -> dict:
    """Retorna configurações recomendadas baseadas no tipo e tamanho do conteúdo."""
    base_config = AI_CONFIGS.get(content_type, AI_CONFIGS['video'])

    # Ajustar baseado no tamanho
    if content_size > 50000:  # Conteúdo muito longo
        multiplier = 1.3
    elif content_size > 20000:  # Conteúdo longo
        multiplier = 1.1
    else:  # Conteúdo normal
        multiplier = 1.0

    return {
        'summary_tokens': int(base_config['summary_tokens'] * multiplier),
        'insights_tokens': int(base_config['insights_tokens'] * multiplier),
        'quiz_tokens': int(base_config['quiz_tokens'] * multiplier),
        'temperature': base_config['temperature']
    }

# --- INICIALIZAÇÃO ---


def init_config():
    """Inicializa configurações no session_state do Streamlit."""
    if 'config_initialized' not in st.session_state:
        # Configurações padrão
        st.session_state.max_tokens_summary = DEFAULT_MAX_TOKENS_SUMMARY
        st.session_state.max_tokens_insights = DEFAULT_MAX_TOKENS_INSIGHTS
        st.session_state.max_tokens_quiz = DEFAULT_MAX_TOKENS_QUIZ
        st.session_state.temperature = DEFAULT_TEMPERATURE

        # Configurações de sistema
        st.session_state.whisper_model = DEFAULT_WHISPER_MODEL
        st.session_state.whisper_language = DEFAULT_WHISPER_LANGUAGE

        # Flags
        st.session_state.config_initialized = True
        st.session_state.debug_mode = DEBUG_MODE


# Validar configuração ao importar
CONFIG_ISSUES = validate_config()

if __name__ == "__main__":
    print("🎓 NASCO Analyzer v4.0 - Configurações")
    print("="*50)

    if CONFIG_ISSUES:
        print("❌ Problemas encontrados:")
        for issue in CONFIG_ISSUES:
            print(f"  {issue}")
    else:
        print("✅ Todas as configurações OK!")

    print(f"\n📊 Configuração atual:")
    print(f"  • Modelo GPT: {DEFAULT_GPT_MODEL}")
    print(f"  • Whisper: {DEFAULT_WHISPER_MODEL}")
    print(f"  • Cache: {'Ativo' if ENABLE_CACHE else 'Inativo'}")
    print(f"  • Debug: {'Ativo' if DEBUG_MODE else 'Inativo'}")
    print(f"  • Threads: {MAX_THREADS}")
    print(f"  • Tamanho máx.: {MAX_FILE_SIZE_MB}MB")

    # Flags
    st.session_state.config_initialized = True
    st.session_state.debug_mode = DEBUG_MODE

# --- PASTAS DE OUTPUT ---
OUTPUT_FOLDERS = ['analises_ia', 'relatorios', 'logs', 'backups']

# Validar configuração ao importar
CONFIG_ISSUES = validate_config()

if __name__ == "__main__":
    print("🎓 NASCO Analyzer v4.0 - Configurações")
    print("="*50)

    if CONFIG_ISSUES:
        print("❌ Problemas encontrados:")
        for issue in CONFIG_ISSUES:
            print(f"  {issue}")
    else:
        print("✅ Todas as configurações OK!")

    print(f"\n📊 Configuração atual:")
    print(f"  • Modelo GPT: {DEFAULT_GPT_MODEL}")
    print(f"  • Whisper: {DEFAULT_WHISPER_MODEL}")
    print(f"  • Cache: {'Ativo' if ENABLE_CACHE else 'Inativo'}")
    print(f"  • Debug: {'Ativo' if DEBUG_MODE else 'Inativo'}")
    print(f"  • Threads: {MAX_THREADS}")
    print(f"  • Tamanho máx.: {MAX_FILE_SIZE_MB}MB")
