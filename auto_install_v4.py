#!/usr/bin/env python3
"""
🎓 INSTALADOR AUTOMÁTICO v4.0 ULTIMATE - NASCO ANALYZER
Instala e configura automaticamente a versão 4.0 ULTIMATE
"""

import sys
import os
import subprocess
import platform
from pathlib import Path
import shutil


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{title.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'='*60}{Colors.END}")


def print_success(message):
    print(f"{Colors.GREEN}✅ {message}{Colors.END}")


def print_error(message):
    print(f"{Colors.RED}❌ {message}{Colors.END}")


def print_warning(message):
    print(f"{Colors.YELLOW}⚠️ {message}{Colors.END}")


def print_info(message):
    print(f"{Colors.CYAN}ℹ️ {message}{Colors.END}")


def run_command(command, description, check_return_code=True):
    """Executa comando e retorna resultado."""
    print_info(f"Executando: {description}")

    try:
        if isinstance(command, str):
            result = subprocess.run(
                command, shell=True, capture_output=True, text=True)
        else:
            result = subprocess.run(command, capture_output=True, text=True)

        if check_return_code and result.returncode != 0:
            print_error(f"Erro: {result.stderr}")
            return False

        print_success(description)
        return True
    except Exception as e:
        print_error(f"Erro ao executar {description}: {e}")
        return False


def check_python_version():
    """Verifica versão do Python."""
    print_header("🐍 VERIFICANDO PYTHON")

    version = sys.version_info
    if version.major >= 3 and version.minor >= 8:
        print_success(
            f"Python {version.major}.{version.minor}.{version.micro} ✓")
        return True
    else:
        print_error(f"Python {version.major}.{version.minor} é muito antigo")
        print_error("Versão mínima: Python 3.8")
        return False


def install_ffmpeg():
    """Instala FFmpeg baseado no sistema operacional."""
    print_header("🎬 INSTALANDO FFMPEG")

    system = platform.system().lower()

    # Verificar se já está instalado
    if run_command(['ffmpeg', '-version'], "Verificando FFmpeg existente", False):
        print_success("FFmpeg já está instalado")
        return True

    print_info("FFmpeg não encontrado. Tentando instalar...")

    if system == "windows":
        print_info("Sistema Windows detectado")
        # Tentar Chocolatey
        if run_command(['choco', '--version'], "Verificando Chocolatey", False):
            return run_command(['choco', 'install', 'ffmpeg', '-y'], "Instalando FFmpeg via Chocolatey")
        else:
            print_warning("Chocolatey não encontrado")
            print_info("Por favor, instale FFmpeg manualmente:")
            print_info("1. Baixe de: https://ffmpeg.org/download.html")
            print_info("2. Extraia e adicione ao PATH")
            return False

    elif system == "darwin":  # macOS
        print_info("Sistema macOS detectado")
        # Tentar Homebrew
        if run_command(['brew', '--version'], "Verificando Homebrew", False):
            return run_command(['brew', 'install', 'ffmpeg'], "Instalando FFmpeg via Homebrew")
        else:
            print_warning("Homebrew não encontrado")
            print_info(
                "Instale Homebrew primeiro: /bin/bash -c \"$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\"")
            return False

    elif system == "linux":
        print_info("Sistema Linux detectado")
        # Tentar apt (Ubuntu/Debian)
        if run_command(['which', 'apt'], "Verificando apt", False):
            run_command(['sudo', 'apt', 'update'], "Atualizando apt")
            return run_command(['sudo', 'apt', 'install', '-y', 'ffmpeg'], "Instalando FFmpeg via apt")
        # Tentar yum (CentOS/RHEL)
        elif run_command(['which', 'yum'], "Verificando yum", False):
            return run_command(['sudo', 'yum', 'install', '-y', 'ffmpeg'], "Instalando FFmpeg via yum")
        else:
            print_warning("Gerenciador de pacotes não reconhecido")
            print_info("Instale FFmpeg manualmente para sua distribuição")
            return False

    else:
        print_error(f"Sistema operacional não suportado: {system}")
        return False


