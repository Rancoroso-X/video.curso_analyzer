# video_analyzer/v4/app.py - VERSÃO CORRIGIDA
import streamlit as st
from pathlib import Path
from analyzer import mapear_modulos, extrair_duracao
from logger import gerar_relatorios, segundos_para_hms
from transcriber import transcrever_videos, extrair_todos_audios
from llm_processor import generate_summary, generate_quiz_questions, extract_keywords_and_insights, detect_course_type
from config import OPENAI_API_KEY
from datetime import datetime
import shutil
import json
import os
import subprocess
import sys
import time

# --- Configurações da Página Streamlit ---
st.set_page_config(
    layout="wide",
    page_title="Analisador de Cursos NASCO",
    page_icon="📚",
    initial_sidebar_state="expanded"
)

# --- CSS Customizado MELHORADO ---


def load_custom_css():
    st.markdown("""
    <style>
    /* Reset e configurações base */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }
    
    /* Cards de métricas CORRIGIDOS */
    .metric-card {
        background: var(--background-color, #ffffff);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
    }
    
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.15);
    }
    
    .metric-card h3 {
        color: #1f77b4;
        margin: 0;
        font-size: 2rem;
        font-weight: 700;
    }
    
    .metric-card p {
        color: var(--text-color, #333333);
        margin: 0.5rem 0 0 0;
        font-size: 0.9rem;
        font-weight: 500;
    }
    
    /* Tema escuro */
    [data-theme="dark"] .metric-card {
        background: linear-gradient(145deg, #2b2b2b 0%, #1e1e1e 100%);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border-left: 4px solid #90caf9;
    }
    
    [data-theme="dark"] .metric-card h3 {
        color: #90caf9;
    }
    
    [data-theme="dark"] .metric-card p {
        color: #e0e0e0;
    }
    
    /* Loading overlay */
    .loading-overlay {
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background: rgba(0, 0, 0, 0.7);
        display: flex;
        justify-content: center;
        align-items: center;
        z-index: 9999;
        color: white;
        font-size: 1.2rem;
    }
    
    .loading-content {
        text-align: center;
        background: rgba(255, 255, 255, 0.1);
        padding: 2rem;
        border-radius: 12px;
        backdrop-filter: blur(10px);
    }
    
    /* Botões melhorados */
    .stButton > button {
        border-radius: 8px;
        border: none;
        padding: 0.6rem 1.2rem;
        font-weight: 600;
        transition: all 0.3s ease;
        background: linear-gradient(145deg, #007bff 0%, #0056b3 100%);
        color: white !important;
        box-shadow: 0 2px 4px rgba(0,123,255,0.3);
    }
    
    .stButton > button:hover {
        background: linear-gradient(145deg, #0056b3 0%, #004085 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,123,255,0.4);
    }
    
    /* Progress indicators */
    .progress-card {
        background: var(--background-color, #f8f9fa);
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #007bff;
        margin: 0.5rem 0;
    }
    
    [data-theme="dark"] .progress-card {
        background: #2b2b2b;
        border-left: 3px solid #90caf9;
    }
    
    /* Status indicators */
    .status-success { color: #28a745; font-weight: bold; }
    .status-warning { color: #ffc107; font-weight: bold; }
    .status-error { color: #dc3545; font-weight: bold; }
    .status-info { color: #17a2b8; font-weight: bold; }
    </style>
    """, unsafe_allow_html=True)

# --- Funções de Loading Visual ---


def show_loading_overlay(message="Carregando..."):
    """Mostra overlay de loading."""
    st.markdown(f"""
    <div class="loading-overlay" id="loading-overlay">
        <div class="loading-content">
            <div style="font-size: 3rem; margin-bottom: 1rem;">⏳</div>
            <div>{message}</div>
            <div style="margin-top: 1rem; font-size: 0.9rem; opacity: 0.8;">
                Por favor, aguarde...
            </div>
        </div>
    </div>
    <script>
    setTimeout(function() {{
        const overlay = document.getElementById('loading-overlay');
        if (overlay) overlay.style.display = 'none';
    }}, 3000);
    </script>
    """, unsafe_allow_html=True)


