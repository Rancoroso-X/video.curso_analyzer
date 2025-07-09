#!/usr/bin/env python3
"""
🎓 VERIFICAÇÃO RÁPIDA - NASCO v4.0 ULTIMATE
Verifica rapidamente se tudo está funcionando
"""

import sys
import os
from pathlib import Path
import subprocess


def quick_test():
    """Teste rápido de 30 segundos."""
    print("🎓 NASCO v4.0 ULTIMATE - Verificação Rápida")
    print("=" * 50)

    checks = []

    # 1. Python
    try:
        version = sys.version_info
        if version.major >= 3 and version.minor >= 8:
            print("✅ Python", f"{version.major}.{version.minor}")
            checks.append(True)
        else:
            print("❌ Python muito antigo")
            checks.append(False)
    except:
        print("❌ Python")
        checks.append(False)

    # 2. FFmpeg
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

    # 3. Dependências críticas
    critical_modules = ['streamlit', 'openai', 'whisper']
    module_ok = 0
    for module in critical_modules:
        try:
            __import__(module)
            module_ok += 1
        except ImportError:
            pass

    if module_ok == len(critical_modules):
        print("✅ Dependências críticas")
        checks.append(True)
    else:
        print(f"❌ Dependências ({module_ok}/{len(critical_modules)})")
        checks.append(False)

    # 4. Arquivo .env
    if Path('.env').exists():
        print("✅ Arquivo .env")
        checks.append(True)
    else:
        print("❌ Arquivo .env não encontrado")
        checks.append(False)

    # 5. API Key
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

    # 6. Estrutura de arquivos
    required_files = ['video_analyzer/v4/app.py',
                      'video_analyzer/v4/config.py']
    files_ok = sum(1 for f in required_files if Path(f).exists())

    if files_ok == len(required_files):
        print("✅ Arquivos v4.0")
        checks.append(True)
    else:
        print(f"❌ Arquivos v4.0 ({files_ok}/{len(required_files)})")
        checks.append(False)

    # Resultado
    passed = sum(checks)
    total = len(checks)

    print("-" * 50)
    print(f"Resultado: {passed}/{total}")

    if passed == total:
        print("🎉 TUDO OK! Pronto para usar")
        print("▶️  Execute: streamlit run video_analyzer/v4/app.py")
        return True
    elif passed >= total - 1:
        print("⚠️  Quase perfeito - um problema menor")
        print("▶️  Pode tentar executar mesmo assim")
        return True
    else:
        print("❌ Problemas encontrados")
        print("🔧 Execute: python setup_validator.py")
        return False


if __name__ == "__main__":
    success = quick_test()
    sys.exit(0 if success else 1)
