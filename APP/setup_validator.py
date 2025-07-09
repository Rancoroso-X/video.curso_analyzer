#!/usr/bin/env python3
"""
🎓 ANALISADOR DE CURSOS NASCO v4.0 ULTIMATE - SETUP VALIDATOR
Verifica e valida toda a instalação automaticamente
"""

import sys
import os
import subprocess
import platform
from pathlib import Path
import importlib.util


class Colors:
    """Cores ANSI para terminal."""
    HEADER = '\033[95m'
    OKBLUE = '\033[94m'
    OKCYAN = '\033[96m'
    OKGREEN = '\033[92m'
    WARNING = '\033[93m'
    FAIL = '\033[91m'
    ENDC = '\033[0m'
    BOLD = '\033[1m'


def print_header(text):
    """Imprime cabeçalho colorido."""
    print(f"\n{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{text.center(60)}{Colors.ENDC}")
    print(f"{Colors.BOLD}{Colors.HEADER}{'='*60}{Colors.ENDC}")


def print_success(text):
    """Imprime texto de sucesso."""
    print(f"{Colors.OKGREEN}✅ {text}{Colors.ENDC}")


def print_warning(text):
    """Imprime texto de aviso."""
    print(f"{Colors.WARNING}⚠️  {text}{Colors.ENDC}")


def print_error(text):
    """Imprime texto de erro."""
    print(f"{Colors.FAIL}❌ {text}{Colors.ENDC}")


def print_info(text):
    """Imprime texto informativo."""
    print(f"{Colors.OKCYAN}ℹ️  {text}{Colors.ENDC}")


def check_python_version():
    """Verifica versão do Python."""
    print_info("Verificando versão do Python...")

    version = sys.version_info
    version_str = f"{version.major}.{version.minor}.{version.micro}"

    if version.major == 3 and version.minor >= 8:
        print_success(f"Python {version_str} ✓")
        return True
    else:
        print_error(f"Python {version_str} - Versão mínima: 3.8")
        return False


def check_pip():
    """Verifica se pip está disponível e atualizado."""
    print_info("Verificando pip...")

    try:
        import pip
        pip_version = pip.__version__
        print_success(f"pip {pip_version} ✓")
        return True
    except ImportError:
        print_error("pip não encontrado")
        return False


