#!/usr/bin/env python3
"""
🔧 CORRETOR DE DEPENDÊNCIAS - NASCO v4.0 ULTIMATE
Resolve problemas comuns de dependências e pkg_resources
"""

import sys
import subprocess
import os
from pathlib import Path


def print_status(message, status="info"):
    """Imprime mensagem com status colorido."""
    colors = {
        "success": "\033[92m✅",
        "error": "\033[91m❌",
        "warning": "\033[93m⚠️",
        "info": "\033[94mℹ️"
    }
    print(f"{colors.get(status, '')} {message}\033[0m")


def run_command(command, description):
    """Executa comando e retorna resultado."""
    print_status(f"Executando: {description}", "info")

    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=300
        )

        if result.returncode == 0:
            print_status(f"{description} - Sucesso", "success")
            return True
        else:
            print_status(f"{description} - Erro: {result.stderr}", "error")
            return False

    except subprocess.TimeoutExpired:
        print_status(f"{description} - Timeout", "error")
        return False
    except Exception as e:
        print_status(f"{description} - Exceção: {e}", "error")
        return False


def fix_pkg_resources():
    """Corrige problemas com pkg_resources."""
    print_status("🔧 Corrigindo pkg_resources...", "info")

    # Atualizar setuptools
    commands = [
        "pip install --upgrade setuptools",
        "pip install --upgrade pip",
        "pip install --upgrade wheel",
        "pip uninstall pkg_resources -y || true",
        "pip install --upgrade setuptools --force-reinstall"
    ]

    for cmd in commands:
        run_command(cmd, f"Executando: {cmd}")


def fix_ffmpeg_python():
    """Corrige problemas com ffmpeg-python."""
    print_status("🎬 Corrigindo ffmpeg-python...", "info")

    commands = [
        "pip uninstall ffmpeg-python -y",
        "pip install ffmpeg-python --no-cache-dir",
        "pip install --upgrade ffmpeg-python"
    ]

    for cmd in commands:
        run_command(cmd, f"Executando: {cmd}")


def fix_moviepy():
    """Corrige problemas com moviepy."""
    print_status("🎥 Corrigindo moviepy...", "info")

    commands = [
        "pip uninstall moviepy -y",
        "pip uninstall imageio -y",
        "pip uninstall imageio-ffmpeg -y",
        "pip install imageio==2.31.1",
        "pip install imageio-ffmpeg==0.4.8",
        "pip install moviepy==1.0.3 --no-deps",
        "pip install decorator>=4.4.2"
    ]

    for cmd in commands:
        run_command(cmd, f"Executando: {cmd}")


def fix_numpy_compatibility():
    """Corrige problemas de compatibilidade com numpy."""
    print_status("🔢 Corrigindo numpy...", "info")

    commands = [
        "pip install 'numpy>=1.21.0,<2.0.0' --force-reinstall",
        "pip install 'scipy>=1.10.0' --force-reinstall"
    ]

    for cmd in commands:
        run_command(cmd, f"Executando: {cmd}")


def reinstall_core_packages():
    """Reinstala pacotes essenciais."""
    print_status("📦 Reinstalando pacotes essenciais...", "info")

    essential_packages = [
        "streamlit>=1.28.0",
        "openai>=1.3.0",
        "python-dotenv>=1.0.0",
        "pandas>=2.0.0",
        "requests>=2.31.0",
        "pillow>=10.0.0"
    ]

    for package in essential_packages:
        run_command(
            f"pip install '{package}' --force-reinstall", f"Reinstalando {package}")


def test_imports():
    """Testa imports críticos."""
    print_status("🧪 Testando imports...", "info")

    test_modules = [
        ("streamlit", "Streamlit"),
        ("openai", "OpenAI"),
        ("pandas", "Pandas"),
        ("numpy", "NumPy"),
        ("PIL", "Pillow"),
        ("dotenv", "Python-dotenv")
    ]

    all_good = True
    for module, name in test_modules:
        try:
            __import__(module)
            print_status(f"{name} - OK", "success")
        except ImportError as e:
            print_status(f"{name} - ERRO: {e}", "error")
            all_good = False

    return all_good


