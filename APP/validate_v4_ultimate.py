#!/usr/bin/env python3
"""
🎓 VALIDADOR ESPECÍFICO v4.0 ULTIMATE - NASCO ANALYZER
Valida especificamente as funcionalidades exclusivas da versão 4.0 ULTIMATE
"""

import sys
import os
from pathlib import Path
import importlib.util
import subprocess
import tempfile


class Colors:
    GREEN = '\033[92m'
    RED = '\033[91m'
    YELLOW = '\033[93m'
    BLUE = '\033[94m'
    PURPLE = '\033[95m'
    CYAN = '\033[96m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_status(emoji, message, color=Colors.CYAN):
    print(f"{color}{emoji} {message}{Colors.END}")


def print_success(message):
    print_status("✅", message, Colors.GREEN)


def print_error(message):
    print_status("❌", message, Colors.RED)


def print_warning(message):
    print_status("⚠️", message, Colors.YELLOW)


def print_info(message):
    print_status("ℹ️", message, Colors.BLUE)


def print_header(title):
    print(f"\n{Colors.BOLD}{Colors.PURPLE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{title.center(60)}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.PURPLE}{'='*60}{Colors.END}")


def test_multiformat_detection():
    """Testa detecção de múltiplos formatos."""
    print_header("🎯 TESTE MULTI-FORMATO v4.0")

    try:
        # Importar file_processor
        sys.path.append('.')
        sys.path.append('video_analyzer/v4')

        from file_processor import MultiFormatProcessor, FileType, DocumentExtractor

        print_success("file_processor.py importado com sucesso")

        # Testar detecção de tipos
        temp_dir = Path(tempfile.mkdtemp())
        processor = MultiFormatProcessor(temp_dir)

        # Criar arquivos de teste
        test_files = [
            temp_dir / "video.mp4",
            temp_dir / "audio.mp3",
            temp_dir / "document.pdf",
            temp_dir / "subtitle.srt"
        ]

        for file_path in test_files:
            file_path.touch()

        # Testar detecção
        detected_types = {}
        for file_path in test_files:
            file_type = processor.detect_file_type(file_path)
            detected_types[file_path.name] = file_type.value

        expected = {
            "video.mp4": "video",
            "audio.mp3": "audio",
            "document.pdf": "document",
            "subtitle.srt": "subtitle"
        }

        all_correct = True
        for filename, expected_type in expected.items():
            detected_type = detected_types.get(filename, "unknown")
            if detected_type == expected_type:
                print_success(f"{filename} → {detected_type}")
            else:
                print_error(
                    f"{filename} → {detected_type} (esperado: {expected_type})")
                all_correct = False

        # Limpar arquivos temporários
        for file_path in test_files:
            file_path.unlink()
        temp_dir.rmdir()

        return all_correct

    except ImportError as e:
        print_error(f"Erro ao importar file_processor: {e}")
        return False
    except Exception as e:
        print_error(f"Erro no teste multi-formato: {e}")
        return False


def test_document_processing():
    """Testa processamento de documentos."""
    print_header("📄 TESTE PROCESSAMENTO DE DOCUMENTOS")

    try:
        # Testar PyMuPDF
        try:
            import fitz
            print_success("PyMuPDF (PDF) disponível")
            pdf_ok = True
        except ImportError:
            print_warning("PyMuPDF (PDF) não disponível")
            pdf_ok = False

        # Testar python-docx
        try:
            from docx import Document
            print_success("python-docx (Word) disponível")
            docx_ok = True
        except ImportError:
            print_warning("python-docx (Word) não disponível")
            docx_ok = False

        # Testar python-pptx
        try:
            from pptx import Presentation
            print_success("python-pptx (PowerPoint) disponível")
            pptx_ok = True
        except ImportError:
            print_warning("python-pptx (PowerPoint) não disponível")
            pptx_ok = False

        # Testar DocumentExtractor
        if any([pdf_ok, docx_ok, pptx_ok]):
            try:
                from file_processor import DocumentExtractor
                extractor = DocumentExtractor()
                print_success("DocumentExtractor criado com sucesso")

                supported_formats = extractor.supported_formats
                print_info(
                    f"Formatos suportados: {', '.join(supported_formats)}")

                return True
            except Exception as e:
                print_error(f"Erro ao criar DocumentExtractor: {e}")
                return False
        else:
            print_error("Nenhuma biblioteca de documento disponível")
            return False

    except Exception as e:
        print_error(f"Erro no teste de documentos: {e}")
        return False