def hide_loading_overlay():
    """Esconde overlay de loading."""
    st.markdown("""
    <script>
    const overlay = document.getElementById('loading-overlay');
    if (overlay) overlay.style.display = 'none';
    </script>
    """, unsafe_allow_html=True)

# --- Funções Auxiliares CORRIGIDAS ---


@st.cache_data(ttl=3600, show_spinner=False)
def _load_content_from_file(file_path: Path) -> str:
    """Carrega conteúdo de arquivo com tratamento de erro melhorado."""
    try:
        if file_path.exists() and file_path.stat().st_size > 0:
            with open(file_path, "r", encoding="utf-8") as f:
                return f.read().strip()
    except Exception as e:
        st.error(f"Erro ao ler arquivo {file_path}: {e}")
    return ""


@st.cache_data(ttl=3600)
def cached_mapear_modulos(caminho: str):
    """Cache do mapeamento de módulos com loading."""
    return mapear_modulos(caminho)

# --- Funções de Migração (mantidas iguais) ---


def detect_structure_issues(base_path: Path) -> dict:
    """Detecta problemas na estrutura de pastas de IA."""
    issues = {
        'old_structure_found': [],
        'mixed_structure': False,
        'recommendations': []
    }

    analises_ia_path = base_path / "analises_ia"
    if not analises_ia_path.exists():
        return issues

    old_folders_types = ["resumos", "insights", "questionarios"]
    for folder_type in old_folders_types:
        old_path = analises_ia_path / folder_type
        if old_path.exists():
            for item in old_path.iterdir():
                if item.is_dir():
                    issues['old_structure_found'].append(folder_type)
                    break

    return issues


def migrate_old_structure(base_path: Path) -> dict:
    """Migra estrutura antiga para nova."""
    analises_ia_path = base_path / "analises_ia"
    results = {
        'migrated_files': 0,
        'errors': [],
        'summary': {}
    }

    if not analises_ia_path.exists():
        return results

    old_structure_map = {
        "resumos": "RESUMO.md",
        "insights": "INSIGHTS.md",
        "questionarios": "QUESTIONARIO.md"
    }

    for old_folder_type, filename in old_structure_map.items():
        old_base_type_path = analises_ia_path / old_folder_type

        if old_base_type_path.exists():
            file_count_for_type = 0

            try:
                for modulo_path_old_type in old_base_type_path.iterdir():
                    if modulo_path_old_type.is_dir():
                        modulo_name = modulo_path_old_type.name

                        for aula_path_old_type in modulo_path_old_type.iterdir():
                            if aula_path_old_type.is_dir():
                                aula_name = aula_path_old_type.name
                                old_file_path = aula_path_old_type / filename

                                if old_file_path.exists():
                                    new_aula_base_path = analises_ia_path / modulo_name / aula_name
                                    new_aula_base_path.mkdir(
                                        parents=True, exist_ok=True)
                                    new_file_path = new_aula_base_path / filename

                                    if not new_file_path.exists():
                                        try:
                                            shutil.move(
                                                str(old_file_path), str(new_file_path))
                                            file_count_for_type += 1
                                            results['migrated_files'] += 1
                                        except Exception as e:
                                            results['errors'].append(
                                                f"Erro ao mover {old_file_path.name}: {e}")
                                    else:
                                        os.remove(old_file_path)

                results['summary'][old_folder_type] = file_count_for_type

            except Exception as e:
                results['errors'].append(
                    f"Erro geral ao processar {old_folder_type}: {e}")

    return results

# --- Sidebar CORRIGIDA ---


