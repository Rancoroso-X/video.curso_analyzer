# video_analyzer/v4/logger.py
from pathlib import Path
from analyzer import extrair_duracao
from datetime import datetime


def segundos_para_hms(segundos: float) -> str:
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    return f"{h:02}:{m:02}:{s:02}"


def gerar_relatorios(modulos: dict, base: Path, nome_curso: str = "Curso") -> None:
    linhas_md = [f"# 📘 Relatório de Curso: {nome_curso}\n"]
    linhas_md.append("## 📁 Módulos e Aulas\n")

    total_modulos = len(modulos)
    total_aulas = 0
    duracao_total = 0

    for modulo, aulas in modulos.items():
        linhas_md.append(f"### 📂 Módulo: {modulo}")
        tempo_modulo = 0
        # Aulas aqui são listas de STR de video_path, não o novo dict de aula_info
        # Assumimos que gerar_relatorios é para o relatório tradicional de VÍDEOS
        for aula_video_path_str in aulas:
            aula_video_path = Path(aula_video_path_str)
            dur = extrair_duracao(str(aula_video_path))  # Garante que é str
            tempo_modulo += dur
            duracao_total += dur
            total_aulas += 1
            nome_arquivo = aula_video_path.name
            linhas_md.append(
                f"- 🎥 {nome_arquivo} (⏱️ {segundos_para_hms(dur)})")
        linhas_md.append(
            f"\n🕒 **Duração total do módulo**: {segundos_para_hms(tempo_modulo)}\n")

    linhas_md.append("---\n")
    linhas_md.append("## 📊 Estatísticas Gerais")
    linhas_md.append(f"- Total de módulos: {total_modulos}")
    linhas_md.append(f"- Total de aulas: {total_aulas}")
    linhas_md.append(
        f"- Duração total do curso: {segundos_para_hms(duracao_total)}")

    # salvar
    relatorio_txt = base / "relatorio_curso.txt"
    relatorio_md = base / "relatorio_curso.md"
    with open(relatorio_txt, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_md))
    with open(relatorio_md, "w", encoding="utf-8") as f:
        f.write("\n".join(linhas_md))

    print(f"\n✅ Relatório gerado em: {relatorio_txt}")
    print(f"✅ Relatório salvo em: {relatorio_md}")