def create_virtual_env():
    """Cria ambiente virtual."""
    print_header("🏗️ CRIANDO AMBIENTE VIRTUAL")

    venv_path = Path('venv_nasco_v4')

    if venv_path.exists():
        print_warning("Ambiente virtual já existe")
        return True

    return run_command([sys.executable, '-m', 'venv', str(venv_path)], "Criando ambiente virtual")


def activate_virtual_env():
    """Ativa ambiente virtual."""
    print_header("🔌 ATIVANDO AMBIENTE VIRTUAL")

    venv_path = Path('venv_nasco_v4')

    if platform.system().lower() == "windows":
        activate_script = venv_path / 'Scripts' / 'activate.bat'
        python_exe = venv_path / 'Scripts' / 'python.exe'
    else:
        activate_script = venv_path / 'bin' / 'activate'
        python_exe = venv_path / 'bin' / 'python'

    if python_exe.exists():
        print_success("Ambiente virtual encontrado")
        print_info(f"Para ativar manualmente:")
        if platform.system().lower() == "windows":
            print_info(f"  {venv_path}\\Scripts\\activate")
        else:
            print_info(f"  source {venv_path}/bin/activate")
        return str(python_exe)
    else:
        print_error("Ambiente virtual não encontrado ou corrompido")
        return None


def install_dependencies(python_exe):
    """Instala dependências."""
    print_header("📦 INSTALANDO DEPENDÊNCIAS")

    # Atualizar pip
    if not run_command([python_exe, '-m', 'pip', 'install', '--upgrade', 'pip'], "Atualizando pip"):
        return False

    # Instalar requirements
    requirements_path = Path('requirements.txt')
    if requirements_path.exists():
        return run_command([python_exe, '-m', 'pip', 'install', '-r', 'requirements.txt'], "Instalando dependências")
    else:
        print_error("requirements.txt não encontrado")
        print_info("Instalando dependências essenciais...")

        essential_packages = [
            'streamlit>=1.28.0',
            'openai>=1.3.0',
            'openai-whisper>=20231117',
            'moviepy>=1.0.3',
            'PyMuPDF>=1.23.0',
            'python-docx>=0.8.11',
            'python-pptx>=0.6.21',
            'python-dotenv>=1.0.0',
            'pandas>=2.0.0',
            'numpy>=1.24.0'
        ]

        for package in essential_packages:
            if not run_command([python_exe, '-m', 'pip', 'install', package], f"Instalando {package.split('>=')[0]}"):
                print_warning(f"Falha ao instalar {package}")

        return True


def setup_configuration():
    """Configura arquivo .env."""
    print_header("⚙️ CONFIGURANDO AMBIENTE")

    env_template = Path('.env.template')
    env_file = Path('.env')

    if env_file.exists():
        print_success("Arquivo .env já existe")
        return True

    if env_template.exists():
        shutil.copy(env_template, env_file)
        print_success("Arquivo .env criado a partir do template")
    else:
        # Criar .env básico
        env_content = """# NASCO Analyzer v4.0 ULTIMATE - Configuração
OPENAI_API_KEY=sk-proj-INSIRA_SUA_CHAVE_AQUI
DEFAULT_GPT_MODEL=gpt-3.5-turbo
DEFAULT_TEMPERATURE=0.3
DEFAULT_WHISPER_MODEL=small
ENABLE_CACHE=true
DEBUG_MODE=false
"""
        env_file.write_text(env_content)
        print_success("Arquivo .env criado com configurações padrão")

    print_warning("IMPORTANTE: Configure sua OPENAI_API_KEY no arquivo .env")
    print_info("1. Abra o arquivo .env em um editor de texto")
    print_info("2. Substitua 'INSIRA_SUA_CHAVE_AQUI' pela sua API key")
    print_info("3. Obtenha sua chave em: https://platform.openai.com/api-keys")

    return True