def render_sidebar():
    """Sidebar com seletor de pastas corrigido e loading visual."""
    st.sidebar.markdown("## ⚙️ Configurações")

    if 'caminho_input_value' not in st.session_state:
        st.session_state.caminho_input_value = ""

    caminho_text_input = st.sidebar.text_input(
        "📁 Caminho da pasta:",
        value=st.session_state.caminho_input_value,
        placeholder="/caminho/para/seus/cursos",
        help="Cole aqui o caminho completo da pasta contendo os vídeos/transcrições do curso"
    )

    # BOTÃO SELETOR DE PASTAS CORRIGIDO
    if st.sidebar.button("📂 Abrir Seletor de Pastas"):
        with st.sidebar:
            with st.spinner("Abrindo seletor de pastas..."):
                try:
                    selected_path = ""

                    if sys.platform == 'darwin':  # macOS
                        # Comando melhorado para macOS
                        command = """
                        osascript -e '
                        try
                            set folderPath to choose folder with prompt "Selecione a pasta do curso:"
                            return POSIX path of folderPath
                        on error number -128
                            return ""
                        end try'
                        """.strip()

                        result = subprocess.run(
                            command,
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=30
                        )

                        if result.returncode == 0:
                            selected_path = result.stdout.strip()
                        else:
                            st.sidebar.error(
                                f"Erro no osascript: {result.stderr}")

                    elif sys.platform.startswith('linux'):  # Linux
                        command = "zenity --file-selection --directory --title='Selecione a pasta do curso'"
                        result = subprocess.run(
                            command,
                            shell=True,
                            capture_output=True,
                            text=True,
                            timeout=30
                        )

                        if result.returncode == 0:
                            selected_path = result.stdout.strip()

                    elif sys.platform.startswith('win'):  # Windows
                        try:
                            import tkinter as tk
                            from tkinter import filedialog

                            root = tk.Tk()
                            root.withdraw()  # Esconder janela principal
                            # Trazer para frente
                            root.attributes('-topmost', True)

                            selected_path = filedialog.askdirectory(
                                title="Selecione a pasta do curso"
                            )
                            root.destroy()

                        except ImportError:
                            st.sidebar.error(
                                "❌ tkinter não disponível no Windows")

                    if selected_path and selected_path.strip():
                        st.session_state.caminho_input_value = selected_path.strip()
                        st.sidebar.success(f"✅ Pasta selecionada!")
                        st.rerun()
                    else:
                        st.sidebar.info("ℹ️ Nenhuma pasta selecionada")

                except subprocess.TimeoutExpired:
                    st.sidebar.error("❌ Timeout ao abrir seletor de pastas")
                except FileNotFoundError:
                    st.sidebar.error("❌ Ferramenta de seleção não encontrada")
                    if sys.platform == 'darwin':
                        st.sidebar.info(
                            "💡 Instale XCode Command Line Tools: `xcode-select --install`")
                    elif sys.platform.startswith('linux'):
                        st.sidebar.info(
                            "💡 Instale zenity: `sudo apt install zenity`")
                except Exception as e:
                    st.sidebar.error(f"❌ Erro inesperado: {e}")

    # Atualizar state se usuário digitou manualmente
    if caminho_text_input != st.session_state.caminho_input_value:
        st.session_state.caminho_input_value = caminho_text_input

    # Validação em tempo real
    current_path_value = st.session_state.caminho_input_value
    if current_path_value:
        if Path(current_path_value).exists():
            st.sidebar.success("✅ Caminho válido")
        else:
            st.sidebar.error("❌ Caminho não encontrado")

    # Botões de carregamento
    col1, col2 = st.sidebar.columns([2, 1])
    with col1:
        load_button = st.sidebar.button(
            "🚀 Carregar Curso", use_container_width=True)
    with col2:
        if st.sidebar.button("🔄", help="Recarregar curso atual", key="reload_curso_btn"):
            if 'curso_path' in st.session_state:
                cached_mapear_modulos.clear()
                st.rerun()

    # PROCESSAMENTO COM LOADING
    if load_button and current_path_value:
        if Path(current_path_value).exists():
            # Mostrar loading
            progress_container = st.sidebar.empty()

            with progress_container:
                with st.spinner("🔍 Analisando pasta..."):
                    time.sleep(0.5)  # Pequeno delay para mostrar o spinner

                try:
                    # Limpar cache
                    cached_mapear_modulos.clear()

                    # Carregar curso
                    st.session_state.curso_path = current_path_value

                    with st.spinner("📊 Processando módulos..."):
                        # Testar se consegue mapear os módulos
                        test_mapping = mapear_modulos(current_path_value)

                    st.sidebar.success("✅ Curso carregado com sucesso!")
                    time.sleep(1)  # Mostrar sucesso brevemente
                    st.rerun()

                except Exception as e:
                    st.sidebar.error(f"❌ Erro ao carregar: {str(e)}")
                    progress_container.empty()

        else:
            st.sidebar.error("❌ Caminho inválido!")

    st.sidebar.markdown("---")

    # Seção de manutenção (mantida igual)
    if 'curso_path' in st.session_state and st.session_state.curso_path:
        st.sidebar.markdown("### 🔧 Manutenção")

        base_path = Path(st.session_state.curso_path)
        issues = detect_structure_issues(base_path)

        if issues['old_structure_found']:
            st.sidebar.warning(
                f"⚠️ Estrutura antiga: {', '.join(issues['old_structure_found'])}")

            if st.sidebar.button("🔄 Migrar Estrutura"):
                with st.spinner("Migrando estrutura..."):
                    results = migrate_old_structure(base_path)

                    if results['migrated_files'] > 0:
                        st.sidebar.success(
                            f"✅ {results['migrated_files']} arquivos migrados!")
                        cached_mapear_modulos.clear()
                        st.rerun()
                    else:
                        st.sidebar.info("ℹ️ Nenhum arquivo para migrar")

                    if results['errors']:
                        st.sidebar.error(f"❌ {len(results['errors'])} erros")
        else:
            st.sidebar.success("✅ Estrutura de análise atualizada")

        st.sidebar.markdown("---")

    # Configurações de IA
    st.sidebar.markdown("## 🧠 Configurações de IA")

    gpt_model = st.sidebar.selectbox(
        "Modelo GPT:",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4o"],
        index=0,
        help="💡 GPT-3.5: Rápido e econômico\n🚀 GPT-4: Melhor qualidade\n⚡ GPT-4o: Mais rápido que GPT-4"
    )

    with st.sidebar.expander("⚙️ Configurações Avançadas"):
        st.session_state.max_tokens_summary = st.slider(
            "Max Tokens Resumo", 100, 1000, 400, key="max_tokens_summary_slider")
        st.session_state.max_tokens_quiz = st.slider(
            "Max Tokens Questionário", 300, 1500, 700, key="max_tokens_quiz_slider")
        st.session_state.max_tokens_insights = st.slider(
            "Max Tokens Insights", 200, 1200, 600, key="max_tokens_insights_slider")
        st.session_state.temperature = st.slider(
            "Criatividade (Temperature)", 0.0, 1.0, 0.3, 0.1, key="temperature_slider")

    return current_path_value, gpt_model

