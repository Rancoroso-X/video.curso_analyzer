#!/usr/bin/env python3
"""
🎓 SISTEMA ORQUESTRADO COMPLETO - NASCO v4.0 ULTIMATE
Processa TUDO: Transcrição → Documentos → IA com progresso avançado
"""

import streamlit as st
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple
import json
import traceback


class ProcessingLogger:
    """Sistema de logs avançado com interface visual."""

    def __init__(self):
        if 'processing_logs' not in st.session_state:
            st.session_state.processing_logs = []

    def log(self, level: str, message: str, details: str = None):
        """Adiciona log com timestamp."""
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = {
            'timestamp': timestamp,
            'level': level,
            'message': message,
            'details': details
        }
        st.session_state.processing_logs.append(log_entry)

        # Manter apenas últimos 100 logs
        if len(st.session_state.processing_logs) > 100:
            st.session_state.processing_logs = st.session_state.processing_logs[-100:]

    def info(self, message: str, details: str = None):
        self.log("INFO", message, details)

    def warning(self, message: str, details: str = None):
        self.log("WARNING", message, details)

    def error(self, message: str, details: str = None):
        self.log("ERROR", message, details)

    def success(self, message: str, details: str = None):
        self.log("SUCCESS", message, details)

    def render_logs(self):
        """Renderiza logs na interface."""
        if not st.session_state.processing_logs:
            return

        st.markdown("### 📋 Logs de Processamento")

        # Container scrollável para logs
        with st.container():
            # Últimos 20
            for log in reversed(st.session_state.processing_logs[-20:]):
                level_colors = {
                    'INFO': '🔵',
                    'SUCCESS': '✅',
                    'WARNING': '⚠️',
                    'ERROR': '❌'
                }

                icon = level_colors.get(log['level'], '📝')
                st.text(f"{icon} {log['timestamp']} - {log['message']}")

                if log['details']:
                    st.caption(f"   └─ {log['details']}")

    def clear_logs(self):
        """Limpa todos os logs."""
        st.session_state.processing_logs = []


class AdvancedProgressTracker:
    """Rastreador de progresso avançado com estimativas de tempo."""

    def __init__(self, total_phases: int = 4):
        self.total_phases = total_phases
        self.current_phase = 1
        self.phase_names = {
            1: "🔍 Análise Inicial",
            2: "🎙️ Transcrição de Vídeos",
            3: "📄 Processamento de Documentos",
            4: "🧠 Análise de IA"
        }
        self.start_time = time.time()
        self.phase_start_time = time.time()

        # Containers para UI
        self.main_progress_container = st.empty()
        self.phase_progress_container = st.empty()
        self.details_container = st.empty()
        self.eta_container = st.empty()

    def start_phase(self, phase_num: int, total_items: int = 0):
        """Inicia uma nova fase."""
        self.current_phase = phase_num
        self.phase_start_time = time.time()
        self.total_items = total_items
        self.completed_items = 0

    def update_phase_progress(self, completed: int, current_item: str = "", eta_seconds: int = 0):
        """Atualiza progresso da fase atual."""
        self.completed_items = completed

        # Progresso geral (entre fases)
        overall_progress = (self.current_phase - 1) / self.total_phases

        # Progresso da fase atual
        if self.total_items > 0:
            phase_progress = completed / self.total_items
            overall_progress += phase_progress / self.total_phases

        # Atualizar UI
        self._render_progress(overall_progress, current_item, eta_seconds)

    def _render_progress(self, overall_progress: float, current_item: str, eta_seconds: int):
        """Renderiza interface de progresso."""

        # Barra de progresso principal
        with self.main_progress_container.container():
            st.progress(
                overall_progress, text=f"🎓 PROCESSAMENTO COMPLETO: {overall_progress*100:.0f}%")

        # Progresso da fase atual
        phase_name = self.phase_names.get(
            self.current_phase, f"Fase {self.current_phase}")

        if self.total_items > 0:
            phase_progress = self.completed_items / self.total_items
            with self.phase_progress_container.container():
                st.progress(phase_progress,
                            text=f"{phase_name}: {self.completed_items}/{self.total_items}")

        # Detalhes atuais
        if current_item:
            with self.details_container.container():
                st.info(f"🔄 Processando: {current_item}")

        # Estimativa de tempo
        if eta_seconds > 0:
            eta_str = self._format_eta(eta_seconds)
            with self.eta_container.container():
                st.caption(f"⏱️ Tempo restante estimado: {eta_str}")

    def _format_eta(self, seconds: int) -> str:
        """Formata tempo estimado em string legível."""
        if seconds < 60:
            return f"{seconds}s"
        elif seconds < 3600:
            minutes = seconds // 60
            secs = seconds % 60
            return f"{minutes}m {secs}s"
        else:
            hours = seconds // 3600
            minutes = (seconds % 3600) // 60
            return f"{hours}h {minutes}m"

    def complete(self):
        """Marca processamento como completo."""
        total_time = time.time() - self.start_time

        with self.main_progress_container.container():
            st.success(
                f"🎉 Processamento concluído em {self._format_eta(int(total_time))}")

        self.phase_progress_container.empty()
        self.details_container.empty()
        self.eta_container.empty()


