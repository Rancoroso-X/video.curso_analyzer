# video_analyzer/v4/analyzer.py
from pathlib import Path
import os
from moviepy.editor import VideoFileClip


def extrair_duracao(video_path: str) -> float:
    """Extrai a duração de um vídeo usando moviepy."""
    try:
        clip = VideoFileClip(video_path)
        duracao = clip.duration
        clip.close()
        return duracao
    except Exception:
        # Se houver erro (ex: vídeo corrompido, formato não suportado), retorna 0
        return 0.0


def mapear_modulos(caminho_base: str) -> dict:
    """
    Mapeia a estrutura de pastas para módulos e aulas.
    Retorna um dicionário onde as chaves são nomes de módulos e os valores são listas de dicionários,
    cada um contendo os caminhos para o vídeo (.mp4), transcrição (.txt) e legenda (.srt) se existirem.
    """
    base = Path(caminho_base)
    dados = {}

    def _processar_pasta(pasta: Path, eh_modulo_raiz: bool = False):
        aulas_info = []
        processed_stems = set()  # Para evitar duplicatas ao lidar com TXT/SRT sem MP4

        # Prioriza encontrar vídeos e seus correspondentes
        for arquivo_video in sorted(pasta.glob("*.mp4")):
            stem = arquivo_video.stem
            aulas_info.append({
                "stem": stem,
                "video_path": str(arquivo_video),
                "txt_path": str(pasta / f"{stem}.txt") if (pasta / f"{stem}.txt").exists() else None,
                "srt_path": str(pasta / f"{stem}.srt") if (pasta / f"{stem}.srt").exists() else None
            })
            processed_stems.add(stem)

        # Adiciona TXT/SRT que não têm um MP4 correspondente (apenas para análise de texto)
        for arquivo_txt in sorted(pasta.glob("*.txt")):
            stem = arquivo_txt.stem
            if stem not in processed_stems:
                aulas_info.append({
                    "stem": stem,
                    "video_path": None,  # Não há vídeo
                    "txt_path": str(arquivo_txt),
                    "srt_path": str(pasta / f"{stem}.srt") if (pasta / f"{stem}.srt").exists() else None
                })
                processed_stems.add(stem)

        for arquivo_srt in sorted(pasta.glob("*.srt")):
            stem = arquivo_srt.stem
            if stem not in processed_stems:
                aulas_info.append({
                    "stem": stem,
                    "video_path": None,
                    "txt_path": str(pasta / f"{stem}.txt") if (pasta / f"{stem}.txt").exists() else None,
                    "srt_path": str(arquivo_srt)
                })
                processed_stems.add(stem)

        # Filtra para garantir que há pelo menos um tipo de arquivo relevante
        return [a for a in aulas_info if a["video_path"] or a["txt_path"] or a["srt_path"]]

    # Módulos: subpastas
    for entrada in sorted(base.iterdir()):
        if entrada.is_dir():
            nome_modulo = entrada.name
            aulas = _processar_pasta(entrada)
            if aulas:
                dados[nome_modulo] = aulas

    # Vídeos/Textos soltos na raiz (tratado como 'modulo_raiz')
    videos_raiz_info = _processar_pasta(base, eh_modulo_raiz=True)
    if videos_raiz_info:
        dados["modulo_raiz"] = videos_raiz_info

    return dados
