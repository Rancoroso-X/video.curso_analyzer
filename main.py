# video_analyzer/v2.1/main.py
from analyzer import mapear_modulos, extrair_duracao
from logger import gerar_relatorios
from transcriber import transcrever_videos
from pathlib import Path
from datetime import datetime
import time
# Importar Progress aqui
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn, SpinnerColumn


def segundos_para_hms(segundos: float) -> str:
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    return f"{h:02}:{m:02}:{s:02}"


def exibir_resumo_breve(modulos: dict, curso_nome: str):
    total_aulas = sum(len(aulas) for aulas in modulos.values())
    dur_total = sum(extrair_duracao(aula)
                    for aulas in modulos.values() for aula in aulas)
    print(f"\n📦 Curso: {curso_nome}")
    print(f"📁 Módulos: {len(modulos)}")
    print(f"🎞️ Aulas: {total_aulas}")
    print(f"⏱️ Duração total: {segundos_para_hms(dur_total)}")
    print(
        f"🕒 Estimativa de tempo de transcrição: {segundos_para_hms(dur_total * 1.2)} (aprox. para o modelo base, Small/Faster Whisper será mais rápido).")


def exibir_resumo_completo(modulos: dict):
    duracao_total = 0
    print("\n📊 Resumo Detalhado:")
    for modulo, aulas in modulos.items():
        tempo_modulo = 0
        print(f"\n📁 {modulo} ({len(aulas)} aulas)")
        for aula in aulas:
            dur = extrair_duracao(aula)
            tempo_modulo += dur
            duracao_total += dur
            print(f"  - 🎥 {Path(aula).stem} ({segundos_para_hms(dur)})")
        print(f"  ⏱️ Tempo total do módulo: {segundos_para_hms(tempo_modulo)}")
    print(f"\n⏱️ Duração total do curso: {segundos_para_hms(duracao_total)}")


def escolher_modelo_whisper() -> str:
    print("\n🧠 Modelos Whisper disponíveis:")
    print("  tiny   = mais leve, mais rápido, menor precisão")
    print("  base   = leve e equilibrado")
    print("  small  = bom equilíbrio, mais lento  ✅ (padrão)")
    print("  medium = alta precisão, bem mais pesado")
    print("  large  = máxima precisão, bem lento 🐢")
    modelo = input(
        "Digite o modelo desejado (ou deixe em branco para usar 'small'): ").strip()
    return modelo if modelo else "small"


def main():
    print("🎬 ANALISADOR DE CURSOS 📚\n")
    caminho = input(
        "📁 Digite o caminho da pasta com os cursos: ").strip().strip("'\"")

    base = Path(caminho)
    if not base.exists():
        print("❌ Caminho inválido.")
        return

    nome_curso = base.name
    resultado = mapear_modulos(caminho)

    exibir_resumo_breve(resultado, nome_curso)

    while True:
        print("\n=== MENU ===")
        print("1. 📊 Ver resumo completo")
        print("2. 📝 Gerar relatórios .txt e .md")
        print("3. 🎙️ Transcrever vídeos com Whisper")
        print("0. 🚪 Sair")

        escolha = input("Digite sua escolha: ").strip()

        if escolha == "1":
            exibir_resumo_completo(resultado)

        elif escolha == "2":
            gerar_relatorios(resultado, base, nome_curso)

        elif escolha == "3":
            modelo = escolher_modelo_whisper()
            print("\n🔉 Escolha o formato do áudio extraído:")
            print("  1. mp3 (padrão)")
            print("  2. wav")
            while True:
                escolha_audio = input("Digite sua escolha (1 ou 2): ").strip()
                if escolha_audio == "1":
                    tipo_audio = "mp3"
                    break
                elif escolha_audio == "2":
                    tipo_audio = "wav"
                    break
                else:
                    print("Opção inválida. Por favor, digite 1 para mp3 ou 2 para wav.")

            deletar_audio = input(
                "🧹 Apagar áudios após gerar legendas/transcrição? (s/n): ").strip().lower() == 's'

            inicio = time.time()
            # Inicializa a barra de progresso da rich AQUI
            with Progress(
                SpinnerColumn(spinner_name="dots"),
                TextColumn("[progress.description]{task.description}"),
                BarColumn(),
                TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
                TimeRemainingColumn(),
                TimeElapsedColumn(),
                auto_refresh=True,
                redirect_stdout=True,
                redirect_stderr=True,
            ) as progress:
                transcrever_videos(resultado, modelo=modelo, tipo_audio=tipo_audio,
                                   deletar_audio=deletar_audio, progress=progress)

            fim = time.time()

            duracao_total = fim - inicio
            print(
                f"⏱️ Tempo total de execução: {segundos_para_hms(duracao_total)}")

        elif escolha == "0":
            print("👋 Encerrando.")
            break

        else:
            print("❌ Opção inválida.")


if __name__ == "__main__":
    main()