def check_ffmpeg():
    """Verifica se FFmpeg está instalado."""
    print_info("Verificando FFmpeg...")

    try:
        result = subprocess.run(['ffmpeg', '-version'],
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            # Extrair versão do FFmpeg
            lines = result.stdout.split('\n')
            version_line = lines[0] if lines else "Versão desconhecida"
            print_success(f"FFmpeg encontrado: {version_line[:50]}...")
            return True
        else:
            print_error("FFmpeg não responde corretamente")
            return False
    except (subprocess.TimeoutExpired, FileNotFoundError):
        print_error("FFmpeg não encontrado no PATH")
        print_info("Instale FFmpeg:")

        system = platform.system().lower()
        if system == "windows":
            print_info("  Windows: choco install ffmpeg")
            print_info("  Ou baixe de: https://ffmpeg.org/download.html")
        elif system == "darwin":  # macOS
            print_info("  macOS: brew install ffmpeg")
        elif system == "linux":
            print_info("  Ubuntu/Debian: sudo apt install ffmpeg")
            print_info("  CentOS/RHEL: sudo yum install ffmpeg")

        return False


def check_dependencies():
    """Verifica dependências críticas do Python."""
    print_info("Verificando dependências críticas...")

    critical_deps = [
        ('streamlit', 'Streamlit'),
        ('openai', 'OpenAI'),
        ('whisper', 'OpenAI Whisper'),
        ('fitz', 'PyMuPDF'),
        ('docx', 'python-docx'),
        ('pptx', 'python-pptx'),
        ('moviepy', 'MoviePy'),
        ('dotenv', 'python-dotenv'),
        ('pandas', 'Pandas'),
        ('numpy', 'NumPy')
    ]

    results = []
    for module, name in critical_deps:
        try:
            if importlib.util.find_spec(module) is not None:
                print_success(f"{name} ✓")
                results.append(True)
            else:
                print_error(f"{name} não encontrado")
                results.append(False)
        except Exception as e:
            print_error(f"{name} - Erro: {e}")
            results.append(False)

    return all(results)


def check_optional_dependencies():
    """Verifica dependências opcionais."""
    print_info("Verificando dependências opcionais...")

    optional_deps = [
        ('torch', 'PyTorch'),
        ('transformers', 'Transformers'),
        ('langchain', 'LangChain'),
        ('plotly', 'Plotly'),
        ('PIL', 'Pillow')
    ]

    for module, name in optional_deps:
        try:
            if importlib.util.find_spec(module) is not None:
                print_success(f"{name} ✓ (opcional)")
            else:
                print_warning(f"{name} não encontrado (opcional)")
        except Exception:
            print_warning(f"{name} - Erro na verificação (opcional)")


def check_env_file():
    """Verifica arquivo .env."""
    print_info("Verificando configuração (.env)...")

    env_path = Path('.env')
    env_template_path = Path('.env.template')

    if not env_template_path.exists():
        print_warning("Arquivo .env.template não encontrado")

    if env_path.exists():
        print_success("Arquivo .env encontrado")

        # Verificar se tem OPENAI_API_KEY
        try:
            with open(env_path, 'r') as f:
                content = f.read()
                if 'OPENAI_API_KEY=' in content and 'sk-' in content:
                    print_success("OPENAI_API_KEY configurada")
                    return True
                else:
                    print_warning("OPENAI_API_KEY não configurada ou inválida")
                    return False
        except Exception as e:
            print_error(f"Erro ao ler .env: {e}")
            return False
    else:
        print_error("Arquivo .env não encontrado")
        print_info("Copie .env.template para .env e configure")
        return False


def check_file_structure():
    """Verifica estrutura de arquivos."""
    print_info("Verificando estrutura de arquivos...")

    required_files = [
        'app.py',
        'file_processor.py',
        'config.py'
    ]

    all_present = True
    for file in required_files:
        if Path(file).exists():
            print_success(f"{file} ✓")
        else:
            print_error(f"{file} não encontrado")
            all_present = False

    # Verificar pastas importantes
    important_dirs = ['video_analyzer/v4']
    for dir_path in important_dirs:
        if Path(dir_path).exists():
            print_success(f"Pasta {dir_path} ✓")
        else:
            print_warning(f"Pasta {dir_path} não encontrada")

    return all_present


def check_permissions():
    """Verifica permissões de escrita."""
    print_info("Verificando permissões...")

    try:
        test_file = Path('test_write_permission.tmp')
        test_file.write_text('test')
        test_file.unlink()
        print_success("Permissões de escrita ✓")
        return True
    except Exception as e:
        print_error(f"Sem permissão de escrita: {e}")
        return False


def check_disk_space():
    """Verifica espaço em disco."""
    print_info("Verificando espaço em disco...")

    try:
        import shutil

        total, used, free = shutil.disk_usage('.')
        free_gb = free // (1024**3)

        if free_gb >= 2:
            print_success(f"Espaço livre: {free_gb}GB ✓")
            return True
        else:
            print_warning(f"Pouco espaço livre: {free_gb}GB (mínimo: 2GB)")
            return False
    except Exception as e:
        print_warning(f"Não foi possível verificar espaço: {e}")
        return True


def check_memory():
    """Verifica memória RAM disponível."""
    print_info("Verificando memória RAM...")

    try:
        import psutil

        memory = psutil.virtual_memory()
        available_gb = memory.available // (1024**3)
        total_gb = memory.total // (1024**3)

        if available_gb >= 4:
            print_success(
                f"RAM disponível: {available_gb}GB de {total_gb}GB ✓")
            return True
        elif available_gb >= 2:
            print_warning(
                f"RAM limitada: {available_gb}GB de {total_gb}GB (mínimo: 4GB)")
            return True
        else:
            print_error(f"RAM insuficiente: {available_gb}GB de {total_gb}GB")
            return False
    except ImportError:
        print_warning("psutil não instalado - não foi possível verificar RAM")
        return True
    except Exception as e:
        print_warning(f"Erro ao verificar RAM: {e}")
        return True


def test_basic_functionality():
    """Testa funcionalidades básicas."""
    print_info("Testando funcionalidades básicas...")

    try:
        # Testar importação de config
        sys.path.append('.')
        sys.path.append('video_analyzer/v4')

        try:
            import config
            print_success("Importação de config ✓")

            # Testar validação de config
            issues = config.validate_config()
            if not issues:
                print_success("Validação de configuração ✓")
            else:
                print_warning(f"Problemas na configuração: {len(issues)}")
                for issue in issues[:3]:  # Mostrar até 3 problemas
                    print_warning(f"  {issue}")

            config_ok = len(issues) == 0
        except ImportError:
            print_warning("config.py não encontrado ou com erro")
            config_ok = False

        # Testar importação Streamlit
        try:
            import streamlit
            print_success("Streamlit importado ✓")
            streamlit_ok = True
        except ImportError:
            print_error("Erro ao importar Streamlit")
            streamlit_ok = False

        # Testar importação OpenAI
        try:
            import openai
            print_success("OpenAI importado ✓")
            openai_ok = True
        except ImportError:
            print_error("Erro ao importar OpenAI")
            openai_ok = False

        return config_ok and streamlit_ok and openai_ok

    except Exception as e:
        print_error(f"Erro ao testar funcionalidades: {e}")
        return False


def test_openai_connection():
    """Testa conexão com OpenAI."""
    print_info("Testando conexão OpenAI...")

    try:
        # Importar dotenv e carregar .env
        from dotenv import load_dotenv
        load_dotenv()

        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            print_error("OPENAI_API_KEY não configurada")
            return False

        if not api_key.startswith('sk-'):
            print_error("OPENAI_API_KEY parece inválida")
            return False

        # Testar conexão básica
        import openai

        # Configurar cliente
        client = openai.OpenAI(api_key=api_key)

        # Fazer uma requisição simples
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[{"role": "user", "content": "Teste"}],
            max_tokens=5
        )

        print_success("Conexão OpenAI funcionando ✓")
        return True

    except ImportError as e:
        print_error(f"Erro de importação: {e}")
        return False
    except Exception as e:
        error_msg = str(e).lower()
        if "api key" in error_msg or "unauthorized" in error_msg:
            print_error("API Key inválida ou sem créditos")
        elif "rate limit" in error_msg:
            print_warning("Rate limit atingido - mas API key válida")
            return True
        else:
            print_error(f"Erro na conexão OpenAI: {e}")
        return False