class TimeEstimator:
    """Estimador inteligente de tempo de processamento."""

    @staticmethod
    def estimate_transcription_time(video_paths: List[str]) -> int:
        """Estima tempo de transcrição baseado na duração dos vídeos."""
        total_seconds = 0

        for video_path in video_paths:
            try:
                # Usar ffprobe para duração rápida
                from analyzer import extrair_duracao
                duration = extrair_duracao(video_path)
                if duration:
                    # Whisper é ~10-20% da duração real do vídeo
                    total_seconds += int(duration * 0.15)
            except:
                # Fallback: estimar 2 minutos por vídeo
                total_seconds += 120

        # Mínimo 30s por vídeo
        return max(total_seconds, len(video_paths) * 30)

    @staticmethod
    def estimate_ai_time(num_texts: int, avg_tokens_per_analysis: int = 600) -> int:
        """Estima tempo de análise de IA."""
        # ~20-40 segundos por análise dependendo do modelo e tokens
        base_time = 30  # segundos base por análise
        token_time = (avg_tokens_per_analysis / 1000) * \
            10  # ~10s por 1k tokens

        # 3 análises por texto
        return int(num_texts * 3 * (base_time + token_time))


def identify_missing_transcriptions(modulos_mapeados: Dict) -> List[Tuple[str, Dict]]:
    """Identifica vídeos que precisam de transcrição."""
    missing = []

    for module_name, aulas_list in modulos_mapeados.items():
        for aula in aulas_list:
            if aula.get('video_path'):
                txt_path = Path(aula['video_path']).with_suffix('.txt')
                if not txt_path.exists():
                    missing.append((module_name, aula))

    return missing


def update_modulos_after_transcription(modulos_mapeados: Dict, base_path: Path) -> Dict:
    """Atualiza modulos_mapeados após transcrição."""
    logger = ProcessingLogger()
    logger.info("Atualizando mapeamento após transcrição...")

    updated_count = 0
    for module_name, aulas_list in modulos_mapeados.items():
        for aula in aulas_list:
            if aula.get('video_path'):
                txt_path = Path(aula['video_path']).with_suffix('.txt')
                if txt_path.exists() and not aula.get('txt_path'):
                    aula['txt_path'] = str(txt_path)
                    updated_count += 1

    logger.success(
        f"Mapeamento atualizado: {updated_count} novos arquivos .txt")
    return modulos_mapeados


def check_cancellation() -> bool:
    """Verifica se o usuário solicitou cancelamento."""
    return st.session_state.get('cancel_processing', False)


def transcribe_videos_orchestrated(missing_transcriptions: List[Tuple[str, Dict]],
                                   progress_tracker: AdvancedProgressTracker,
                                   logger: ProcessingLogger) -> bool:
    """Transcreve vídeos com progresso avançado."""

    if not missing_transcriptions:
        logger.info("Nenhuma transcrição pendente")
        return True

    # Estimar tempo
    video_paths = [aula['video_path'] for _, aula in missing_transcriptions]
    estimated_time = TimeEstimator.estimate_transcription_time(video_paths)

    logger.info(
        f"Iniciando transcrição de {len(missing_transcriptions)} vídeos")
    logger.info(
        f"Tempo estimado: {estimated_time//60}m {estimated_time % 60}s")

    progress_tracker.start_phase(2, len(missing_transcriptions))

    # Preparar estrutura para transcrever_videos
    items_to_transcribe = {}
    for module_name, aula in missing_transcriptions:
        if module_name not in items_to_transcribe:
            items_to_transcribe[module_name] = []
        items_to_transcribe[module_name].append(aula)

    # Transcrever com progresso manual
    completed = 0
    errors = []

    for module_name, aulas_list in items_to_transcribe.items():
        for aula in aulas_list:
            if check_cancellation():
                logger.warning("Transcrição cancelada pelo usuário")
                return False

            try:
                # Atualizar progresso
                remaining_items = len(missing_transcriptions) - completed
                eta = int((remaining_items * estimated_time) /
                          len(missing_transcriptions))

                progress_tracker.update_phase_progress(
                    completed,
                    f"{aula['stem']}.mp4",
                    eta
                )

                # Usar função de transcrição existente
                from transcriber import transcrever_videos
                single_item = {module_name: [aula]}

                # Transcrever arquivo individual
                result = transcrever_videos(
                    single_item,
                    modelo=st.session_state.get('whisper_model', 'small'),
                    tipo_audio='mp3',
                    deletar_audio=True
                )

                completed += 1
                logger.success(f"Transcrito: {aula['stem']}")

            except Exception as e:
                error_msg = f"Erro ao transcrever {aula['stem']}: {str(e)}"
                logger.error(error_msg, traceback.format_exc()[:200])
                errors.append(error_msg)
                completed += 1  # Continuar mesmo com erro

    # Relatório final da transcrição
    if errors:
        logger.warning(f"Transcrição concluída com {len(errors)} erros")
        for error in errors[:5]:  # Mostrar até 5 erros
            logger.error(error)
    else:
        logger.success("Todas as transcrições concluídas com sucesso!")

    return True


