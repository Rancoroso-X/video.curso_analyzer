#!/usr/bin/env python3
"""
Teste simples para verificar se a transcrição está funcionando
"""

import sys
from pathlib import Path


def test_imports():
    """Testa se todas as dependências estão instaladas."""
    print("🔍 Testando imports...")

    try:
        import ffmpeg
        print("✅ ffmpeg-python: OK")
    except ImportError as e:
        print(f"❌ ffmpeg-python: {e}")
        return False

    try:
        from faster_whisper import WhisperModel
        print("✅ faster-whisper: OK")
    except ImportError as e:
        print(f"❌ faster-whisper: {e}")
        return False

    try:
        from rich.progress import Progress
        print("✅ rich: OK")
    except ImportError as e:
        print(f"❌ rich: {e}")
        return False

    return True


def test_whisper_model():
    """Testa se consegue carregar o modelo Whisper."""
    print("\n🤖 Testando modelo Whisper...")

    try:
        from faster_whisper import WhisperModel
        print("Carregando modelo 'tiny' para teste...")
        model = WhisperModel("tiny", compute_type="auto")
        print("✅ Modelo Whisper carregado com sucesso!")
        return True
    except Exception as e:
        print(f"❌ Erro ao carregar modelo Whisper: {e}")
        return False


def test_ffmpeg():
    """Testa se o FFmpeg está disponível no sistema."""
    print("\n🎵 Testando FFmpeg...")

    try:
        import subprocess
        result = subprocess.run(['ffmpeg', '-version'],
                                capture_output=True, text=True, timeout=10)
        if result.returncode == 0:
            print("✅ FFmpeg está instalado e funcionando!")
            return True
        else:
            print("❌ FFmpeg não está funcionando corretamente")
            return False
    except FileNotFoundError:
        print("❌ FFmpeg não está instalado no sistema")
        return False
    except Exception as e:
        print(f"❌ Erro ao testar FFmpeg: {e}")
        return False


def main():
    """Função principal de teste."""
    print("🎓 TESTE DE DEPENDÊNCIAS - NASCO ANALYZER v4.0")
    print("=" * 50)

    # Teste 1: Imports
    if not test_imports():
        print("\n❌ FALHA: Dependências Python não instaladas")
        print("Execute: pip install faster-whisper ffmpeg-python rich")
        return False

    # Teste 2: FFmpeg
    if not test_ffmpeg():
        print("\n❌ FALHA: FFmpeg não está disponível")
        print("Instale o FFmpeg no seu sistema:")
        print("- macOS: brew install ffmpeg")
        print("- Ubuntu: sudo apt install ffmpeg")
        print("- Windows: Baixe de https://ffmpeg.org/")
        return False

    # Teste 3: Whisper
    if not test_whisper_model():
        print("\n❌ FALHA: Modelo Whisper não pode ser carregado")
        return False

    print("\n🎉 TODOS OS TESTES PASSARAM!")
    print("✅ O sistema de transcrição está pronto para uso!")
    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