def suggest_fixes():
    """Sugere correções para problemas comuns."""
    print_header("🔧 SUGESTÕES DE CORREÇÃO")

    print_info("Para resolver problemas comuns:")
    print()

    print("📦 Instalar dependências:")
    print("   pip install --upgrade pip")
    print("   pip install -r requirements.txt")
    print()

    print("🔧 Configurar FFmpeg:")
    system = platform.system().lower()
    if system == "windows":
        print("   choco install ffmpeg")
        print("   Ou baixar: https://ffmpeg.org/download.html")
    elif system == "darwin":
        print("   brew install ffmpeg")
    else:
        print("   sudo apt install ffmpeg  # Ubuntu/Debian")
    print()

    print("⚙️ Configurar .env:")
    print("   cp .env.template .env")
    print("   # Editar .env com sua OPENAI_API_KEY")
    print()

    print("🐍 Problema com Python:")
    print("   Usar Python 3.8+ em ambiente virtual")
    print("   python -m venv venv")
    print("   source venv/bin/activate  # Linux/macOS")
    print("   venv\\Scripts\\activate     # Windows")
    print()

    print("🔑 Configurar OpenAI:")
    print("   1. Criar conta em https://platform.openai.com")
    print("   2. Gerar API key em API Keys")
    print("   3. Adicionar créditos na conta")
    print("   4. Configurar no .env: OPENAI_API_KEY=sk-...")


