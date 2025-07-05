# video_analyzer/v4/transcriber.py
from pathlib import Path
import os
import ffmpeg
import time
from faster_whisper import WhisperModel
from concurrent.futures import ThreadPoolExecutor
from rich.progress import Progress, BarColumn, TextColumn, TimeRemainingColumn, TimeElapsedColumn, SpinnerColumn

def extrair_audio_ffmpeg(video_path: str, tipo: str = "wav") -> Path:
    """Extrai o áudio de um arquivo de vídeo usando FFmpeg."""
    saida = Path(video_path).with_suffix(f".{tipo}")
    # Certifique-se de que o diretório de saída existe
    saida.parent.mkdir(parents=True, exist_ok=True)
    try:
        (
            ffmpeg
            .input(video_path)
            .output(str(saida), ac=1, ar='16000') # ac=1 (mono), ar='16000' (16kHz) para Whisper
            .run(overwrite_output=True, quiet=True)
        )
        return saida
    except ffmpeg.Error as e:
        print(f"Erro FFmpeg ao extrair áudio de {video_path}: {e.stderr.decode()}")
        raise # Propaga o erro

def formatar_tempo_srt(segundos: float) -> str:
    """Formata segundos em formato de tempo SRT (HH:MM:SS,ms)."""
    h = int(segundos // 3600)
    m = int((segundos % 3600) // 60)
    s = int(segundos % 60)
    ms = int((segundos - int(segundos)) * 1000)
    return f"{h:02}:{m:02}:{s:02},{ms:03}"

def salvar_transcricao(segments, texto: str, destino: Path, nome_base: str):
    """Salva a transcrição em arquivos .txt e .srt."""
    destino.mkdir(parents=True, exist_ok=True) # Garante que o diretório de destino exista

    with open(destino / f"{nome_base}.txt", "w", encoding="utf-8") as f:
        f.write(texto.strip())

    with open(destino / f"{nome_base}.srt", "w", encoding="utf-8") as f:
        for i, seg in enumerate(segments):
            ini_fmt = formatar_tempo_srt(seg.start)
            fim_fmt = formatar_tempo_srt(seg.end)
            conteudo = seg.text.strip()
            f.write(f"{i+1}\n{ini_fmt} --> {fim_fmt}\n{conteudo}\n\n")


def processar_aula_transcricao(aula_info: dict, model, tipo_audio: str, deletar_audio: bool, progress_instance: Progress, task_id):
    """Processa uma única aula para transcrição."""
    video_path_str = aula_info.get("video_path")
    if not video_path_str:
        progress_instance.update(task_id, description=f"[yellow]Skipping: {aula_info['stem']} (no video)", completed=1)
        progress_instance.advance(task_id) # Avança mesmo que pule
        return

    nome_arquivo = Path(video_path_str).name
    progress_instance.update(task_id, description=f"[cyan]🎙️ Transcrevendo: {nome_arquivo}")
    
    inicio = time.time()
    try:
        audio_path = extrair_audio_ffmpeg(video_path_str, tipo=tipo_audio)
        
        segments, info = model.transcribe(str(audio_path), language="pt", beam_size=5)
        texto = "".join([seg.text for seg in segments])

        destino = Path(video_path_str).parent # Salva no mesmo diretório do vídeo
        base = Path(video_path_str).stem
        salvar_transcricao(segments, texto, destino, base)

        if deletar_audio:
            os.remove(audio_path) # Usar os.remove para Path objects
            # audio_path.unlink() # Alternative if Path object, but os.remove is robust

        duracao = time.time() - inicio
        progress_instance.update(task_id, description=f"[green]✅ Concluído: {nome_arquivo} ({duracao:.2f}s)")

    except Exception as e:
        progress_instance.update(task_id, description=f"[red]❌ Erro em {nome_arquivo}")
        print(f"❌ Erro ao transcrever {nome_arquivo}: {e}")
    finally:
        progress_instance.advance(task_id)


def transcrever_videos(modulos: dict, modelo: str = "small", tipo_audio: str = "wav", deletar_audio: bool = False, progress: Progress = None):
    """Orquestra a transcrição de múltiplos vídeos com barra de progresso."""
    
    # Se a função for chamada sem uma instância de Progress (ex: em testes ou CLI direto), cria uma temporária.
    if progress is None:
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(), TimeElapsedColumn(), auto_refresh=True, redirect_stdout=True, redirect_stderr=True
        ) as temp_progress:
            _transcrever_videos_internal(modulos, modelo, tipo_audio, deletar_audio, temp_progress)
        return
    
    _transcrever_videos_internal(modulos, modelo, tipo_audio, deletar_audio, progress)


def _transcrever_videos_internal(modulos: dict, modelo: str, tipo_audio: str, deletar_audio: bool, progress: Progress):
    """Lógica interna de transcrição com gerenciamento de progresso."""
    loading_task_id = progress.add_task(f"[yellow]Carregando modelo Whisper otimizado: {modelo}...", start=False)
    progress.start_task(loading_task_id)

    model = WhisperModel(modelo, compute_type="auto")
    
    progress.update(loading_task_id, description=f"[green]Modelo {modelo} carregado!", completed=1)
    progress.stop_task(loading_task_id)

    # Contar apenas vídeos que realmente serão transcritos
    videos_para_transcrever = [aula_info for aulas in modulos.values() for aula_info in aulas if aula_info.get("video_path")]
    total_videos = len(videos_para_transcrever)

    if total_videos == 0:
        print("🎥 Nenhum vídeo para transcrever encontrado.")
        progress.update(loading_task_id, description=f"[green]Nenhum vídeo para transcrever encontrado.") # Atualiza a msg final se não houver vídeos
        return


    overall_task = progress.add_task("[green]Processando vídeos...", total=total_videos)

    tarefas_futures = []
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
        for aula_info in videos_para_transcrever: # Iterar apenas sobre os vídeos que serão processados
            tarefas_futures.append(executor.submit(processar_aula_transcricao, aula_info, model, tipo_audio, deletar_audio, progress, overall_task))

        for future in tarefas_futures:
            future.result()

    progress.update(overall_task, description="[green]✅ Todas as transcrições finalizadas com sucesso!")


def processar_aula_audio_extraction(aula_info: dict, tipo_audio: str, progress_instance: Progress, task_id):
    """Processa uma única aula para extração de áudio."""
    video_path_str = aula_info.get("video_path")
    if not video_path_str:
        progress_instance.update(task_id, description=f"[yellow]Skipping: {aula_info['stem']} (no video)", completed=1)
        progress_instance.advance(task_id)
        return

    nome_arquivo = Path(video_path_str).name
    progress_instance.update(task_id, description=f"[cyan]🔉 Extraindo áudio de: {nome_arquivo}")

    inicio = time.time()
    try:
        audio_path = extrair_audio_ffmpeg(video_path_str, tipo=tipo_audio)
        duracao = time.time() - inicio
        progress_instance.update(task_id, description=f"[green]✅ Áudio extraído de: {nome_arquivo} ({duracao:.2f}s)")
    except Exception as e:
        progress_instance.update(task_id, description=f"[red]❌ Erro ao extrair áudio de: {nome_arquivo}")
        print(f"❌ Erro ao extrair áudio de {nome_arquivo}: {e}")
    finally:
        progress_instance.advance(task_id)


def extrair_todos_audios(modulos: dict, tipo_audio: str = "wav", progress: Progress = None):
    """Orquestra a extração de áudio de múltiplos vídeos com barra de progresso."""
    if progress is None:
        with Progress(
            SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeRemainingColumn(), TimeElapsedColumn(), auto_refresh=True, redirect_stdout=True, redirect_stderr=True
        ) as temp_progress:
            _extrair_todos_audios_internal(modulos, tipo_audio, temp_progress)
        return
    
    _extrair_todos_audios_internal(modulos, tipo_audio, progress)


def _extrair_todos_audios_internal(modulos: dict, tipo_audio: str, progress: Progress):
    """Lógica interna de extração de áudio com gerenciamento de progresso."""
    videos_para_extrair = [aula_info for aulas in modulos.values() for aula_info in aulas if aula_info.get("video_path")]
    total_videos = len(videos_para_extrair)

    if total_videos == 0:
        print("🎥 Nenhum vídeo para extrair áudio encontrado.")
        return

    audio_extraction_task = progress.add_task("[green]Extraindo áudios...", total=total_videos)

    tarefas_futures = []
    with ThreadPoolExecutor(max_workers=os.cpu_count() or 4) as executor:
        for aula_info in videos_para_extrair:
            tarefas_futures.append(executor.submit(processar_aula_audio_extraction, aula_info, tipo_audio, progress, audio_extraction_task))
        
        for future in tarefas_futures:
            future.result()

    progress.update(audio_extraction_task, description="[green]✅ Extração de todos os áudios finalizada com sucesso!")