# --- Renderização de Métricas (mantida igual) ---


def render_course_metrics(modulos_mapeados, dur_total_segundos):
    """Renderiza cards de métricas com CSS corrigido e valores corretos."""
    total_aulas_detectadas = sum(len(aulas_list)
                                 for aulas_list in modulos_mapeados.values())
    total_transcricoes_existentes = sum(1 for aulas_list in modulos_mapeados.values()
                                        for aula in aulas_list if aula.get('txt_path') and Path(aula.get('txt_path', '')).exists())
    total_videos_existentes = sum(1 for aulas_list in modulos_mapeados.values()
                                  for aula in aulas_list if aula.get('video_path'))

    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(modulos_mapeados)}</h3>
            <p>📁 Módulos</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_videos_existentes}/{total_aulas_detectadas}</h3>
            <p>🎞️ Vídeos/Aulas</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_transcricoes_existentes}/{total_aulas_detectadas}</h3>
            <p>📝 Transcrições</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{segundos_para_hms(dur_total_segundos)}</h3>
            <p>⏱️ Duração Total</p>
        </div>
        """, unsafe_allow_html=True)

# --- FUNÇÃO AUSENTE: render_action_cards ---


def render_action_cards(modulos_mapeados, base_path, curso_nome, gpt_model):
    """Renderiza cards de ação organizados."""
    st.markdown("## 🛠️ Ações Disponíveis")

    # Análise e Relatórios
    with st.expander("📊 **Análise e Relatórios**", expanded=True):
        col1, col2 = st.columns(2)
        with col1:
            if st.button("📈 Ver Resumo Detalhado", use_container_width=True):
                st.session_state.show_detailed_summary = True
        with col2:
            if st.button("📋 Gerar Relatórios (.txt/.md)", use_container_width=True):
                with st.spinner("Gerando relatórios..."):
                    video_paths = {}
                    for modulo, aulas_list in modulos_mapeados.items():
                        video_paths[modulo] = [aula['video_path']
                                               for aula in aulas_list if aula.get("video_path")]

                    if any(video_paths.values()):
                        gerar_relatorios(video_paths, base_path, curso_nome)
                        st.success("✅ Relatórios gerados!")
                    else:
                        st.warning("❌ Nenhum vídeo encontrado")

    # Processamento de Áudio/Vídeo
    with st.expander("🎙️ **Processamento de Áudio/Vídeo**", expanded=False):
        col1, col2 = st.columns(2)

        with col1:
            st.markdown("### Transcrição com Whisper")
            whisper_model = st.selectbox(
                "Modelo:", ["tiny", "base", "small", "medium", "large"], index=2)
            audio_format = st.radio("Formato:", ("mp3", "wav"))
            delete_audio = st.checkbox("🧹 Deletar áudios após transcrição")

            if st.button("🎙️ Iniciar Transcrição", use_container_width=True):
                videos_to_transcribe = {}
                for modulo, aulas_list in modulos_mapeados.items():
                    videos_to_transcribe[modulo] = [
                        aula for aula in aulas_list if aula.get("video_path")]

                if any(videos_to_transcribe.values()):
                    with st.spinner("Transcrevendo vídeos..."):
                        transcrever_videos(videos_to_transcribe, modelo=whisper_model,
                                           tipo_audio=audio_format, deletar_audio=delete_audio)
                        st.success("✅ Transcrição concluída!")
                        cached_mapear_modulos.clear()
                        st.rerun()
                else:
                    st.warning("❌ Nenhum vídeo encontrado")

        with col2:
            st.markdown("### Extração de Áudio")
            audio_extract_format = st.radio(
                "Formato de extração:", ("mp3", "wav"))

            if st.button("🎵 Extrair Áudios", use_container_width=True):
                videos_to_extract = {}
                for modulo, aulas_list in modulos_mapeados.items():
                    videos_to_extract[modulo] = [
                        aula for aula in aulas_list if aula.get("video_path")]

                if any(videos_to_extract.values()):
                    with st.spinner("Extraindo áudios..."):
                        extrair_todos_audios(
                            videos_to_extract, tipo_audio=audio_extract_format)
                        st.success("✅ Áudios extraídos!")
                else:
                    st.warning("❌ Nenhum vídeo encontrado")

# --- FUNÇÃO AUSENTE: render_ai_section ---


def render_ai_section(modulos_mapeados, base_path, gpt_model):
    """Renderiza a seção de análise de IA com botões de massa e individuais."""
    st.markdown("## ✨ Análise Inteligente (Powered by GPT)")

    if not OPENAI_API_KEY:
        st.error(
            "⚠️ Chave de API da OpenAI não configurada no arquivo .env. Funcionalidades de IA desabilitadas.")
        return

    st.info("Certifique-se de que as transcrições (.txt) já foram geradas antes de usar essas funções.")

    ai_stats = calculate_ai_stats(modulos_mapeados, base_path)
    render_ai_progress(ai_stats)

    col_regen, _ = st.columns([3, 1])
    with col_regen:
        st.session_state['force_regenerate_ia'] = st.checkbox(
            "🔄 Forçar regeração (ignorar arquivos existentes)?",
            value=st.session_state.get('force_regenerate_ia', False),
            key="force_regenerate_ia_checkbox",
            help="Se marcado, irá regenerar os arquivos de IA, sobrescrevendo os existentes."
        )

    st.markdown("### 🚀 Processamento em Lote")
    col_all_sum, col_all_ins, col_all_quiz, col_all_all = st.columns(4)

    with col_all_sum:
        if st.button("💡 Todos os Resumos", use_container_width=True, key="all_summaries_btn"):
            with st.spinner("Gerando todos os resumos..."):
                _process_all_ai_content_type(
                    modulos_mapeados, base_path, gpt_model, "resumo", generate_summary)
            st.rerun()

    with col_all_ins:
        if st.button("🔍 Todos os Insights", use_container_width=True, key="all_insights_btn"):
            with st.spinner("Gerando todos os insights..."):
                _process_all_ai_content_type(
                    modulos_mapeados, base_path, gpt_model, "insight", extract_keywords_and_insights)
            st.rerun()

    with col_all_quiz:
        if st.button("❓ Todos os Questionários", use_container_width=True, key="all_quizzes_btn"):
            with st.spinner("Gerando todos os questionários..."):
                _process_all_ai_content_type(
                    modulos_mapeados, base_path, gpt_model, "questionario", generate_quiz_questions)
            st.rerun()

    with col_all_all:
        if st.button("🎯 Gerar TUDO", use_container_width=True, key="all_in_one_btn"):
            with st.spinner("Gerando todo o conteúdo de IA..."):
                process_all_ai_content(
                    modulos_mapeados, base_path, gpt_model, st.session_state.get('curso_nome', 'Curso'))
            st.rerun()

# --- Funções auxiliares para IA ---


def calculate_ai_stats(modulos_mapeados: dict, base_path: Path) -> dict:
    """Calcula estatísticas dos arquivos de IA gerados."""
    stats = {
        'total_aulas': 0,
        'resumos_gerados': 0,
        'insights_gerados': 0,
        'questionarios_gerados': 0,
        'transcricoes_disponiveis': 0
    }

    for modulo, aulas_list in modulos_mapeados.items():
        for aula_info in aulas_list:
            aula_stem = aula_info['stem']
            stats['total_aulas'] += 1

            txt_path = Path(aula_info['txt_path']
                            ) if aula_info['txt_path'] else None
            if txt_path and txt_path.exists() and txt_path.stat().st_size > 0:
                stats['transcricoes_disponiveis'] += 1

            # Verificar arquivos de IA
            summary_path = base_path / "analises_ia" / modulo / aula_stem / "RESUMO.md"
            insights_path = base_path / "analises_ia" / modulo / aula_stem / "INSIGHTS.md"
            quiz_path = base_path / "analises_ia" / modulo / aula_stem / "QUESTIONARIO.md"

            if summary_path.exists():
                stats['resumos_gerados'] += 1
            if insights_path.exists():
                stats['insights_gerados'] += 1
            if quiz_path.exists():
                stats['questionarios_gerados'] += 1

    return stats


def render_ai_progress(ai_stats: dict):
    """Renderiza o progresso das análises de IA."""
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{ai_stats['resumos_gerados']}/{ai_stats['transcricoes_disponiveis']}</h3>
            <p>📝 Resumos</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{ai_stats['insights_gerados']}/{ai_stats['transcricoes_disponiveis']}</h3>
            <p>💡 Insights</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{ai_stats['questionarios_gerados']}/{ai_stats['transcricoes_disponiveis']}</h3>
            <p>❓ Questionários</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{ai_stats['transcricoes_disponiveis']}/{ai_stats['total_aulas']}</h3>
            <p>📄 Transcrições</p>
        </div>
        """, unsafe_allow_html=True)