def process_ai_orchestrated(modulos_mapeados: Dict, base_path: Path, gpt_model: str,
                            progress_tracker: AdvancedProgressTracker,
                            logger: ProcessingLogger) -> bool:
    """Processa análises de IA com progresso avançado."""

    # Contar itens para processar
    total_texts = 0
    for aulas_list in modulos_mapeados.values():
        for aula in aulas_list:
            if aula.get('txt_path') and Path(aula['txt_path']).exists():
                total_texts += 1

    if total_texts == 0:
        logger.warning("Nenhum texto encontrado para análise de IA")
        return True

    # Estimar tempo
    estimated_time = TimeEstimator.estimate_ai_time(total_texts)
    logger.info(f"Iniciando análise de IA para {total_texts} textos")
    logger.info(
        f"Tempo estimado: {estimated_time//60}m {estimated_time % 60}s")

    progress_tracker.start_phase(4, total_texts * 3)  # 3 análises por texto

    # Importar funções de IA
    from llm_processor import generate_summary, extract_keywords_and_insights, generate_quiz_questions

    completed_analyses = 0
    total_analyses = total_texts * 3
    errors = []

    # Processar cada texto
    for module_name, aulas_list in modulos_mapeados.items():
        for aula in aulas_list:
            if check_cancellation():
                logger.warning("Análise de IA cancelada pelo usuário")
                return False

            txt_path = aula.get('txt_path')
            if not txt_path or not Path(txt_path).exists():
                continue

            aula_stem = aula['stem']

            try:
                # Carregar texto
                with open(txt_path, 'r', encoding='utf-8') as f:
                    texto = f.read().strip()

                if not texto:
                    logger.warning(f"Arquivo vazio: {aula_stem}")
                    completed_analyses += 3
                    continue

                # 3 análises por texto
                analyses = [
                    ("Resumo", generate_summary),
                    ("Insights", extract_keywords_and_insights),
                    ("Questionário", generate_quiz_questions)
                ]

                for analysis_name, analysis_func in analyses:
                    if check_cancellation():
                        return False

                    try:
                        # Atualizar progresso
                        remaining = total_analyses - completed_analyses
                        eta = int((remaining * estimated_time) /
                                  total_analyses)

                        progress_tracker.update_phase_progress(
                            completed_analyses,
                            f"{analysis_name}: {aula_stem}",
                            eta
                        )

                        # Gerar análise
                        if analysis_name == "Questionário":
                            result = analysis_func(
                                texto, aula_stem, base_path, module_name,
                                num_questions=5, model=gpt_model
                            )
                        else:
                            result = analysis_func(
                                texto, aula_stem, base_path, module_name,
                                model=gpt_model
                            )

                        if result and not result.startswith("Erro"):
                            logger.success(
                                f"{analysis_name} gerado: {aula_stem}")
                        else:
                            logger.error(f"Falha {analysis_name}: {aula_stem}")
                            errors.append(f"{analysis_name} - {aula_stem}")

                        completed_analyses += 1
                        # Pequena pausa para não sobrecarregar API
                        time.sleep(0.1)

                    except Exception as e:
                        error_msg = f"Erro {analysis_name} {aula_stem}: {str(e)}"
                        logger.error(error_msg)
                        errors.append(error_msg)
                        completed_analyses += 1

            except Exception as e:
                error_msg = f"Erro geral ao processar {aula_stem}: {str(e)}"
                logger.error(error_msg)
                errors.append(error_msg)
                completed_analyses += 3  # Pular todas as análises deste arquivo

    # Relatório final
    if errors:
        logger.warning(f"Análise de IA concluída com {len(errors)} erros")
    else:
        logger.success("Todas as análises de IA concluídas com sucesso!")

    return True


