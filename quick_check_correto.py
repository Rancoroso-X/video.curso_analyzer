#!/usr/bin/env python3
"""
🎓 VERIFICAÇÃO RÁPIDA - ESTRUTURA CORRETA - NASCO v4.0 ULTIMATE
"""

import sys
import os
from pathlib import Path
import subprocess


def quick_test_correct():
    """Teste rápido com estrutura correta."""
    print("🎓 NASCO v4.0 ULTIMATE - Verificação Estrutura Correta")
    print("=" * 55)

    # Verificar se estamos na pasta correta
    current_path = Path.cwd()
    print(f"📁 Pasta atual: {current_path}")

    if not Path("app.py").exists():
        print("❌ app.py não encontrado na pasta atual")
        print("Execute este script na pasta: video_analyzer/APP")
        return False

    checks = []

    # 1. Python
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print(f"✅ Python {version.major}.{version.minor}")
            checks.append(True)
        else:
            print("❌ Python muito antigo")
            checks.append(False)
    except:
        print("❌ Python")
        checks.append(False)

    # 2. Ambiente virtual
    if 'VIRTUAL_ENV' in os.environ:
        venv_path = Path(os.environ['VIRTUAL_ENV'])
        print(f"✅ Ambiente virtual: {venv_path.name}")
        checks.append(True)
    else:
        print("❌ Ambiente virtual não ativo")
        checks.append(False)

    # 3. FFmpeg
    try:
        result = subprocess.run(['ffmpeg', '-version'],
                                capture_output=True, timeout=5)
        if result.returncode == 0:
            print("✅ FFmpeg")
            checks.append(True)
        else:
            print("❌ FFmpeg não responde")
            checks.append(False)
    except:
        print("❌ FFmpeg não encontrado")
        checks.append(False)

    # 4. Dependências críticas
    critical_modules = [
        ('streamlit', 'Streamlit'),
        ('openai', 'OpenAI'),
        ('moviepy.editor', 'MoviePy'),
        ('whisper', 'Whisper')
    ]

    module_ok = 0
    for module, name in critical_modules:
        try:
            __import__(module)
            print(f"✅ {name}")
            module_ok += 1
        except ImportError:
            print(f"❌ {name}")

    checks.append(module_ok == len(critical_modules))

    # 5. Arquivo .env
    if Path('.env').exists():
        print("✅ Arquivo .env")
        checks.append(True)
    else:
        print("❌ Arquivo .env não encontrado")
        checks.append(False)

    # 6. API Key
    try:
        from dotenv import load_dotenv
        load_dotenv()
        api_key = os.getenv('OPENAI_API_KEY', '')
        if api_key and api_key.startswith('sk-'):
            print("✅ API Key OpenAI")
            checks.append(True)
        else:
            print("❌ API Key não configurada")
            checks.append(False)
    except:
        print("❌ Erro ao verificar API Key")
        checks.append(False)

    # 7. Estrutura de arquivos (correta)
    required_files = ['app.py', 'analyzer.py', 'config.py']
    files_ok = sum(1 for f in required_files if Path(f).exists())

    if files_ok == len(required_files):
        print("✅ Arquivos principais")
        checks.append(True)
    else:
        print(f"❌ Arquivos principais ({files_ok}/{len(required_files)})")
        checks.append(False)

    # Resultado
    passed = sum(checks)
    total = len(checks)

    print("-" * 55)
    print(f"Resultado: {passed}/{total}")

    if passed == total:
        print("🎉 TUDO OK! Pronto para usar")
        print("▶️  Execute: streamlit run app.py")
        return True
    elif passed >= total - 1:
        print("⚠️  Quase perfeito - um problema menor")
        print("▶️  Pode tentar executar mesmo assim")
        return True
    else:
        print("❌ Problemas encontrados")
        print("🔧 Principais problemas:")
        if not checks[0]:
            print("   • Python: Atualize para 3.8+")
        if not checks[1]:
            print("   • Ambiente: source venv_nasco_v4/bin/activate")
        if not checks[2]:
            print("   • FFmpeg: brew install ffmpeg")
        if not checks[3]:
            print("   • Dependências: pip install -r requirements.txt")
        if not checks[4]:
            print("   • .env: Copie .env.template para .env")
        if not checks[5]:
            print("   • API Key: Configure no arquivo .env")

        return False


if __name__ == "__main__":
    success = quick_test_correct()
    sys.exit(0 if success else 1)