def _process_all_ai_content_type(modulos_mapeados: dict, base_course_path: Path, gpt_model: str, content_type: str, generation_function):
    """Processa conteúdo de IA com verificação corrigida."""
    all_content_by_module = {}

    # Contar aulas com transcrição válida
    aulas_validas = []
    for module_name, aulas_list in modulos_mapeados.items():
        for aula_info in aulas_list:
            txt_path = Path(aula_info['txt_path']) if aula_info.get(
                'txt_path') else None
            if txt_path and txt_path.exists() and txt_path.stat().st_size > 0:
                aulas_validas.append((module_name, aula_info))

    if not aulas_validas:
        st.warning(
            f"Nenhuma transcrição válida encontrada para gerar {content_type}.")
        return None

    progress_text = st.empty()
    progress_bar = st.progress(0)

    total_aulas = len(aulas_validas)

    for idx, (module_name, aula_info) in enumerate(aulas_validas):
        if module_name not in all_content_by_module:
            all_content_by_module[module_name] = {}

        aula_stem = aula_info['stem']
        txt_path = Path(aula_info['txt_path'])

        progress_text.info(
            f"Processando {content_type}: {module_name}/{aula_stem} ({idx+1}/{total_aulas})")

        # Verificar se arquivo já existe
        check_file_path = base_course_path / "analises_ia" / \
            module_name / aula_stem / f"{content_type.upper()}.md"

        try:
            if not check_file_path.exists() or st.session_state.get('force_regenerate_ia', False):
                aula_text = _load_content_from_file(txt_path)
                if aula_text:
                    # Chama função de geração com parâmetros corretos
                    if content_type == "questionario":
                        generated_content = generation_function(
                            aula_text, aula_stem, base_course_path, module_name,
                            num_questions=5, model=gpt_model,
                            max_tokens=st.session_state.get(
                                'max_tokens_quiz', 700)
                        )
                    else:
                        generated_content = generation_function(
                            aula_text, aula_stem, base_course_path, module_name,
                            model=gpt_model,
                            max_tokens=st.session_state.get(
                                f'max_tokens_{content_type}', 400)
                        )

                    if generated_content and not generated_content.startswith("Erro:"):
                        all_content_by_module[module_name][aula_stem] = generated_content
                    else:
                        all_content_by_module[module_name][
                            aula_stem] = f"Erro: {generated_content}"
                        st.error(
                            f"❌ Erro ao gerar {content_type} para '{aula_stem}'")
                else:
                    all_content_by_module[module_name][aula_stem] = "Erro: Transcrição vazia"
            else:
                # Carregar existente
                content = _load_content_from_file(check_file_path)
                all_content_by_module[module_name][aula_stem] = content if content else "Arquivo vazio"

        except Exception as e:
            st.error(f"❌ Erro ao processar {aula_stem}: {e}")
            all_content_by_module[module_name][aula_stem] = f"Erro: {e}"

        progress_bar.progress((idx + 1) / total_aulas)

    progress_text.success(f"✅ Processamento de {content_type} concluído!")
    progress_bar.empty()

    return all_content_by_module