def process_everything_orchestrated(modulos_mapeados: Dict, base_path: Path, gpt_model: str) -> bool:
    """Função principal orquestrada - GERAR TUDO COMPLETO."""

    # Inicializar componentes
    logger = ProcessingLogger()
    progress_tracker = AdvancedProgressTracker(4)

    # Container para cancelamento
    cancel_container = st.empty()

    try:
        logger.info("🚀 Iniciando processamento completo orquestrado")

        # FASE 1: ANÁLISE INICIAL
        progress_tracker.start_phase(1)
        progress_tracker.update_phase_progress(0, "Analisando arquivos...")

        missing_transcriptions = identify_missing_transcriptions(
            modulos_mapeados)

        # Mostrar botão de cancelamento
        with cancel_container.container():
            if st.button("🛑 Cancelar Processamento", key="cancel_btn", type="secondary"):
                st.session_state.cancel_processing = True

        logger.info(
            f"Encontrados {len(missing_transcriptions)} vídeos para transcrever")

        # FASE 2: TRANSCRIÇÃO (se necessário)
        if missing_transcriptions:
            success = transcribe_videos_orchestrated(
                missing_transcriptions, progress_tracker, logger
            )
            if not success:
                return False

            # Atualizar mapeamento
            modulos_mapeados = update_modulos_after_transcription(
                modulos_mapeados, base_path)

            # Invalidar cache
            from app import cached_mapear_modulos
            cached_mapear_modulos.clear()
        else:
            logger.info("Nenhuma transcrição necessária")

        # FASE 3: PROCESSAMENTO DE DOCUMENTOS (se implementado)
        progress_tracker.start_phase(3)
        progress_tracker.update_phase_progress(0, "Verificando documentos...")
        logger.info("Documentos já processados na detecção inicial")

        # FASE 4: ANÁLISE DE IA
        success = process_ai_orchestrated(
            modulos_mapeados, base_path, gpt_model, progress_tracker, logger
        )
        if not success:
            return False

        # CONCLUSÃO
        progress_tracker.complete()
        logger.success("🎉 Processamento completo finalizado com sucesso!")

        return True

    except Exception as e:
        logger.error(
            f"Erro crítico no processamento: {str(e)}", traceback.format_exc())
        return False

    finally:
        # Limpar estado de cancelamento
        if 'cancel_processing' in st.session_state:
            del st.session_state.cancel_processing
        cancel_container.empty()


def render_orchestrated_interface(modulos_mapeados: Dict, base_path: Path, gpt_model: str):
    """Renderiza interface do processamento orquestrado."""

    st.markdown("### 🚀 Processamento Completo Orquestrado")

    # Análise prévia
    missing_transcriptions = identify_missing_transcriptions(modulos_mapeados)
    total_texts = sum(1 for aulas_list in modulos_mapeados.values()
                      for aula in aulas_list
                      if aula.get('txt_path') and Path(aula['txt_path']).exists())

    # Estimativas
    transcription_time = TimeEstimator.estimate_transcription_time(
        [aula['video_path'] for _, aula in missing_transcriptions]
    ) if missing_transcriptions else 0

    ai_time = TimeEstimator.estimate_ai_time(total_texts)
    total_estimated_time = transcription_time + ai_time

    # Preview do que será processado
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "🎙️ Vídeos para Transcrever",
            len(missing_transcriptions),
            f"~{transcription_time//60}m"
        )

    with col2:
        st.metric(
            "📝 Textos para Analisar",
            total_texts,
            f"~{ai_time//60}m"
        )

    with col3:
        st.metric(
            "⏱️ Tempo Total Estimado",
            f"{total_estimated_time//60}m",
            f"{total_estimated_time % 60}s"
        )

    # Botão principal
    if st.button(
        "🎯 GERAR TUDO - Processamento Completo",
        use_container_width=True,
        type="primary",
        help="Transcreve vídeos pendentes + Gera todas as análises de IA"
    ):
        if total_estimated_time > 600:  # Mais de 10 minutos
            st.warning(
                f"⚠️ Processamento estimado: {total_estimated_time//60} minutos. Recomendado não fechar o navegador.")

        success = process_everything_orchestrated(
            modulos_mapeados, base_path, gpt_model)

        if success:
            st.balloons()
            st.success(
                "🎉 Processamento completo finalizado! Verifique os logs para detalhes.")
        else:
            st.error(
                "❌ Processamento interrompido. Verifique os logs para detalhes.")

    # Renderizar logs sempre
    logger = ProcessingLogger()
    logger.render_logs()

    # Botão para limpar logs
    if st.button("🧹 Limpar Logs", key="clear_logs_btn"):
        logger.clear_logs()
        st.rerun()
