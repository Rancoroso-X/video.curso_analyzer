#!/usr/bin/env python3
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


def test_app_imports():
    """Testa imports específicos da aplicação."""
    try:
        from transcriber import transcrever_videos
        print("✅ transcriber OK")
    except Exception as e:
        print(f"❌ transcriber erro: {e}")
        return False

    try:
        from config import OPENAI_API_KEY
        print("✅ config OK")
    except Exception as e:
        print(f"❌ config erro: {e}")
        return False

    try:
        from analyzer import mapear_modulos
        print("✅ analyzer OK")
    except Exception as e:
        print(f"❌ analyzer erro: {e}")
        return False

    return True


if __name__ == "__main__":
    print("🧪 TESTE RÁPIDO - NASCO v4.0")
    print("=" * 40)

    basic_ok = test_basic()
    optional_ok = test_optional()
    app_ok = test_app_imports()

    print("\n" + "=" * 40)
    if basic_ok and app_ok:
        print("🎉 Sistema básico funcionando!")
        print("Execute: streamlit run app.py")
    else:
        print("❌ Problemas nos módulos básicos")
        print("Execute novamente: python fix_dependencies.py")