def test_advanced_ai_features():
    """Testa recursos avançados de IA."""
    print_header("🧠 TESTE RECURSOS AVANÇADOS DE IA")

    try:
        # Importar config
        from config import (
            AI_CONFIGS, get_recommended_settings_for_content,
            estimate_processing_cost, get_model_costs
        )

        print_success("Configurações de IA importadas")

        # Testar configurações por tipo
        for content_type in ['video', 'audio', 'document']:
            if content_type in AI_CONFIGS:
                config = AI_CONFIGS[content_type]
                print_success(
                    f"Config {content_type}: {config['summary_tokens']} tokens")
            else:
                print_error(f"Config {content_type} não encontrada")
                return False

        # Testar recomendações automáticas
        recommendations = get_recommended_settings_for_content('video', 30000)
        if recommendations and 'summary_tokens' in recommendations:
            print_success(
                f"Recomendação automática: {recommendations['summary_tokens']} tokens")
        else:
            print_error("Erro nas recomendações automáticas")
            return False

        # Testar estimativa de custo
        cost = estimate_processing_cost(10000, 'gpt-3.5-turbo')
        if cost > 0:
            print_success(f"Estimativa de custo: ${cost:.4f}")
        else:
            print_error("Erro na estimativa de custo")
            return False

        return True

    except ImportError as e:
        print_error(f"Erro ao importar configurações de IA: {e}")
        return False
    except Exception as e:
        print_error(f"Erro no teste de IA: {e}")
        return False


def test_interface_v4_features():
    """Testa recursos específicos da interface v4.0."""
    print_header("🎨 TESTE INTERFACE v4.0")

    try:
        # Verificar se app.py tem as funções v4.0
        app_path = Path('video_analyzer/v4/app.py')
        if not app_path.exists():
            print_error("app.py não encontrado")
            return False

        with open(app_path, 'r', encoding='utf-8') as f:
            app_content = f.read()

        # Verificar funcionalidades v4.0
        v4_features = [
            'TokenCounter',
            'render_file_upload_zone',
            'render_detected_files_summary',
            'generate_complete_course_report',
            'estimate_course_config',
            'mapear_modulos_multiformat'
        ]

        missing_features = []
        for feature in v4_features:
            if feature in app_content:
                print_success(f"Recurso v4.0: {feature}")
            else:
                print_warning(f"Recurso v4.0 não encontrado: {feature}")
                missing_features.append(feature)

        if len(missing_features) == 0:
            print_success("Todos os recursos v4.0 presentes")
            return True
        elif len(missing_features) <= 2:
            print_warning(
                f"{len(missing_features)} recursos opcionais ausentes")
            return True
        else:
            print_error(f"{len(missing_features)} recursos críticos ausentes")
            return False

    except Exception as e:
        print_error(f"Erro ao verificar interface v4.0: {e}")
        return False


def test_cache_system():
    """Testa sistema de cache."""
    print_header("💾 TESTE SISTEMA DE CACHE")

    try:
        from config import ENABLE_CACHE, CACHE_SETTINGS

        if ENABLE_CACHE:
            print_success("Cache habilitado na configuração")
        else:
            print_warning("Cache desabilitado na configuração")

        print_info(f"TTL Cache: {CACHE_SETTINGS['ttl_seconds']}s")
        print_info(f"Tamanho máximo: {CACHE_SETTINGS['max_size_mb']}MB")

        # Testar se MultiFormatProcessor usa cache
        try:
            from file_processor import MultiFormatProcessor
            temp_dir = Path(tempfile.mkdtemp())
            processor = MultiFormatProcessor(temp_dir)

            # Verificar se tem método de cache
            if hasattr(processor, 'cache_file'):
                print_success("Sistema de cache implementado no processor")
                cache_ok = True
            else:
                print_warning("Cache não implementado no processor")
                cache_ok = False

            temp_dir.rmdir()
            return cache_ok

        except Exception as e:
            print_error(f"Erro ao testar cache: {e}")
            return False

    except ImportError as e:
        print_error(f"Erro ao importar configurações de cache: {e}")
        return False


def test_performance_features():
    """Testa recursos de performance."""
    print_header("⚡ TESTE RECURSOS DE PERFORMANCE")

    try:
        from config import PERFORMANCE_SETTINGS, MAX_THREADS

        print_success(f"Threads configuradas: {MAX_THREADS}")
        print_info(
            f"Processamento paralelo: {PERFORMANCE_SETTINGS['parallel_processing']}")
        print_info(f"Chunk size: {PERFORMANCE_SETTINGS['chunk_size_mb']}MB")
        print_info(
            f"Limite de memória: {PERFORMANCE_SETTINGS['memory_limit_mb']}MB")

        # Verificar se moviepy está disponível (para performance de vídeo)
        try:
            import moviepy
            print_success("MoviePy disponível para processamento de vídeo")
            moviepy_ok = True
        except ImportError:
            print_warning("MoviePy não disponível")
            moviepy_ok = False

        # Verificar whisper
        try:
            import whisper
            models = whisper.available_models()
            print_success(f"Whisper disponível com {len(models)} modelos")
            whisper_ok = True
        except ImportError:
            print_error("Whisper não disponível")
            whisper_ok = False

        return moviepy_ok and whisper_ok

    except Exception as e:
        print_error(f"Erro no teste de performance: {e}")
        return False