def run_comprehensive_test():
    """Executa teste abrangente do sistema."""
    print_header("🧪 TESTE ABRANGENTE")

    tests = []

    # Teste de importações críticas
    print_info("Testando importações críticas...")
    critical_modules = ['streamlit', 'openai',
                        'whisper', 'moviepy', 'fitz', 'docx', 'pptx']

    for module in critical_modules:
        try:
            __import__(module)
            print_success(f"✓ {module}")
            tests.append(True)
        except ImportError:
            print_error(f"✗ {module}")
            tests.append(False)

    # Teste de funcionalidades específicas
    print_info("Testando funcionalidades específicas...")

    # Teste Whisper
    try:
        import whisper
        models = whisper.available_models()
        print_success(f"✓ Whisper - {len(models)} modelos disponíveis")
        tests.append(True)
    except Exception as e:
        print_error(f"✗ Whisper - {e}")
        tests.append(False)

    # Teste MoviePy
    try:
        from moviepy.editor import VideoFileClip
        print_success("✓ MoviePy - VideoFileClip")
        tests.append(True)
    except Exception as e:
        print_error(f"✗ MoviePy - {e}")
        tests.append(False)

    # Teste PDF
    try:
        import fitz
        print_success("✓ PyMuPDF - PDF processing")
        tests.append(True)
    except Exception as e:
        print_error(f"✗ PyMuPDF - {e}")
        tests.append(False)

    return all(tests)


def main():
    """Função principal de validação."""
    print_header("🎓 NASCO ANALYZER v4.0 ULTIMATE - SETUP VALIDATOR")

    print_info(f"Sistema: {platform.system()} {platform.release()}")
    print_info(f"Arquitetura: {platform.machine()}")
    print_info(f"Python: {sys.version}")
    print()

    # Executar todas as verificações
    checks = [
        ("Python Version", check_python_version),
        ("pip", check_pip),
        ("FFmpeg", check_ffmpeg),
        ("Dependencies", check_dependencies),
        ("Configuration", check_env_file),
        ("File Structure", check_file_structure),
        ("Permissions", check_permissions),
        ("Disk Space", check_disk_space),
        ("Memory", check_memory),
        ("Basic Functionality", test_basic_functionality),
        ("OpenAI Connection", test_openai_connection)
    ]

    results = []
    for name, check_func in checks:
        print_header(f"🔍 {name}")
        try:
            result = check_func()
            results.append((name, result))
        except Exception as e:
            print_error(f"Erro durante verificação: {e}")
            results.append((name, False))

    # Verificar dependências opcionais
    print_header("🔍 Optional Dependencies")
    check_optional_dependencies()

    # Teste abrangente
    print_header("🧪 Comprehensive Test")
    comprehensive_result = run_comprehensive_test()
    results.append(("Comprehensive Test", comprehensive_result))

    # Resumo final
    print_header("📊 RESUMO FINAL")

    critical_checks = [
        "Python Version", "Dependencies", "Configuration",
        "Basic Functionality", "OpenAI Connection"
    ]

    passed = sum(1 for name, result in results if result)
    total = len(results)
    critical_passed = sum(
        1 for name, result in results if name in critical_checks and result)
    critical_total = len(critical_checks)

    print(f"📈 Verificações passaram: {passed}/{total}")
    print(f"🎯 Verificações críticas: {critical_passed}/{critical_total}")
    print()

    for name, result in results:
        status = "✅" if result else "❌"
        critical_mark = " (CRÍTICO)" if name in critical_checks else ""
        print(f"{status} {name}{critical_mark}")

    print()

    if critical_passed == critical_total and passed >= total - 2:
        print_success("🎉 INSTALAÇÃO PERFEITA!")
        print_success("Pronto para executar: streamlit run app.py")
        print()
        print_info("💡 Comandos para iniciar:")
        print("   cd video_analyzer/v4")
        print("   streamlit run app.py")
        success = True
    elif critical_passed == critical_total:
        print_warning("⚠️ INSTALAÇÃO FUNCIONAL!")
        print_warning("Alguns recursos opcionais podem não funcionar")
        print_success("Ainda assim pode executar: streamlit run app.py")
        success = True
    else:
        print_error(f"❌ PROBLEMAS CRÍTICOS ENCONTRADOS!")
        print_error(
            f"{critical_total - critical_passed} verificação(ões) crítica(s) falharam")
        suggest_fixes()
        success = False

    return success


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