def process_all_ai_content(modulos_mapeados: dict, base_path: Path, gpt_model: str, course_name: str):
    """Processa todos os tipos de conteúdo de IA."""
    st.info("🚀 Iniciando geração completa de IA...")

    # Resumos
    all_summaries = _process_all_ai_content_type(
        modulos_mapeados, base_path, gpt_model, "resumo", generate_summary)

    # Insights
    all_insights = _process_all_ai_content_type(
        modulos_mapeados, base_path, gpt_model, "insight", extract_keywords_and_insights)

    # Questionários
    all_quizzes = _process_all_ai_content_type(
        modulos_mapeados, base_path, gpt_model, "questionario", generate_quiz_questions)

    st.success("✅ Geração completa de IA concluída!")
    st.session_state['force_regenerate_ia'] = False

# --- Função Principal CORRIGIDA ---


def main_app():
    """Função principal que orquestra toda a aplicação."""
    st.title("🎓 Analisador de Cursos e Vídeos.")
    st.markdown("### Análise inteligente de vídeos educacionais com IA")

    # Footer com créditos
    st.markdown("""
    <div style="position: fixed; bottom: 20px; right: 20px; 
                background: rgba(0,0,0,0.7); color: white; 
                padding: 8px 12px; border-radius: 6px; 
                font-size: 0.8rem; z-index: 999;">
        <strong>NASCO COMPANY</strong> • v4.0
    </div>
    """, unsafe_allow_html=True)

    # Renderizar sidebar e obter configurações
    current_path_value, gpt_model = render_sidebar()

    # Verificar se um curso foi carregado
    if 'curso_path' not in st.session_state:
        st.info("👆 Por favor, digite o caminho da pasta com os cursos na barra lateral e clique em 'Carregar Curso'.")
        return

    # Carregar dados do curso COM LOADING
    try:
        with st.spinner("📊 Carregando dados do curso..."):
            modulos_mapeados = cached_mapear_modulos(
                st.session_state.curso_path)

        if not modulos_mapeados:
            st.error("❌ Nenhum módulo ou vídeo encontrado no caminho especificado.")
            return

        # Extrair nome do curso do caminho
        curso_nome = Path(st.session_state.curso_path).name
        st.session_state.curso_nome = curso_nome

        # Calcular duração total COM LOADING
        with st.spinner("⏱️ Calculando durações..."):
            dur_total_segundos = 0
            for aulas_list in modulos_mapeados.values():
                for aula_info in aulas_list:
                    if aula_info.get('video_path'):
                        try:
                            duracao = extrair_duracao(aula_info['video_path'])
                            if duracao:
                                dur_total_segundos += duracao
                        except:
                            continue

        # Renderizar métricas do curso
        render_course_metrics(modulos_mapeados, dur_total_segundos)

        # Renderizar cards de ação
        render_action_cards(modulos_mapeados, Path(
            st.session_state.curso_path), curso_nome, gpt_model)

        # Renderizar seção de IA
        render_ai_section(modulos_mapeados, Path(
            st.session_state.curso_path), gpt_model)

        # Mostrar resumo detalhado se solicitado
        if st.session_state.get('show_detailed_summary', False):
            st.markdown("## 📊 Resumo Detalhado do Curso")
            for modulo, aulas_list in modulos_mapeados.items():
                with st.expander(f"📁 {modulo} ({len(aulas_list)} aulas)"):
                    for aula_info in aulas_list:
                        col1, col2, col3 = st.columns([2, 1, 1])
                        with col1:
                            st.write(f"🎥 {aula_info['stem']}")
                        with col2:
                            if aula_info.get('video_path'):
                                try:
                                    duracao = extrair_duracao(
                                        aula_info['video_path'])
                                    if duracao:
                                        st.write(
                                            f"⏱️ {segundos_para_hms(duracao)}")
                                except:
                                    st.write("⏱️ N/A")
                        with col3:
                            txt_path = Path(
                                aula_info['txt_path']) if aula_info['txt_path'] else None
                            if txt_path and txt_path.exists():
                                st.write("📝 ✅")
                            else:
                                st.write("📝 ❌")

            if st.button("🔙 Voltar", key="voltar_resumo_detalhado"):
                st.session_state.show_detailed_summary = False
                st.rerun()

    except Exception as e:
        st.error(f"❌ Erro ao processar o curso: {str(e)}")
        st.info("Verifique se o caminho está correto e contém vídeos ou transcrições.")


if __name__ == "__main__":
    load_custom_css()
    main_app()