def test_optional_imports():
    """Testa imports opcionais."""
    print_status("🔍 Testando imports opcionais...", "info")

    optional_modules = [
        ("moviepy.editor", "MoviePy"),
        ("ffmpeg", "FFmpeg-python"),
        ("whisper", "OpenAI Whisper"),
        ("fitz", "PyMuPDF")
    ]

    for module, name in optional_modules:
        try:
            __import__(module)
            print_status(f"{name} - OK", "success")
        except ImportError:
            print_status(f"{name} - Não instalado (opcional)", "warning")


def create_test_script():
    """Cria script de teste rápido."""
    test_content = '''#!/usr/bin/env python3
"""Teste rápido de funcionamento."""

def test_basic():
    try:
        import streamlit as st
        import openai
        import pandas as pd
        import numpy as np
        print("✅ Imports básicos OK")
        return True
    except Exception as e:
        print(f"❌ Erro nos imports básicos: {e}")
        return False

def test_optional():
    optional_ok = 0
    total_optional = 0
    
    modules = [
        ("moviepy.editor", "MoviePy"),
        ("ffmpeg", "FFmpeg-python"), 
        ("whisper", "Whisper"),
        ("fitz", "PyMuPDF")
    ]
    
    for module, name in modules:
        total_optional += 1
        try:
            __import__(module)
            print(f"✅ {name} OK")
            optional_ok += 1
        except ImportError:
            print(f"⚠️ {name} não disponível")
    
    print(f"📊 Módulos opcionais: {optional_ok}/{total_optional}")
    return optional_ok > 0

if __name__ == "__main__":
    print("🧪 TESTE RÁPIDO - NASCO v4.0")
    print("=" * 40)
    
    basic_ok = test_basic()
    optional_ok = test_optional()
    
    if basic_ok:
        print("\\n🎉 Sistema básico funcionando!")
        print("Execute: streamlit run app.py")
    else:
        print("\\n❌ Problemas nos módulos básicos")
        print("Execute novamente: python fix_dependencies.py")
'''

    with open("quick_test.py", "w") as f:
        f.write(test_content)

    print_status("Script de teste criado: quick_test.py", "success")


def main():
    """Função principal."""
    print("🔧 CORRETOR DE DEPENDÊNCIAS - NASCO v4.0 ULTIMATE")
    print("=" * 60)

    # Verificar se está em ambiente virtual
    if not hasattr(sys, 'real_prefix') and not (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix):
        print_status("⚠️ Não está em ambiente virtual", "warning")
        print_status("Recomendado: source venv_nasco_v4/bin/activate", "info")

    # Executar correções
    steps = [
        ("Corrigindo pkg_resources", fix_pkg_resources),
        ("Corrigindo numpy", fix_numpy_compatibility),
        ("Reinstalando pacotes essenciais", reinstall_core_packages),
        ("Corrigindo ffmpeg-python", fix_ffmpeg_python),
        ("Corrigindo moviepy", fix_moviepy)
    ]

    for step_name, step_func in steps:
        print(f"\n🔄 {step_name}...")
        step_func()

    # Testes finais
    print("\n🧪 TESTES FINAIS")
    print("=" * 30)

    basic_ok = test_imports()
    test_optional_imports()

    # Criar script de teste
    create_test_script()

    # Resultado final
    print("\n" + "=" * 60)
    if basic_ok:
        print_status("🎉 CORREÇÃO CONCLUÍDA COM SUCESSO!", "success")
        print_status("Execute: python quick_test.py para verificar", "info")
        print_status("Depois: streamlit run app.py", "info")
    else:
        print_status(
            "❌ Ainda há problemas. Verifique os erros acima.", "error")
        print_status(
            "Tente: pip install --upgrade --force-reinstall -r requirements.txt", "info")


if __name__ == "__main__":
    main()