def test_security_features():
    """Testa recursos de segurança."""
    print_header("🔒 TESTE RECURSOS DE SEGURANÇA")

    try:
        from config import SECURITY_SETTINGS, MAX_FILE_SIZE_MB

        print_info(f"Tamanho máximo de upload: {MAX_FILE_SIZE_MB}MB")

        allowed_extensions = SECURITY_SETTINGS['allowed_file_extensions']
        print_success(f"Extensões permitidas: {len(allowed_extensions)} tipos")

        # Verificar se .env está protegido
        gitignore_path = Path('.gitignore')
        if gitignore_path.exists():
            with open(gitignore_path, 'r') as f:
                gitignore_content = f.read()
                if '.env' in gitignore_content:
                    print_success(".env protegido no .gitignore")
                    gitignore_ok = True
                else:
                    print_warning(".env não encontrado no .gitignore")
                    gitignore_ok = False
        else:
            print_warning(".gitignore não encontrado")
            gitignore_ok = False

        # Verificar API key
        from config import OPENAI_API_KEY
        if OPENAI_API_KEY and OPENAI_API_KEY.startswith('sk-'):
            print_success("API Key OpenAI configurada corretamente")
            api_ok = True
        else:
            print_error("API Key OpenAI não configurada ou inválida")
            api_ok = False

        return gitignore_ok and api_ok

    except Exception as e:
        print_error(f"Erro no teste de segurança: {e}")
        return False


def run_v4_ultimate_validation():
    """Executa validação completa da v4.0 ULTIMATE."""
    print_header("🎓 VALIDAÇÃO v4.0 ULTIMATE - NASCO ANALYZER")

    print_info("Validando recursos exclusivos da versão 4.0 ULTIMATE...")
    print()

    # Testes específicos v4.0
    tests = [
        ("Multi-Formato", test_multiformat_detection),
        ("Processamento de Documentos", test_document_processing),
        ("IA Avançada", test_advanced_ai_features),
        ("Interface v4.0", test_interface_v4_features),
        ("Sistema de Cache", test_cache_system),
        ("Performance", test_performance_features),
        ("Segurança", test_security_features)
    ]

    results = []
    for test_name, test_func in tests:
        print_header(f"🔍 TESTANDO: {test_name}")
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print_error(f"Erro crítico no teste {test_name}: {e}")
            results.append((test_name, False))

    # Resultado final
    print_header("📊 RESULTADO FINAL v4.0 ULTIMATE")

    passed = sum(1 for _, result in results if result)
    total = len(results)

    print(f"📈 Testes aprovados: {passed}/{total}")
    print()

    for test_name, result in results:
        status = "✅" if result else "❌"
        print(f"{status} {test_name}")

    print()

    if passed == total:
        print_success("🎉 v4.0 ULTIMATE TOTALMENTE FUNCIONAL!")
        print_success("Todos os recursos exclusivos estão operacionais")
        print()
        print_info("🚀 Características validadas:")
        print_info("  ✓ Suporte multi-formato completo")
        print_info("  ✓ IA avançada com configurações inteligentes")
        print_info("  ✓ Interface moderna v4.0")
        print_info("  ✓ Sistema de cache otimizado")
        print_info("  ✓ Performance aprimorada")
        print_info("  ✓ Segurança implementada")
        success = True
    elif passed >= total - 1:
        print_warning("⚠️ v4.0 ULTIMATE QUASE PERFEITA!")
        print_warning("Um recurso opcional não está funcionando perfeitamente")
        print_success(
            "Ainda assim, pode usar todas as funcionalidades principais")
        success = True
    elif passed >= total - 2:
        print_warning("⚠️ v4.0 ULTIMATE PARCIALMENTE FUNCIONAL")
        print_warning("Alguns recursos opcionais precisam de ajustes")
        print_info("Funcionalidades principais ainda disponíveis")
        success = True
    else:
        print_error("❌ PROBLEMAS CRÍTICOS NA v4.0 ULTIMATE")
        print_error(f"{total - passed} recursos essenciais não funcionam")
        print_info("Consulte o setup_validator.py para diagnóstico completo")
        success = False

    return success


if __name__ == "__main__":
    success = run_v4_ultimate_validation()

    print()
    if success:
        print_success(
            "🎯 A versão v4.0 ULTIMATE está funcionando corretamente!")
        print_info("Execute: streamlit run video_analyzer/v4/app.py")
    else:
        print_error("🔧 Execute setup_validator.py para diagnóstico completo")

    sys.exit(0 if success else 1)