def create_directory_structure():
    """Cria estrutura de diretórios."""
    print_header("📁 CRIANDO ESTRUTURA DE PASTAS")

    directories = [
        'video_analyzer',
        'video_analyzer/v4',
        'logs',
        'backups'
    ]

    for directory in directories:
        dir_path = Path(directory)
        dir_path.mkdir(exist_ok=True)
        print_success(f"Pasta criada: {directory}")

    return True


def run_validation(python_exe):
    """Executa validação da instalação."""
    print_header("✅ VALIDANDO INSTALAÇÃO")

    # Executar setup_validator se existir
    validator_path = Path('setup_validator.py')
    if validator_path.exists():
        print_info("Executando validação completa...")
        return run_command([python_exe, 'setup_validator.py'], "Validação completa", False)
    else:
        print_warning("setup_validator.py não encontrado")
        print_info("Executando validação básica...")

        # Validação básica
        basic_tests = [
            ('streamlit', 'Streamlit'),
            ('openai', 'OpenAI'),
            ('whisper', 'Whisper'),
            ('fitz', 'PyMuPDF')
        ]

        all_good = True
        for module, name in basic_tests:
            test_command = [python_exe, '-c',
                            f'import {module}; print("{name} OK")']
            if run_command(test_command, f"Testando {name}", False):
                print_success(f"{name} importado com sucesso")
            else:
                print_error(f"Erro ao importar {name}")
                all_good = False

        return all_good


def print_final_instructions(python_exe):
    """Imprime instruções finais."""
    print_header("🎉 INSTALAÇÃO CONCLUÍDA")

    venv_path = Path('venv_nasco_v4')

    print_success("NASCO Analyzer v4.0 ULTIMATE instalado com sucesso!")
    print()

    print_info("📋 PRÓXIMOS PASSOS:")
    print()

    print("1️⃣ Ativar ambiente virtual:")
    if platform.system().lower() == "windows":
        print(f"   {venv_path}\\Scripts\\activate")
    else:
        print(f"   source {venv_path}/bin/activate")
    print()

    print("2️⃣ Configurar API OpenAI:")
    print("   - Edite o arquivo .env")
    print("   - Configure sua OPENAI_API_KEY")
    print()

    print("3️⃣ Executar aplicação:")
    print("   cd video_analyzer/v4")
    print("   streamlit run app.py")
    print()

    print("4️⃣ Acessar interface:")
    print("   http://localhost:8501")
    print()

    print_info("🔧 COMANDOS ÚTEIS:")
    print("   Validar instalação: python setup_validator.py")
    print("   Testar v4.0: python validade_v4_ultimate.py")
    print("   Ver configurações: python video_analyzer/v4/config.py")


def main():
    """Função principal do instalador."""
    print_header("🎓 INSTALADOR AUTOMÁTICO v4.0 ULTIMATE")

    print_info("Este script irá:")
    print_info("• Verificar Python 3.8+")
    print_info("• Instalar FFmpeg (se possível)")
    print_info("• Criar ambiente virtual")
    print_info("• Instalar dependências Python")
    print_info("• Configurar arquivos básicos")
    print_info("• Validar instalação")
    print()

    # Confirmar instalação
    response = input("Continuar com a instalação? (s/N): ").strip().lower()
    if response not in ['s', 'sim', 'y', 'yes']:
        print_info("Instalação cancelada pelo usuário")
        return False

    # Executar passos de instalação
    steps = [
        ("Verificação Python", check_python_version),
        ("Instalação FFmpeg", install_ffmpeg),
        ("Criação do ambiente virtual", create_virtual_env),
        ("Estrutura de pastas", create_directory_structure),
        ("Configuração inicial", setup_configuration)
    ]

    for step_name, step_func in steps:
        print_header(f"🔄 {step_name}")
        if not step_func():
            print_error(f"Falha na etapa: {step_name}")
            return False

    # Ativar ambiente e instalar dependências
    python_exe = activate_virtual_env()
    if not python_exe:
        return False

    if not install_dependencies(python_exe):
        print_error("Falha na instalação de dependências")
        return False

    # Validação final
    if run_validation(python_exe):
        print_final_instructions(python_exe)
        return True
    else:
        print_error("Validação falhou - verifique os erros acima")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
