# video_analyzer/v4/app.py - VERSÃO 4.0 ULTIMATE FINAL
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
import re

# NOVO: Para processamento multi-formato e outras utilidades
# Certifique-se de que este arquivo existe e contém as classes e funções
# mencionadas: MultiFormatProcessor, DocumentExtractor, FileType, mapear_modulos_multiformat
# render_file_upload_zone, render_detected_files_summary, check_dependencies, format_file_size
# Se você não tiver file_processor.py ou ele não estiver completo, este import falhará.
from file_processor import (
    MultiFormatProcessor,
    DocumentExtractor,
    FileType,
    mapear_modulos_multiformat,
    render_file_upload_zone,
    render_detected_files_summary,
    check_dependencies,
    format_file_size
)

# Import da interface orquestrada
try:
    from orchestrated_processor import render_orchestrated_interface
    ORCHESTRATED_AVAILABLE = True
except ImportError:
    ORCHESTRATED_AVAILABLE = False

    def render_orchestrated_interface(*args, **kwargs):
        st.warning(
            "⚠️ Interface orquestrada não disponível. Verifique se orchestrated_processor.py existe.")

# --- Configurações da Página Streamlit ---
st.set_page_config(
    layout="wide",
    page_title="Analisador de Cursos",
    page_icon="🎓",
    initial_sidebar_state="expanded"
)

# --- Sistema de Contagem de Tokens Avançado ---


class TokenCounter:
    def __init__(self):
        if 'token_usage' not in st.session_state:
            st.session_state.token_usage = {
                'total_tokens': 0,
                'resumos': 0,
                'insights': 0,
                'questionarios': 0,
                'relatorio_completo': 0,
                'estimated_cost': 0.0,
                'session_start': datetime.now().isoformat(),
                'daily_usage': {}
            }

    def add_tokens(self, category: str, tokens: int, model: str = "gpt-3.5-turbo"):
        """Adiciona tokens usados por categoria com custo por modelo."""
        st.session_state.token_usage[category] += tokens
        st.session_state.token_usage['total_tokens'] += tokens

        model_costs = {
            'gpt-3.5-turbo': 0.002,  # Custo de output
            'gpt-4': 0.03,        # Custo de output
            'gpt-4o': 0.015       # Custo de output
        }
        # Para estimar custo, a gente geralmente soma input + output, mas aqui vamos estimar com base no output gerado
        # Ou usar uma taxa média de custo por token gerado.
        # Por simplicidade, vamos usar o custo de output por token.
        cost_per_token_generated = model_costs.get(
            model, 0.002) / 1000  # Custo por token, não por 1K tokens
        additional_cost = tokens * cost_per_token_generated
        st.session_state.token_usage['estimated_cost'] += additional_cost

        today = datetime.now().strftime('%Y-%m-%d')
        if today not in st.session_state.token_usage['daily_usage']:
            st.session_state.token_usage['daily_usage'][today] = 0
        st.session_state.token_usage['daily_usage'][today] += tokens

    def get_usage_display(self) -> str:
        """Retorna string formatada do uso de tokens."""
        usage = st.session_state.token_usage
        today = datetime.now().strftime('%Y-%m-%d')
        today_usage = usage['daily_usage'].get(today, 0)

        return f"""
        🎯 **Tokens Totais:** {usage['total_tokens']:,}
        💰 **Custo Est.:** ${usage['estimated_cost']:.3f}
        📅 **Hoje:** {today_usage:,} tokens

        **Por Categoria:**
        📝 Resumos: {usage['resumos']:,}
        💡 Insights: {usage['insights']:,}
        ❓ Quiz: {usage['questionarios']:,}
        📊 Relatório: {usage['relatorio_completo']:,}
        """

    def reset_usage(self):
        """Reseta contagem de tokens."""
        st.session_state.token_usage = {
            'total_tokens': 0,
            'resumos': 0,
            'insights': 0,
            'questionarios': 0,
            'relatorio_completo': 0,
            'estimated_cost': 0.0,
            'session_start': datetime.now().isoformat(),
            'daily_usage': {}
        }


token_counter = TokenCounter()

# --- CSS Customizado VERSÃO 4.0 ULTIMATE ---


def load_custom_css():
    st.markdown("""
    <style>
    /* Reset e configurações base */
    .block-container {
        padding-top: 2rem;
        padding-bottom: 2rem;
        max-width: 95%;
    }

    /* Cards de métricas melhorados */
    .metric-card {
        background: var(--background-color, #ffffff);
        padding: 1.5rem;
        border-radius: 12px;
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
        border-left: 4px solid #1f77b4;
        margin-bottom: 1rem;
        text-align: center;
        transition: transform 0.3s ease, box-shadow 0.3s ease;
        position: relative;
        overflow: hidden;
    }

    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 2px;
        background: linear-gradient(90deg, #1f77b4, #007bff, #17a2b8);
        animation: shimmer 2s infinite;
    }

    @keyframes shimmer {
        0% { transform: translateX(-100%); }
        100% { transform: translateX(100%); }
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

    /* Tema escuro melhorado */
    [data-theme="dark"] .metric-card {
        background: linear-gradient(145deg, #2b2b2b 0%, #1e1e1e 100%);
        box-shadow: 0 4px 12px rgba(0,0,0,0.3);
        border-left: 4px solid #90caf9;
    }

    [data-theme="dark"] .metric-card::before {
        background: linear-gradient(90deg, #90caf9, #64b5f6, #42a5f5);
    }

    [data-theme="dark"] .metric-card h3 {
        color: #90caf9;
    }

    [data-theme="dark"] .metric-card p {
        color: #e0e0e0;
    }

    /* Ícones de status interativos AVANÇADOS */
    .status-icon {
        font-size: 1.3rem;
        margin: 0 0.3rem;
        cursor: pointer;
        transition: all 0.3s ease;
        position: relative;
        display: inline-block;
    }

    .status-icon.pending {
        opacity: 0.3;
        filter: grayscale(100%);
        transform: scale(0.9);
    }

    .status-icon.completed {
        opacity: 1;
        filter: none;
        transform: scale(1);
    }

    .status-icon.resumo.completed {
        color: #28a745;
        text-shadow: 0 0 10px rgba(40, 167, 69, 0.3);
    }

    .status-icon.insights.completed {
        color: #17a2b8;
        text-shadow: 0 0 10px rgba(23, 162, 184, 0.3);
    }

    .status-icon.questionario.completed {
        color: #fd7e14;
        text-shadow: 0 0 10px rgba(253, 126, 20, 0.3);
    }

    .status-icon:hover {
        transform: scale(1.3);
        filter: brightness(1.2);
    }

    .status-icon.completed:hover::after {
        content: attr(title);
        position: absolute;
        bottom: -35px;
        left: 50%;
        transform: translateX(-50%);
        background: rgba(0, 0, 0, 0.8);
        color: white;
        padding: 0.3rem 0.6rem;
        border-radius: 4px;
        font-size: 0.7rem;
        white-space: nowrap;
        z-index: 1000;
    }

    /* Token counter sidebar melhorado */
    .token-counter {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 1rem;
        border-radius: 12px;
        margin: 1rem 0;
        font-size: 0.85rem;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        position: relative;
        overflow: hidden;
    }

    .token-counter::before {
        content: '';
        position: absolute;
        top: -2px;
        left: -2px;
        right: -2px;
        bottom: -2px;
        background: linear-gradient(45deg, #667eea, #764ba2, #667eea);
        border-radius: 12px;
        z-index: -1;
        animation: rotate 3s linear infinite;
    }

    @keyframes rotate {
        0% { transform: rotate(0deg); }
        100% { transform: rotate(360deg); }
    }

    /* Dependências status */
    .dependency-status {
        background: rgba(40, 167, 69, 0.1);
        border: 1px solid #28a745;
        color: #28a745;
        padding: 0.5rem;
        border-radius: 6px;
        margin: 0.2rem 0;
        font-size: 0.8rem;
    }

    .dependency-status.missing {
        background: rgba(220, 53, 69, 0.1);
        border-color: #dc3545;
        color: #dc3545;
    }

    /* Multi-format indicators */
    .format-indicator {
        display: inline-block;
        background: linear-gradient(135deg, #007bff, #0056b3);
        color: white;
        padding: 0.2rem 0.5rem;
        border-radius: 12px;
        font-size: 0.7rem;
        margin: 0.1rem;
        font-weight: 500;
    }

    .format-indicator.video { background: linear-gradient(135deg, #e74c3c, #c0392b); }
    .format-indicator.audio { background: linear-gradient(135deg, #f39c12, #d68910); }
    .format-indicator.document { background: linear-gradient(135deg, #3498db, #2980b9); }
    .format-indicator.subtitle { background: linear-gradient(135deg, #2ecc71, #27ae60); }

    /* Progress indicators melhorados */
    .progress-card {
        background: var(--background-color, #f8f9fa);
        padding: 1rem;
        border-radius: 8px;
        border-left: 3px solid #007bff;
        margin: 0.5rem 0;
        transition: all 0.3s ease;
    }

    .progress-card:hover {
        border-left-width: 5px;
        transform: translateX(2px);
    }

    [data-theme="dark"] .progress-card {
        background: #2b2b2b;
        border-left: 3px solid #90caf9;
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
        position: relative;
        overflow: hidden;
    }

    .stButton > button::before {
        content: '';
        position: absolute;
        top: 0;
        left: -100%;
        width: 100%;
        height: 100%;
        background: linear-gradient(90deg, transparent, rgba(255,255,255,0.2), transparent);
        transition: left 0.5s;
    }

    .stButton > button:hover::before {
        left: 100%;
    }

    .stButton > button:hover {
        background: linear-gradient(145deg, #0056b3 0%, #004085 100%);
        transform: translateY(-1px);
        box-shadow: 0 4px 8px rgba(0,123,255,0.4);
    }

    /* Status indicators */
    .status-success { color: #28a745; font-weight: bold; }
    .status-warning { color: #ffc107; font-weight: bold; }
    .status-error { color: #dc3545; font-weight: bold; }
    .status-info { color: #17a2b8; font-weight: bold; }

    /* Expander styling melhorado */
    .streamlit-expanderHeader {
        font-size: 1.1rem !important;
        font-weight: 600 !important;
        color: #007bff !important;
        background-color: transparent !important;
        transition: all 0.3s ease !important;
    }

    .streamlit-expanderHeader:hover {
        color: #0056b3 !important;
        text-shadow: 0 0 5px rgba(0, 123, 255, 0.3) !important;
    }

    [data-theme="dark"] .streamlit-expanderHeader {
        color: #90caf9 !important;
    }

    [data-theme="dark"] .streamlit-expanderHeader:hover {
        color: #64b5f6 !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- Funções Auxiliares Avançadas ---


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
def cached_mapear_modulos(caminho: str, use_multiformat: bool = True):
    """Cache do mapeamento de módulos com suporte multi-formato."""
    if use_multiformat:
        # AQUI É ONDE VAI A CHAMA PARA O NOVO mapear_modulos_multiformat do file_processor.py
        # E ele precisa do MultiFormatProcessor para funcionar.
        # Ele detecta os arquivos e passa para a lógica principal.

        # Inicia o MultiFormatProcessor para escanear
        processor = MultiFormatProcessor(Path(caminho))
        detected_files = processor.scan_directory(Path(caminho))
        # Armazena para render_detected_files_summary
        st.session_state.detected_files = detected_files

        # Passa detected_files
        return mapear_modulos_multiformat(caminho, detected_files)
    else:
        # Mantém a lógica original de mapeamento (apenas vídeos)
        return mapear_modulos(caminho)


def estimate_course_config(modulos_mapeados: dict) -> dict:
    """Analisa o curso e sugere configurações otimizadas."""
    total_aulas = sum(len(aulas_list)
                      for aulas_list in modulos_mapeados.values())

    # Contar tipos de conteúdo
    content_types = {'video': 0, 'audio': 0, 'document': 0}
    for aulas_list in modulos_mapeados.values():
        for aula in aulas_list:
            aula_type = aula.get('type', 'video')
            content_types[aula_type] = content_types.get(aula_type, 0) + 1

    # Análise básica do conteúdo
    sample_texts = []
    for aulas_list in modulos_mapeados.values():
        for aula in aulas_list[:2]:  # Amostra das primeiras aulas
            if aula.get('txt_path'):
                txt_path = Path(aula['txt_path'])
                if txt_path.exists():
                    content = _load_content_from_file(txt_path)
                    if content:
                        sample_texts.append(content[:1000])

    combined_sample = " ".join(sample_texts).lower()

    # Detectar complexidade
    complexity_indicators = [
        'algoritmo', 'implementação', 'avançado', 'complexo', 'profundo',
        'advanced', 'complex', 'deep', 'technical', 'expert'
    ]

    complexity_score = sum(
        1 for indicator in complexity_indicators if indicator in combined_sample)

    # Detectar área técnica
    is_technical = any(word in combined_sample for word in [
        'código', 'programming', 'development', 'software', 'api', 'framework'
    ])

    # Detectar se tem documentos
    has_documents = content_types['document'] > 0

    # Sugestões baseadas na análise
    if complexity_score > 3 or total_aulas > 15:
        config = {
            'resumo_tokens': 550,
            'insights_tokens': 750,
            'quiz_tokens': 850,
            'temperature': 0.2,
            'reasoning': f'Curso complexo detectado ({total_aulas} aulas) - tokens aumentados para análises detalhadas'
        }
    elif is_technical:
        config = {
            'resumo_tokens': 500,
            'insights_tokens': 700,
            'quiz_tokens': 800,
            'temperature': 0.3,
            'reasoning': 'Conteúdo técnico detectado - configuração balanceada para precisão'
        }
    elif has_documents:
        config = {
            'resumo_tokens': 480,
            'insights_tokens': 680,
            'quiz_tokens': 750,
            'temperature': 0.3,
            'reasoning': 'Curso com documentos detectado - otimizado para análise textual'
        }
    else:
        config = {
            'resumo_tokens': 400,
            'insights_tokens': 600,
            'quiz_tokens': 700,
            'temperature': 0.4,
            'reasoning': 'Curso padrão - configuração otimizada para didática'
        }

    # Adicionar informações sobre tipos de conteúdo
    config['content_analysis'] = {
        'total_aulas': total_aulas,
        'videos': content_types['video'],
        'audios': content_types['audio'],
        'documentos': content_types['document'],
        'is_multiformat': sum(content_types.values()) > content_types['video']
    }

    return config


def render_status_icons(aula_info: dict, base_path: Path, modulo: str) -> str:
    """Renderiza ícones de status interativos avançados para cada aula."""
    aula_stem = aula_info['stem']

    # Verificar quais arquivos existem
    summary_path = base_path / "analises_ia" / modulo / aula_stem / "RESUMO.md"
    insights_path = base_path / "analises_ia" / modulo / aula_stem / "INSIGHTS.md"
    quiz_path = base_path / "analises_ia" / modulo / aula_stem / "QUESTIONARIO.md"

    # Status de cada tipo
    resumo_status = "completed" if summary_path.exists() else "pending"
    insights_status = "completed" if insights_path.exists() else "pending"
    quiz_status = "completed" if quiz_path.exists() else "pending"

    # Adicionar informação sobre tipo de arquivo
    file_type = aula_info.get('type', 'video')
    type_icon = {
        'video': '🎥',
        'audio': '🎵',
        'document': '📄'
    }.get(file_type, '🎥')

    icons_html = f"""
    <div style="display: flex; align-items: center; gap: 0.3rem;">
        <span class="format-indicator {file_type}" title="Tipo: {file_type.title()}">{type_icon}</span>
        <span class="status-icon resumo {resumo_status}"
              title="📝 Análise de Resumo {'✅ Criado' if resumo_status == 'completed' else '⏳ Pendente'}"
              onclick="window.open('{summary_path}', '_blank')">📝</span>
        <span class="status-icon insights {insights_status}"
              title="💡 Insights Valiosos {'✅ Criado' if insights_status == 'completed' else '⏳ Pendente'}"
              onclick="window.open('{insights_path}', '_blank')">💡</span>
        <span class="status-icon questionario {quiz_status}"
              title="❓ Teste seu Conhecimento {'✅ Criado' if quiz_status == 'completed' else '⏳ Pendente'}"
              onclick="window.open('{quiz_path}', '_blank')">❓</span>
    </div>
    """

    return icons_html

# --- Gerador de Relatório Completo EXTRAORDINÁRIO v2.0 ---


def generate_complete_course_report(modulos_mapeados: dict, base_path: Path, course_name: str, gpt_model: str) -> str:
    """Gera relatório completo e extraordinário do curso - versão multi-formato."""

    # Coletar todas as transcrições e análise de conteúdo
    all_content = []
    course_metadata = {
        'total_modules': len(modulos_mapeados),
        'total_lessons': 0,
        'total_duration': 0,
        'content_types': {'video': 0, 'audio': 0, 'document': 0},
        'formats_detected': set(),
        'lesson_lengths': [],
        'document_pages': 0,
        'slides_count': 0
    }

    for module_name, aulas_list in modulos_mapeados.items():
        course_metadata['total_lessons'] += len(aulas_list)

        for aula_info in aulas_list:
            # Coletar conteúdo
            if aula_info.get('txt_path'):
                txt_path = Path(aula_info['txt_path'])
                if txt_path.exists():
                    content = _load_content_from_file(txt_path)
                    if content:
                        all_content.append({
                            'module': module_name,
                            'lesson': aula_info['stem'],
                            'content': content,
                            'type': aula_info.get('type', 'video'),
                            'metadata': aula_info.get('metadata', {})
                        })

            # Coletar metadados
            content_type = aula_info.get('type', 'video')
            course_metadata['content_types'][content_type] = course_metadata['content_types'].get(
                content_type, 0) + 1  # Correção: Use .get para evitar KeyError

            if aula_info.get('video_path'):
                try:
                    duration = extrair_duracao(aula_info['video_path'])
                    if duration:
                        course_metadata['total_duration'] += duration
                        course_metadata['lesson_lengths'].append(duration)

                    video_ext = Path(aula_info['video_path']).suffix
                    course_metadata['formats_detected'].add(
                        f"Vídeo {video_ext}")
                except:
                    pass

            if aula_info.get('doc_path'):
                doc_ext = Path(aula_info['doc_path']).suffix
                course_metadata['formats_detected'].add(f"Documento {doc_ext}")

                # Contar páginas/slides
                metadata = aula_info.get('metadata', {})
                if 'pages' in metadata:
                    course_metadata['document_pages'] += metadata['pages']
                if 'slides' in metadata:
                    course_metadata['slides_count'] += metadata['slides']

    if not all_content:
        return "❌ Erro: Nenhuma transcrição encontrada para análise."

    # Preparar texto consolidado para análise
    consolidated_text = "\n\n".join([
        f"MÓDULO: {item['module']} | AULA: {item['lesson']} | TIPO: {item['type']}\n{item['content'][:2000]}"
        for item in all_content
    ])

    # Calcular estatísticas avançadas
    avg_lesson_duration = (
        sum(course_metadata['lesson_lengths']) /
        len(course_metadata['lesson_lengths'])
        if course_metadata['lesson_lengths'] else 0
    )

    content_variety_score = len(
        [v for v in course_metadata['content_types'].values() if v > 0])

    # PROMPT EXTRAORDINÁRIO v2.0 para análise completa
    prompt_completo = f"""# 🎯 ANÁLISE COMPLETA ESTRATÉGICA v2.0: {course_name}

Você é um **CONSULTOR EDUCACIONAL PREMIUM** especializado em cursos multimodais (vídeo + áudio + documentos). Sua missão é criar uma análise EXTRAORDINÁRIA que serve como documento definitivo de referência.

## 📊 METADADOS AVANÇADOS DO CURSO:
- **Módulos:** {course_metadata['total_modules']}
- **Aulas Totais:** {course_metadata['total_lessons']}
- **Duração dos Vídeos:** {segundos_para_hms(course_metadata['total_duration'])}
- **Duração Média/Aula:** {segundos_para_hms(int(avg_lesson_duration))}
- **Formatos Detectados:** {', '.join(course_metadata['formats_detected'])}
- **Variedade de Conteúdo:** {content_variety_score}/3 (Vídeo/Áudio/Documento)

### 📈 DISTRIBUIÇÃO DE CONTEÚDO:
- **Vídeos:** {course_metadata['content_types']['video']} aulas
- **Áudios:** {course_metadata['content_types']['audio']} aulas
- **Documentos:** {course_metadata['content_types']['document']} arquivos
- **Páginas de Documentos:** {course_metadata['document_pages']}
- **Slides Detectados:** {course_metadata['slides_count']}

## 🎯 ESTRUTURA OBRIGATÓRIA DO RELATÓRIO v2.0:

### 1. 🌟 VISÃO EXECUTIVA (2-3 parágrafos)
[Análise de alto nível: O que é este curso? Qual é a proposta de valor única? Por que alguém deveria estudar isso?]

### 2. 🎓 PERFIL ESTRATÉGICO DO CURSO
**🎯 Público-Alvo Ideal:** [Nível de experiência + características específicas + pré-requisitos]
**🏷️ Categoria Principal:** [Área principal com subcategorias]
**⏱️ Investimento de Tempo Realista:**
- Conclusão básica: [X semanas com Y horas/semana]
- Domínio completo: [X meses incluindo prática]
- Revisão periódica: [X horas/mês para manter conhecimento]

**🌍 Abordagem Pedagógica Detectada:** [Analisar se é mais teórico, prático, misto, baseado em casos, etc.]
**📱 Modalidade:** [100% vídeo, multimodal, documento-intensivo, etc.]

### 3. 📚 ARQUITETURA CURRICULAR AVANÇADA
**🏗️ Estrutura Pedagógica:**
[Para cada módulo principal, analise:]
- Objetivo específico
- Nivel de dificuldade (1-10)
- Dependências com outros módulos
- Tipo de conteúdo predominante

**📈 Curva de Aprendizado Detalhada:**
- **Onboarding (0-20%):** [Como inicia, primeiras impressões]
- **Construção de Base (20-50%):** [Fundamentos, conceitos core]
- **Desenvolvimento Prático (50-80%):** [Aplicações, exercícios, projetos]
- **Especialização (80-100%):** [Tópicos avançados, edge cases]

### 4. 💎 ANÁLISE COMPETITIVA E DIFERENCIAIS
**🔥 Pontos Fortes Únicos:**
- [3-5 elementos que tornam este curso superior aos concorrentes]

**⚠️ Gaps Identificados:**
- [2-3 áreas onde o curso poderia ser melhorado ou complementado]

**🎯 Conceitos-Chave Dominados:**
- [Lista hierárquica dos 8-15 conceitos mais importantes, organizados por complexidade]

**🏆 Nivel de Completude:** [Análise se é um curso completo ou introdutório]

### 5. 🛤️ ROADMAP DE APRENDIZADO ESTRATÉGICO

**📋 PRÉ-REQUISITOS ESTRATIFICADOS:**
- **Críticos:** [Sem isso, não consegue acompanhar]
- **Importantes:** [Facilita muito o aprendizado]
- **Úteis:** [Contexto adicional]
- **Ferramentas:** [Software, hardware, contas necessárias]

**🎯 METODOLOGIA DE ESTUDO OTIMIZADA:**
- **Fase 1 - Imersão:** [Primeiros módulos, tempo sugerido, foco]
- **Fase 2 - Aplicação:** [Meio do curso, projetos práticos]
- **Fase 3 - Consolidação:** [Últimos módulos, integração de conhecimento]
- **Fase 4 - Extensão:** [Próximos passos, aprofundamento]

**⏰ CRONOGRAMAS FLEXÍVEIS:**
- **Intensivo (40h/semana):** [X semanas - para quem pode se dedicar full-time]
- **Acelerado (15h/semana):** [X semanas - profissionais dedicados]
- **Equilibrado (8h/semana):** [X semanas - a maioria das pessoas]
- **Tranquilo (4h/semana):** [X semanas - quem tem pouco tempo]

### 6. 🚀 ROADMAP DE EVOLUÇÃO PROFISSIONAL

**📈 TRANSFORMAÇÃO ESPERADA:**
- **Estado inicial:** [Que tipo de profissional/pessoa entra]
- **Estado final:** [Que competências concretas terá ao sair]
- **Principais mudanças:** [Como pensará diferente sobre a área]

**🎯 PROJETOS HABILITADOS:**
1. **[Projeto Iniciante]** - [Descrição + tempo estimado + complexidade]
2. **[Projeto Intermediário]** - [Descrição + tempo estimado + complexidade]
3. **[Projeto Avançado]** - [Descrição + tempo estimado + complexidade]

**💼 IMPACTO PROFISSIONAL ESPERADO:**
- **Trabalho atual:** [Como aplicar no trabalho atual, melhorias esperadas]
- **Novas oportunidades:** [Tipos de vagas que ficam acessíveis]
- **Freelancing:** [Tipos de projetos que pode aceitar]
- **Empreendedorismo:** [Ideias de negócio que ficam viáveis]

### 7. 🎯 CONTINUIDADE E ESPECIALIZAÇÃO

**📚 CURSOS DE SEQUÊNCIA (em ordem de prioridade):**
1. **[Nome do Curso Avançado]** - [Por que é a evolução natural + instituição/plataforma]
2. **[Nome do Curso Complementar]** - [Que gap complementa + justificativa]
3. **[Nome da Especialização]** - [Para se tornar expert + requisitos]

**🏆 CERTIFICAÇÕES RELEVANTES:**
- [Certificações da área que fazem sentido após este curso]
- [Ordem recomendada + dificuldade + valor de mercado]

**👥 COMUNIDADES E NETWORKING:**
- [Onde encontrar outros profissionais da área]
- [Eventos, conferências, grupos relevantes]
- [Como se manter atualizado na área]

### 8. 🎯 ESTRATÉGIAS AVANÇADAS DE SUCESSO

**📝 METODOLOGIA DE ESTUDO ESPECÍFICA:**
- [3-4 técnicas específicas baseadas no tipo de conteúdo detectado]
- [Como otimizar a retenção para este curso específico]
- [Frequência ideal de revisão]

**🛠️ STACK TECNOLÓGICO RECOMENDADO:**
- [Ferramentas principais + alternativas]
- [Recursos complementares (plugins, extensions, etc.)]
- [Documentações oficiais essenciais]
- [Blogs/sites para acompanhar]
- [Canais YouTube complementares]
- [Livros físicos recomendados]
- [Podcasts da área]

### 9. 📊 AVALIAÇÃO TÉCNICA DETALHADA

**⭐ SCORING DETALHADO:**
- **Didática e Clareza:** [X/10] - [Justificativa específica]
- **Completude do Conteúdo:** [X/10] - [O que cobre bem/mal]
- **Aplicabilidade Prática:** [X/10] - [Quão utilizável é o conhecimento]
- **Atualidade Tecnológica:** [X/10] - [Quão atual está o conteúdo]
- **Progressão de Dificuldade:** [X/10] - [Se a curva de aprendizado é bem estruturada]
- **Valor vs Tempo Investido:** [X/10] - [ROI educacional]

**🎯 SCORE GERAL:** [Média ponderada]/10

**🏅 CLASSIFICAÇÃO:** [Excelente/Muito Bom/Bom/Regular] baseado no score

### 10. 🎪 RECOMENDAÇÃO FINAL ESTRATÉGICA

**✅ RECOMENDO ESTE CURSO PARA:**
- [Perfis específicos que mais se beneficiariam]
- [Situações onde este curso é a melhor opção]
- [Momentos de carreira ideais para fazê-lo]

**❌ NÃO RECOMENDO PARA:**
- [Perfis que não se beneficiariam]
- [Quando há opções melhores]

**🎯 CONCLUSÃO EXECUTIVA:**
[Parágrafo final definitivo sobre o valor do curso e posicionamento no mercado educacional]

---

## 🎯 DIRETRIZES CRÍTICAS v2.0:
- **Tom:** Consultivo senior, inspirador mas realista, foco em valor acionável
- **Qualidade:** Nivel consultoria estratégica ($1000/hora)
- **Foco:** Insights únicos que só um especialista conseguiria dar
- **Formato:** Markdown perfeito para Notion, com emojis estratégicos
- **Profundidade:** Análise que ninguém mais consegue fazer
- **Tamanho:** 2500-3000 palavras (relatório completo)

## 📖 CONTEÚDO PARA ANÁLISE:
{consolidated_text[:20000]}

---

**MISSÃO CRÍTICA:** Este relatório será usado por pessoas para decidir se vale a pena investir tempo/dinheiro neste curso. Precisa ser tão bom que vire referência na decisão e no planejamento de estudos!"""

    try:
        # Chamar GPT para gerar o relatório
        import openai

        response = openai.chat.completions.create(
            model=gpt_model,
            messages=[
                {
                    "role": "system",
                    "content": "Você é um consultor educacional premium e analista estratégico sênior, especializado em análise profunda de cursos multimodais. Sua expertise é transformar dados educacionais em insights estratégicos acionáveis que orientam decisões de investimento em educação."
                },
                {
                    "role": "user",
                    "content": prompt_completo
                }
            ],
            max_tokens=4000,
            temperature=0.3
        )

        relatorio = response.choices[0].message.content.strip()

        # Adicionar metadados avançados do relatório
        timestamp = datetime.now().strftime("%d/%m/%Y às %H:%M:%S")
        header = f"""# 📊 ANÁLISE ESTRATÉGICA COMPLETA - {course_name}

**📅 Gerado em:** {timestamp}
**🤖 Modelo IA:** {gpt_model}
**🛠️ Ferramenta:** Analisador de Cursos v4.0 ULTIMATE
**📊 Base de Análise:** {len(all_content)} aulas processadas
**🎯 Formatos:** {len(course_metadata['formats_detected'])} tipos diferentes
**⏱️ Duração Total:** {segundos_para_hms(course_metadata['total_duration'])}

---

"""

        relatorio_final = header + relatorio

        # Salvar o relatório
        reports_dir = base_path / "analises_ia" / "consolidados"
        reports_dir.mkdir(parents=True, exist_ok=True)

        report_path = reports_dir / \
            f"ANALISE_ESTRATEGICA_COMPLETA_{course_name}.md"

        with open(report_path, "w", encoding="utf-8") as f:
            f.write(relatorio_final)

        # Contar tokens (estimativa melhorada)
        estimated_tokens = len(relatorio_final.split()) * \
            1.4  # Estimativa mais precisa
        token_counter.add_tokens('relatorio_completo',
                                 int(estimated_tokens), gpt_model)

        return relatorio_final

    except Exception as e:
        return f"❌ Erro ao gerar relatório completo: {str(e)}"

# --- Funções de Migração (mantidas) ---


def detect_structure_issues(base_path: Path) -> dict:
    """Detecta problemas na estrutura de pastas de AI."""
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

# --- Sidebar VERSÃO 4.0 ULTIMATE ---


def render_sidebar():
    """Sidebar versão 4.0 ULTIMATE com multi-formato e IA avançada."""
    st.sidebar.markdown("## ⚙️ Configurações v4.0 ULTIMATE")

    # SELEÇÃO DE PASTA COM MULTI-FORMATO
    if 'caminho_input_value' not in st.session_state:
        st.session_state.caminho_input_value = ""

    if 'use_multiformat' not in st.session_state:
        st.session_state.use_multiformat = True

    st.sidebar.markdown("### 📁 Seleção de Conteúdo")

    # Toggle multi-formato
    st.session_state.use_multiformat = st.sidebar.checkbox(
        "🎯 Modo Multi-Formato",
        value=st.session_state.use_multiformat,
        help="Ativa suporte a vídeos, áudios, PDFs, Word, PowerPoint e legendas"
    )

    caminho_text_input = st.sidebar.text_input(
        "📂 Caminho da pasta:",
        value=st.session_state.caminho_input_value,
        placeholder="/caminho/para/seus/cursos",
        help="Cole aqui o caminho completo da pasta contendo os materiais do curso"
    )

    # Seletor de pastas melhorado
    if st.sidebar.button("📂 Abrir Seletor de Pastas"):
        with st.sidebar:
            with st.spinner("Abrindo seletor de pastas..."):
                try:
                    selected_path = ""

                    if sys.platform == 'darwin':  # macOS
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
                            command, shell=True, capture_output=True, text=True, timeout=30)

                        if result.returncode == 0:
                            selected_path = result.stdout.strip()

                    elif sys.platform.startswith('win'):  # Windows
                        try:
                            import tkinter as tk
                            from tkinter import filedialog

                            root = tk.Tk()
                            root.withdraw()
                            root.attributes('-topmost', True)

                            selected_path = filedialog.askdirectory(
                                title="Selecione a pasta do curso")
                            root.destroy()

                        except ImportError:
                            st.sidebar.error("❌ tkinter não disponível")

                    if selected_path and selected_path.strip():
                        st.session_state.caminho_input_value = selected_path.strip()
                        st.sidebar.success("✅ Pasta selecionada!")
                        st.rerun()
                    else:
                        st.sidebar.info("ℹ️ Nenhuma pasta selecionada")

                except Exception as e:
                    st.sidebar.error(f"❌ Erro: {e}")

    # Atualizar state
    if caminho_text_input != st.session_state.caminho_input_value:
        st.session_state.caminho_input_value = caminho_text_input

    # Validação avançada
    current_path_value = st.session_state.caminho_input_value
    if current_path_value:
        path_obj = Path(current_path_value)
        if path_obj.exists():
            # Mostrar preview do que foi detectado
            if st.session_state.use_multiformat:
                try:
                    processor = MultiFormatProcessor(path_obj)
                    preview_files = {}
                    # Preview dos primeiros 10
                    for file_path in list(path_obj.rglob('*'))[:10]:
                        if file_path.is_file():
                            file_type = processor.detect_file_type(file_path)
                            if file_type != FileType.UNKNOWN:
                                if file_type not in preview_files:
                                    preview_files[file_type] = []
                                preview_files[file_type].append(file_path.name)

                    if preview_files:
                        st.sidebar.success("✅ Pasta válida - Preview:")
                        for file_type, files in preview_files.items():
                            icon = {'video': '🎥', 'audio': '🎵', 'document': '📄', 'subtitle': '📝'}.get(
                                file_type.value, '📁')
                            st.sidebar.caption(
                                f"{icon} {len(files)} {file_type.value}(s)")
                    else:
                        st.sidebar.warning(
                            "⚠️ Nenhum arquivo suportado encontrado")
                except:
                    st.sidebar.success("✅ Caminho válido")
            else:
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

    # Processamento com loading avançado
    if load_button and current_path_value:
        if Path(current_path_value).exists():
            progress_container = st.sidebar.empty()

            with progress_container:
                with st.spinner("🔍 Analisando conteúdo..."):
                    try:
                        cached_mapear_modulos.clear()
                        st.session_state.curso_path = current_path_value
                        st.session_state.multiformat_enabled = st.session_state.use_multiformat

                        with st.spinner("📊 Processando estrutura..."):
                            # Correção: mapear_modulos_multiformat deve ser chamada sem 'current_path_value' na definição,
                            # mas o MultiFormatProcessor e o scan_directory já lidam com isso.
                            # cached_mapear_modulos já chama o processor e mapear_modulos_multiformat internamente.
                            # O erro anterior era no mapear_modulos_multiformat, não aqui.
                            test_mapping = cached_mapear_modulos(  # Esta chamada já faz o trabalho
                                current_path_value,  # Primeiro argumento
                                st.session_state.use_multiformat  # Segundo argumento
                            )

                        format_type = "multi-formato" if st.session_state.use_multiformat else "vídeo tradicional"
                        st.sidebar.success(
                            f"✅ Curso carregado ({format_type})!")
                        st.rerun()

                    except Exception as e:
                        st.sidebar.error(f"❌ Erro ao carregar: {str(e)}")

        else:
            st.sidebar.error("❌ Caminho inválido!")

    st.sidebar.markdown("---")

    # Seção de manutenção
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

    # Configurações de A.I. AVANÇADAS (MOVIDO PARA CIMA)
    st.sidebar.markdown("## 🧠 Configurações de A.I.")

    gpt_model = st.sidebar.selectbox(
        "Modelo GPT:",
        ["gpt-3.5-turbo", "gpt-4", "gpt-4o"],
        index=0,
        help="💡 GPT-3.5: Rápido e econômico\n🚀 GPT-4: Melhor qualidade\n⚡ GPT-4o: Mais rápido que GPT-4"
    )

    # Configurações avançadas INTELIGENTES v2.0
    with st.sidebar.expander("⚙️ Configurações Avançadas"):

        # Sugestões inteligentes baseadas no curso carregado
        if 'curso_path' in st.session_state:
            try:
                modulos_mapeados = cached_mapear_modulos(
                    st.session_state.curso_path,
                    st.session_state.get('multiformat_enabled', True)
                )
                suggestions = estimate_course_config(modulos_mapeados)

                st.markdown("**🎯 Análise do Curso:**")
                st.info(suggestions['reasoning'])

                # Mostrar análise de conteúdo
                content_analysis = suggestions.get('content_analysis', {})
                if content_analysis.get('is_multiformat'):
                    st.markdown("**📊 Distribuição:**")
                    st.caption(f"📹 {content_analysis['videos']} vídeos")
                    st.caption(f"🎵 {content_analysis['audios']} áudios")
                    st.caption(
                        f"📄 {content_analysis['documentos']} documentos")

                if st.button("🎯 Aplicar Sugestões Inteligentes", key="apply_suggestions"):
                    st.session_state.max_tokens_summary = suggestions['resumo_tokens']
                    st.session_state.max_tokens_quiz = suggestions['quiz_tokens']
                    st.session_state.max_tokens_insights = suggestions['insights_tokens']
                    st.session_state.temperature = suggestions['temperature']
                    st.success("✅ Configurações otimizadas aplicadas!")
                    st.rerun()
            except Exception as e:  # Adicionado tratamento de exceção para estimate_course_config
                st.warning(
                    f"Não foi possível gerar sugestões inteligentes: {e}")
                suggestions = None
        else:
            suggestions = None

        # Sliders com explicações detalhadas
        st.session_state.max_tokens_summary = st.slider(
            "Max Tokens Resumo", 100, 1000,
            st.session_state.get('max_tokens_summary', 400),
            key="max_tokens_summary_slider",
            help="""📖 Controla o tamanho e detalhamento do resumo:
• 200-300: Resumo conciso e direto
• 400-500: Resumo detalhado (recomendado)
• 600-800: Análise profunda e abrangente
• 800+: Resumo muito detalhado (para conteúdo complexo)"""
        )

        st.session_state.max_tokens_quiz = st.slider(
            "Max Tokens Questionário", 300, 1500,
            st.session_state.get('max_tokens_quiz', 700),
            key="max_tokens_quiz_slider",
            help="""❓ Controla a complexidade e quantidade dos questionários:
• 500-600: 3-4 questões essenciais
• 700-900: 5-6 questões detalhadas (recomendado)
• 1000-1200: 7-8 questões elaboradas
• 1300+: Questionário muito completo (para conteúdo extenso)"""
        )

        st.session_state.max_tokens_insights = st.slider(
            "Max Tokens Insights", 200, 1200,
            st.session_state.get('max_tokens_insights', 600),
            key="max_tokens_insights_slider",
            help="""💡 Controla a profundidade e quantidade dos insights:
• 400-500: Insights práticos básicos
• 600-800: Análise estratégica (recomendado)
• 900-1000: Insights muito detalhados
• 1100+: Análise completa com aplicações avançadas"""
        )

        st.session_state.temperature = st.slider(
            "Criatividade (Temperature)", 0.0, 1.0,
            st.session_state.get('temperature', 0.3), 0.1,
            key="temperature_slider",
            help="""🎨 Controla o estilo e criatividade da IA:
• 0.1-0.2: Respostas muito precisas e técnicas
• 0.3-0.4: Equilíbrio ideal (recomendado)
• 0.5-0.7: Mais criativo e didático
• 0.8+: Muito criativo (pode ser inconsistente)"""
        )

    st.sidebar.markdown("---")

    # STATUS MULTI-FORMATO (MOVIDO PARA O FINAL)
    st.sidebar.markdown("### 📦 Status Multi-Formato")
    deps = check_dependencies()
    for dep_name, available in deps.items():
        status_class = "dependency-status" if available else "dependency-status missing"
        icon = "✅" if available else "❌"
        st.sidebar.markdown(
            f'<div class="{status_class}">{icon} {dep_name}</div>', unsafe_allow_html=True)

    if not all(deps.values()):
        st.sidebar.warning("⚠️ Instale dependências para suporte completo")
        if st.sidebar.button("📋 Ver Comandos de Instalação"):
            st.sidebar.code("""
pip install PyMuPDF python-docx python-pptx
            """)

    return current_path_value, gpt_model

# --- Renderização de Métricas ULTIMATE ---


def render_course_metrics(modulos_mapeados, dur_total_segundos):
    """Renderiza cards de métricas ultimate com suporte multi-formato."""

    # Calcular estatísticas avançadas
    total_aulas = sum(len(aulas_list)
                      for aulas_list in modulos_mapeados.values())
    total_transcricoes = sum(1 for aulas_list in modulos_mapeados.values()
                             for aula in aulas_list if aula.get('txt_path') and Path(aula.get('txt_path', '')).exists())

    # Contar por tipo de conteúdo
    content_stats = {'video': 0, 'audio': 0, 'document': 0, 'unknown': 0}
    for aulas_list in modulos_mapeados.values():
        for aula in aulas_list:
            content_type = aula.get('type', 'unknown')
            content_stats[content_type] = content_stats.get(
                content_type, 0) + 1

    # Calcular páginas de documentos
    total_pages = 0
    for aulas_list in modulos_mapeados.values():
        for aula in aulas_list:
            if aula.get('metadata') and 'pages' in aula['metadata']:
                total_pages += aula['metadata']['pages']

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{len(modulos_mapeados)}</h3>
            <p>📁 Módulos</p>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        multiformat_indicator = "🎯" if st.session_state.get(
            'multiformat_enabled') else "🎥"
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_aulas}</h3>
            <p>{multiformat_indicator} Itens Totais</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        # Melhor formatação para Multi-Formato
        videos = content_stats['video']
        audios = content_stats['audio']
        docs = content_stats['document']

        st.markdown(f"""
        <div class="metric-card">
            <h3 style="font-size: 1.4rem; line-height: 1.2;">
                <span style="color: #e74c3c;">{videos}</span>📹 
                <span style="color: #f39c12;">{audios}</span>🎵 
                <span style="color: #3498db;">{docs}</span>📄
            </h3>
            <p>🎯 Multi-Formato</p>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card">
            <h3>{total_transcricoes}/{total_aulas}</h3>
            <p>📝 Transcrições</p>
        </div>
        """, unsafe_allow_html=True)

    with col5:
        duration_text = segundos_para_hms(dur_total_segundos)
        pages_text = f"+ {total_pages}pgs" if total_pages > 0 else ""

        st.markdown(f"""
        <div class="metric-card">
            <h3 style="font-size: 1.3rem; line-height: 1.2;">
                {duration_text}<br>
                <small style="font-size: 0.8rem; opacity: 0.8;">{pages_text}</small>
            </h3>
            <p>⏱️ Duração Total</p>
        </div>
        """, unsafe_allow_html=True)

# --- Função de Processamento Completo ULTIMATE ---


def processar_curso_completo(modulos_mapeados, base_path, curso_nome, gpt_model):
    """Processa curso completo: transcrição + IA + relatórios - TUDO de uma vez!"""

    # Container principal para o processamento
    main_container = st.container()

    with main_container:
        st.markdown("## 🚀 PROCESSAMENTO COMPLETO INICIADO")
        st.info("🎯 Este processo fará TUDO: transcrição, análises de IA e relatórios!")

        # Barra de progresso geral
        overall_progress = st.progress(0)
        status_container = st.empty()

        try:
            # ETAPA 1: TRANSCRIÇÃO (25%)
            status_container.info(
                "🎙️ **ETAPA 1/4:** Transcrevendo conteúdo...")
            overall_progress.progress(0.1)

            # Preparar itens para transcrição
            items_to_transcribe = {}
            doc_items = []

            for modulo, aulas_list in modulos_mapeados.items():
                # Vídeos e áudios para transcrição
                media_items = [aula for aula in aulas_list
                               if (aula.get("video_path") or aula.get("audio_path"))
                               and not (aula.get('txt_path') and Path(aula['txt_path']).exists())]
                if media_items:
                    items_to_transcribe[modulo] = media_items

                # Documentos para processamento
                doc_items.extend([aula for aula in aulas_list
                                  if aula.get('type') == 'document' and aula.get('doc_path')])

            # Transcrever mídia
            if items_to_transcribe:
                whisper_model = st.session_state.get('whisper_model', 'small')
                with st.spinner(f"Transcrevendo {sum(len(items) for items in items_to_transcribe.values())} arquivos de mídia..."):
                    transcrever_videos(items_to_transcribe, modelo=whisper_model,
                                       tipo_audio="wav", deletar_audio=True)
                st.success(
                    f"✅ {sum(len(items) for items in items_to_transcribe.values())} mídias transcritas!")

            # Processar documentos
            if doc_items:
                extractor = DocumentExtractor()
                with st.spinner(f"Processando {len(doc_items)} documentos..."):
                    for aula in doc_items:
                        try:
                            doc_text = extractor.extract_text(
                                Path(aula['doc_path']))
                            txt_path = Path(
                                aula['doc_path']).with_suffix('.txt')
                            txt_path.write_text(doc_text, encoding='utf-8')
                        except Exception as e:
                            st.warning(
                                f"Erro ao processar {aula['stem']}: {e}")
                st.success(f"✅ {len(doc_items)} documentos processados!")

            overall_progress.progress(0.25)

            # Recarregar módulos após transcrição
            cached_mapear_modulos.clear()
            modulos_mapeados = cached_mapear_modulos(
                st.session_state.curso_path,
                st.session_state.get('multiformat_enabled', True)
            )

            # ETAPA 2: RESUMOS (50%)
            status_container.info(
                "📝 **ETAPA 2/4:** Gerando todos os resumos...")
            overall_progress.progress(0.3)

            with st.spinner("Gerando resumos para todas as aulas..."):
                _process_all_ai_content_type(
                    modulos_mapeados, base_path, gpt_model, "resumo", generate_summary)

            overall_progress.progress(0.5)
            st.success("✅ Todos os resumos gerados!")

            # ETAPA 3: INSIGHTS E QUESTIONÁRIOS (75%)
            status_container.info(
                "💡 **ETAPA 3/4:** Gerando insights e questionários...")
            overall_progress.progress(0.55)

            with st.spinner("Gerando insights para todas as aulas..."):
                _process_all_ai_content_type(
                    modulos_mapeados, base_path, gpt_model, "insight", extract_keywords_and_insights)

            overall_progress.progress(0.65)

            with st.spinner("Gerando questionários para todas as aulas..."):
                _process_all_ai_content_type(
                    modulos_mapeados, base_path, gpt_model, "questionario", generate_quiz_questions)

            overall_progress.progress(0.75)
            st.success("✅ Insights e questionários gerados!")

            # ETAPA 4: RELATÓRIOS FINAIS (100%)
            status_container.info(
                "📊 **ETAPA 4/4:** Gerando relatórios estratégicos...")
            overall_progress.progress(0.8)

            # Análise estratégica completa
            with st.spinner("Gerando análise estratégica completa..."):
                relatorio_estrategico = generate_complete_course_report(
                    modulos_mapeados, base_path, curso_nome, gpt_model
                )
                # Armazenar no session_state para exibição persistente
                st.session_state['analise_estrategica_content'] = relatorio_estrategico

            overall_progress.progress(0.9)

            # Relatórios tradicionais
            with st.spinner("Gerando relatórios tradicionais..."):
                video_paths = {}
                for modulo, aulas_list in modulos_mapeados.items():
                    video_paths[modulo] = [aula['video_path']
                                           for aula in aulas_list if aula.get("video_path")]

                if any(video_paths.values()):
                    gerar_relatorios(video_paths, base_path, curso_nome)

            overall_progress.progress(1.0)

            # RESULTADO FINAL
            status_container.success(
                "🎉 **PROCESSAMENTO COMPLETO FINALIZADO!**")

            # Estatísticas finais
            ai_stats = calculate_ai_stats(modulos_mapeados, base_path)

            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric(
                    "📝 Resumos", f"{ai_stats['resumos_gerados']}/{ai_stats['total_aulas']}")
            with col2:
                st.metric(
                    "💡 Insights", f"{ai_stats['insights_gerados']}/{ai_stats['total_aulas']}")
            with col3:
                st.metric(
                    "❓ Questionários", f"{ai_stats['questionarios_gerados']}/{ai_stats['total_aulas']}")

            # Mostrar relatório estratégico
            if not relatorio_estrategico.startswith("❌"):
                with st.expander("📖 Visualizar Análise Estratégica Completa", expanded=True):
                    st.markdown(relatorio_estrategico)

            st.balloons()
            st.success(
                "🎯 **CURSO COMPLETAMENTE PROCESSADO!** Todos os arquivos foram gerados com sucesso!")

            # CORREÇÃO CRÍTICA: Forçar atualização do cache e recarregar interface
            st.info("🔄 Atualizando interface com novos arquivos...")
            cached_mapear_modulos.clear()
            _load_content_from_file.clear()  # Limpar cache de arquivos também

            # Forçar rerun para atualizar a interface
            # Pequena pausa para garantir que arquivos foram salvos
            time.sleep(1)
            st.rerun()

        except Exception as e:
            st.error(f"❌ Erro durante o processamento completo: {str(e)}")
            status_container.error("❌ Processamento interrompido por erro")

        finally:
            # Limpar progresso
            overall_progress.empty()


# --- Cards de Ação VERSÃO 4.0 ULTIMATE ---


def render_action_cards(modulos_mapeados, base_path, curso_nome, gpt_model):
    """Renderiza cards de ação versão 4.0 ULTIMATE - REORGANIZADO."""
    st.markdown("## 🛠️ Ações Disponíveis")

    # PRIMEIRA SEÇÃO: TRANSCRIÇÃO E PROCESSAMENTO (REORGANIZADO)
    with st.expander("🎙️ **1. Transcrição e Processamento** (PRIMEIRO PASSO)", expanded=True):

        # Mostrar tipos detectados
        content_types = {}
        for aulas_list in modulos_mapeados.values():
            for aula in aulas_list:
                content_type = aula.get('type', 'video')
                content_types[content_type] = content_types.get(
                    content_type, 0) + 1

        if content_types:
            st.info(f"📊 Conteúdo detectado: {content_types}")

        col1, col2 = st.columns(2)

        with col1:
            st.markdown("#### 🎥 Transcrição de Mídia")
            whisper_model = st.selectbox(
                "Modelo Whisper:", ["tiny", "base", "small", "medium", "large"], index=2)
            audio_format = st.radio("Formato de áudio:", ("mp3", "wav"))
            delete_audio = st.checkbox("🧹 Deletar áudios após transcrição")

            if st.button("🎙️ Transcrever Apenas Vídeos", use_container_width=True):
                items_to_transcribe = {}
                for modulo, aulas_list in modulos_mapeados.items():
                    items_to_transcribe[modulo] = [
                        aula for aula in aulas_list
                        if aula.get("video_path") or aula.get("audio_path")
                    ]

                if any(items_to_transcribe.values()):
                    with st.spinner("Transcrevendo mídia..."):
                        transcrever_videos(items_to_transcribe, modelo=whisper_model,
                                           tipo_audio=audio_format, deletar_audio=delete_audio)
                        st.success("✅ Transcrição de mídia concluída!")
                        cached_mapear_modulos.clear()
                        st.rerun()
                else:
                    st.warning("❌ Nenhuma mídia encontrada para transcrição")

        with col2:
            st.markdown("### 📊 Estatísticas do Curso")

            # Mostrar estatísticas úteis
            ai_stats = calculate_ai_stats(modulos_mapeados, base_path)

            st.info(
                f"📝 Resumos: {ai_stats['resumos_gerados']}/{ai_stats['total_aulas']}")
            st.info(
                f"💡 Insights: {ai_stats['insights_gerados']}/{ai_stats['total_aulas']}")
            st.info(
                f"❓ Questionários: {ai_stats['questionarios_gerados']}/{ai_stats['total_aulas']}")

            # Verificar se existe análise estratégica
            reports_dir = base_path / "analises_ia" / "consolidados"
            report_path = reports_dir / \
                f"ANALISE_ESTRATEGICA_COMPLETA_{curso_nome}.md"

            if report_path.exists():
                st.success("✅ Análise Estratégica disponível!")
            else:
                st.warning("⚠️ Análise Estratégica não gerada")

        # Botão de processamento completo
        st.markdown("---")
        if st.button("🚀 Processar Curso Completo (Transcrever + IA)", use_container_width=True, type="primary"):
            processar_curso_completo(
                modulos_mapeados, base_path, curso_nome, gpt_model)

    # SEGUNDA SEÇÃO: ANÁLISE DE IA (REORGANIZADA)
    with st.expander("🧠 **2. Análise de IA** (SEGUNDO PASSO)", expanded=True):

        if not OPENAI_API_KEY:
            st.error("⚠️ Chave de API da OpenAI não configurada no arquivo .env.")
            return

        # Analisar conteúdo disponível
        content_types = {}
        for file_type in ['video', 'audio', 'document']:
            count = sum(1 for aulas_list in modulos_mapeados.values()
                        for aula in aulas_list if aula.get('type') == file_type)
            content_types[file_type] = count

        if content_types['document'] > 0:
            st.info(
                f"🎯 Modo multi-formato: {content_types['video']} vídeos, {content_types['audio']} áudios, {content_types['document']} documentos")

        ai_stats = calculate_ai_stats(modulos_mapeados, base_path)
        render_ai_progress(ai_stats)

        # Checkbox para regeração
        col_regen, _ = st.columns([3, 1])
        with col_regen:
            st.session_state['force_regenerate_ia'] = st.checkbox(
                "🔄 Forçar regeração (ignorar arquivos existentes)?",
                value=st.session_state.get('force_regenerate_ia', False),
                help="Se marcado, irá regenerar os arquivos de IA, sobrescrevendo os existentes."
            )

        # Processamento individual
        st.markdown("#### 🔧 Processamento Individual")
        col_all_sum, col_all_ins, col_all_quiz = st.columns(3)

        with col_all_sum:
            if st.button("💡 Todos os Resumos", use_container_width=True):
                with st.spinner("Gerando resumos..."):
                    _process_all_ai_content_type(
                        modulos_mapeados, base_path, gpt_model, "resumo", generate_summary)
                st.rerun()

        with col_all_ins:
            if st.button("🔍 Todos os Insights", use_container_width=True):
                with st.spinner("Gerando insights..."):
                    _process_all_ai_content_type(
                        modulos_mapeados, base_path, gpt_model, "insight", extract_keywords_and_insights)
                st.rerun()

        with col_all_quiz:
            if st.button("❓ Todos os Questionários", use_container_width=True):
                with st.spinner("Gerando questionários..."):
                    _process_all_ai_content_type(
                        modulos_mapeados, base_path, gpt_model, "questionario", generate_quiz_questions)
                st.rerun()

        # PROCESSAMENTO ORQUESTRADO (NOVA FUNCIONALIDADE)
        st.markdown("---")
        st.markdown("#### 🚀 PROCESSAMENTO COMPLETO ORQUESTRADO")
        st.info("🎯 Use o botão **'Processar Curso Completo'** acima para executar todas as etapas automaticamente!")

    # TERCEIRA SEÇÃO: ANÁLISE E RELATÓRIOS (REORGANIZADA)
    with st.expander("📊 **3. Análise e Relatórios** (ETAPA FINAL)", expanded=False):

        # Verificar se existe análise estratégica salva
        reports_dir = base_path / "analises_ia" / "consolidados"
        report_path = reports_dir / \
            f"ANALISE_ESTRATEGICA_COMPLETA_{curso_nome}.md"

        # Exibir análise estratégica se existir
        if report_path.exists() or st.session_state.get('analise_estrategica_content'):
            st.success("✅ Análise estratégica gerada!")

            # Carregar conteúdo do arquivo ou session_state
            if st.session_state.get('analise_estrategica_content'):
                analise_content = st.session_state['analise_estrategica_content']
            else:
                analise_content = _load_content_from_file(report_path)

            with st.expander("📖 Visualizar Relatório Estratégico", expanded=True):
                st.markdown(analise_content)

        col1, col2, col3 = st.columns(3)

        with col1:
            if st.button("🎯 Análise Estratégica Completa", use_container_width=True,
                         help="Gera relatório executivo estratégico completo do curso"):
                with st.spinner("🔍 Executando análise estratégica completa..."):
                    relatorio = generate_complete_course_report(
                        modulos_mapeados, base_path, curso_nome, gpt_model
                    )
                    if relatorio.startswith("❌"):
                        st.error(relatorio)
                    else:
                        st.session_state['analise_estrategica_content'] = relatorio
                        st.success("✅ Análise estratégica gerada!")
                        st.rerun()

        with col2:
            if st.button("🔍 Escopo e Detalhes", use_container_width=True):
                st.session_state.show_detailed_summary = True

        with col3:
            if st.button("📋 Relatórios Tradicionais", use_container_width=True):
                with st.spinner("Gerando relatórios tradicionais..."):
                    video_paths = {}
                    for modulo, aulas_list in modulos_mapeados.items():
                        video_paths[modulo] = [aula['video_path']
                                               for aula in aulas_list if aula.get("video_path")]

                    if any(video_paths.values()):
                        gerar_relatorios(video_paths, base_path, curso_nome)
                        st.success("✅ Relatórios tradicionais gerados!")
                    else:
                        st.warning(
                            "❌ Nenhum vídeo encontrado para relatórios tradicionais")

    # Iterar sobre os módulos e aulas para exibir os resultados da IA de forma organizada
    st.markdown("---")
    st.markdown("## 📚 Módulos e Aulas Detalhes")
    for modulo, aulas_list in modulos_mapeados.items():
        st.markdown(f"### 📂 Módulo: {modulo}")
        for aula_info in aulas_list:
            aula_stem = aula_info['stem']

            txt_path = Path(aula_info['txt_path']
                            ) if aula_info['txt_path'] else None

            # Definir caminhos para os arquivos de IA para CARREGAR/VERIFICAR EXISTÊNCIA
            summary_path = base_path / "analises_ia" / modulo / aula_stem / "RESUMO.md"
            insights_path = base_path / "analises_ia" / modulo / aula_stem / "INSIGHTS.md"
            quiz_path = base_path / "analises_ia" / modulo / aula_stem / "QUESTIONARIO.md"

            with st.expander(f"🎥 {aula_stem}"):
                # LÊ A TRANSCRIÇÃO UMA ÚNICA VEZ NO INÍCIO DO EXPANDER
                if txt_path and txt_path.exists() and txt_path.stat().st_size > 0:
                    aula_text = _load_content_from_file(txt_path)

                    if not aula_text.strip():  # Se o arquivo TXT existe mas está vazio
                        st.warning(
                            "Transcrição vazia para esta aula. Não foi possível gerar insights/questionário.")
                    else:
                        # --- Abas para organizar Resumo, Insights, Questionário ---
                        tab_summary, tab_insights, tab_quiz = st.tabs(
                            ["📝 Resumo", "💡 Insights", "❓ Questionário"])

                        with tab_summary:
                            # Lógica para exibir
                            if f'summary_{aula_stem}' in st.session_state and st.session_state[f'summary_{aula_stem}']:
                                st.markdown("**Resumo:**")
                                st.write(
                                    st.session_state[f'summary_{aula_stem}'])
                            elif summary_path.exists():
                                st.markdown(
                                    "**Resumo (Carregado do arquivo):**")
                                st.write(_load_content_from_file(summary_path))
                            else:
                                st.info(
                                    "Nenhum resumo gerado ou encontrado para esta aula.")

                            if st.button("💡 Gerar Resumo", key=f"resumo_btn_{aula_stem}_tab"):
                                with st.spinner(f"Gerando resumo para {aula_stem}..."):
                                    summary_content = generate_summary(
                                        aula_text, aula_stem, base_path, modulo, model=gpt_model,
                                        max_tokens=st.session_state.get(
                                            'max_tokens_summary', 400),
                                        temperature=st.session_state.get(
                                            'temperature', 0.3)
                                    )
                                    st.session_state[f'summary_{aula_stem}'] = summary_content
                                    st.success("Resumo gerado e salvo!")
                                    st.rerun()

                        with tab_insights:
                            if f'insights_{aula_stem}' in st.session_state and st.session_state[f'insights_{aula_stem}']:
                                st.markdown("**Insights:**")
                                st.markdown(
                                    st.session_state[f'insights_{aula_stem}'])
                            elif insights_path.exists():
                                st.markdown(
                                    "**Insights (Carregado do arquivo):**")
                                st.markdown(
                                    _load_content_from_file(insights_path))
                            else:
                                st.info(
                                    "Nenhum insight gerado ou encontrado para esta aula.")

                            if st.button("🔍 Gerar Insights", key=f"insights_btn_{aula_stem}_tab"):
                                with st.spinner(f"Gerando insights para {aula_stem}..."):
                                    insights_content = extract_keywords_and_insights(
                                        aula_text, aula_stem, base_path, modulo, model=gpt_model,
                                        max_tokens=st.session_state.get(
                                            'max_tokens_insights', 600),
                                        temperature=st.session_state.get(
                                            'temperature', 0.3)
                                    )
                                    st.session_state[f'insights_{aula_stem}'] = insights_content
                                    st.success("Insights gerados e salvos!")
                                    st.rerun()

                        with tab_quiz:
                            if f'quiz_{aula_stem}' in st.session_state and st.session_state[f'quiz_{aula_stem}']:
                                st.markdown("**Questionário:**")
                                st.code(
                                    st.session_state[f'quiz_{aula_stem}'], language="text")
                            elif quiz_path.exists():
                                st.markdown(
                                    "**Questionário (Carregado do arquivo):**")
                                st.code(_load_content_from_file(
                                    quiz_path), language="text")
                            else:
                                st.info(
                                    "Nenhum questionário gerado ou encontrado para esta aula.")

                            if st.button("❓ Gerar Questionário", key=f"quiz_btn_{aula_stem}_tab"):
                                with st.spinner(f"Gerando questionário para {aula_stem}..."):
                                    quiz_content = generate_quiz_questions(
                                        aula_text, aula_stem, base_path, modulo, model=gpt_model, num_questions=5,
                                        max_tokens=st.session_state.get(
                                            'max_tokens_quiz', 700),
                                        temperature=st.session_state.get(
                                            'temperature', 0.3)
                                    )
                                    st.session_state[f'quiz_{aula_stem}'] = quiz_content
                                    st.success("Questionário gerado e salvo!")
                                    st.rerun()
                else:  # Este else para o if txt_path.exists() (se não houver TXT ou estiver vazio)
                    st.warning(
                        f"Transcrição (.txt) não encontrada ou vazia para {aula_stem}. Transcreva o vídeo ou forneça o .txt para usar as funções de IA.")


# --- Funções Auxiliares Ausentes ---

def calculate_ai_stats(modulos_mapeados: dict, base_path: Path) -> dict:
    """Calcula estatísticas dos arquivos de IA gerados."""
    stats = {
        'total_aulas': 0,
        'resumos_gerados': 0,
        'insights_gerados': 0,
        'questionarios_gerados': 0,
        'progress_resumos': 0,
        'progress_insights': 0,
        'progress_questionarios': 0
    }

    for modulo, aulas_list in modulos_mapeados.items():
        for aula_info in aulas_list:
            aula_stem = aula_info['stem']
            stats['total_aulas'] += 1

            # Verificar arquivos de IA existentes
            summary_path = base_path / "analises_ia" / modulo / aula_stem / "RESUMO.md"
            insights_path = base_path / "analises_ia" / modulo / aula_stem / "INSIGHTS.md"
            quiz_path = base_path / "analises_ia" / modulo / aula_stem / "QUESTIONARIO.md"

            if summary_path.exists():
                stats['resumos_gerados'] += 1
            if insights_path.exists():
                stats['insights_gerados'] += 1
            if quiz_path.exists():
                stats['questionarios_gerados'] += 1

    # Calcular percentuais
    if stats['total_aulas'] > 0:
        stats['progress_resumos'] = (
            stats['resumos_gerados'] / stats['total_aulas']) * 100
        stats['progress_insights'] = (
            stats['insights_gerados'] / stats['total_aulas']) * 100
        stats['progress_questionarios'] = (
            stats['questionarios_gerados'] / stats['total_aulas']) * 100

    return stats


def render_ai_progress(ai_stats: dict):
    """Renderiza o progresso das análises de AI."""
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric(
            "📝 Resumos",
            f"{ai_stats['resumos_gerados']}/{ai_stats['total_aulas']}",
            f"{ai_stats['progress_resumos']:.1f}%"
        )
        st.progress(ai_stats['progress_resumos'] / 100)

    with col2:
        st.metric(
            "💡 Insights",
            f"{ai_stats['insights_gerados']}/{ai_stats['total_aulas']}",
            f"{ai_stats['progress_insights']:.1f}%"
        )
        st.progress(ai_stats['progress_insights'] / 100)

    with col3:
        st.metric(
            "❓ Questionários",
            f"{ai_stats['questionarios_gerados']}/{ai_stats['total_aulas']}",
            f"{ai_stats['progress_questionarios']:.1f}%"
        )
        st.progress(ai_stats['progress_questionarios'] / 100)


def _process_all_ai_content_type(modulos_mapeados: dict, base_path: Path, gpt_model: str, content_type: str, processor_function):
    """Processa todos os conteúdos de um tipo específico."""
    force_regenerate = st.session_state.get('force_regenerate_ia', False)
    processed_count = 0
    error_count = 0

    progress_bar = st.progress(0)
    status_text = st.empty()

    total_aulas = sum(
        len([a for a in aulas if a.get('type', 'video')
            in ('video', 'audio', 'document')])
        for aulas in modulos_mapeados.values()
    )

    current_aula = 0
    for modulo, aulas_list in modulos_mapeados.items():
        for aula_info in aulas_list:
            current_aula += 1
            aula_stem = aula_info['stem']

            # Atualizar progresso
            progress_bar.progress(current_aula / total_aulas)
            status_text.text(
                f"Processando {content_type}: {aula_stem} ({current_aula}/{total_aulas})")

            # Verificar se já existe (se não forçar regeração)
            file_map = {
                'resumo': 'RESUMO.md',
                'insight': 'INSIGHTS.md',
                'questionario': 'QUESTIONARIO.md'
            }

            output_file = base_path / "analises_ia" / modulo / aula_stem / \
                file_map.get(content_type, f"{content_type.upper()}.md")

            if output_file.exists() and not force_regenerate:
                continue

            # Verificar se existe transcrição
            txt_path = Path(aula_info['txt_path']) if aula_info.get(
                'txt_path') else None
            if not txt_path or not txt_path.exists():
                error_count += 1
                continue

            # Carregar conteúdo
            aula_text = _load_content_from_file(txt_path)
            if not aula_text.strip():
                error_count += 1
                continue

            try:
                # Processar baseado no tipo
                if content_type == 'resumo':
                    result = processor_function(
                        aula_text, aula_stem, base_path, modulo,
                        model=gpt_model,
                        max_tokens=st.session_state.get(
                            'max_tokens_summary', 400),
                        temperature=st.session_state.get('temperature', 0.3)
                    )
                elif content_type == 'insight':
                    result = processor_function(
                        aula_text, aula_stem, base_path, modulo,
                        model=gpt_model,
                        max_tokens=st.session_state.get(
                            'max_tokens_insights', 600),
                        temperature=st.session_state.get('temperature', 0.3)
                    )
                elif content_type == 'questionario':
                    result = processor_function(
                        aula_text, aula_stem, base_path, modulo,
                        model=gpt_model, num_questions=5,
                        max_tokens=st.session_state.get(
                            'max_tokens_quiz', 700),
                        temperature=st.session_state.get('temperature', 0.3)
                    )

                if result:
                    processed_count += 1

            except Exception as e:
                st.error(f"Erro ao processar {aula_stem}: {str(e)}")
                error_count += 1

    # Limpar progresso
    progress_bar.empty()
    status_text.empty()

    # Mostrar resultado
    if processed_count > 0:
        st.success(
            f"✅ {processed_count} {content_type}(s) processado(s) com sucesso!")
    if error_count > 0:
        st.warning(f"⚠️ {error_count} erro(s) durante o processamento")


# --- Função Principal da Aplicação ---

def render_token_monitoring_horizontal():
    """Renderiza monitoramento de tokens de forma horizontal no topo."""
    usage = st.session_state.token_usage
    today = datetime.now().strftime('%Y-%m-%d')
    today_usage = usage['daily_usage'].get(today, 0)

    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("🎯 Tokens Totais", f"{usage['total_tokens']:,}")
    with col2:
        st.metric("💰 Custo Est.", f"${usage['estimated_cost']:.3f}")
    with col3:
        st.metric("📅 Hoje", f"{today_usage:,}")
    with col4:
        st.metric("📝 Resumos", f"{usage['resumos']:,}")
    with col5:
        st.metric("💡 Insights", f"{usage['insights']:,}")


def render_footer_credits():
    """Renderiza créditos flutuantes no rodapé."""
    st.markdown("""
    <div style="
        position: fixed;
        bottom: 10px;
        right: 20px;
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        padding: 8px 16px;
        border-radius: 20px;
        font-size: 12px;
        font-weight: 600;
        box-shadow: 0 4px 15px rgba(102, 126, 234, 0.3);
        z-index: 999;
        opacity: 0.8;
        transition: opacity 0.3s ease;
    " onmouseover="this.style.opacity='1'" onmouseout="this.style.opacity='0.8'">
        © 2025 NASCO COMPANY - ALL RIGHTS RESERVED
    </div>
    """, unsafe_allow_html=True)


def main_app():
    """Função principal da aplicação Streamlit."""
    try:
        # Título principal
        st.title("🎓 Analisador de Cursos v4.0 ULTIMATE")
        st.markdown("### 🚀 Análise Inteligente Multi-Formato com AI Avançada")

        # Monitoramento horizontal no topo
        if 'curso_path' in st.session_state and st.session_state.curso_path:
            with st.expander("🎯 Monitoramento de AI", expanded=False):
                render_token_monitoring_horizontal()

        # Renderizar créditos no rodapé
        render_footer_credits()

        # Renderizar sidebar e obter configurações
        caminho_curso, gpt_model = render_sidebar()

        # Verificar se um curso foi carregado
        if 'curso_path' not in st.session_state or not st.session_state.curso_path:
            # Mostrar instruções se nenhum curso foi carregado
            st.info("👈 **Comece selecionando uma pasta de curso na barra lateral**")

            with st.expander("📖 Como usar o Analisador v4.0", expanded=True):
                st.markdown("""
                ## 🎯 **Passo a Passo:**
                
                ### 1. 📁 **Selecione sua pasta de curso**
                - Use o campo de texto ou o botão "📂 Abrir Seletor de Pastas"
                - Suporte para: **Vídeos, Áudios, PDFs, Word, PowerPoint, Legendas**
                
                ### 2. 🎙️ **Transcreva o conteúdo**
                - Vídeos/Áudios: Transcrição automática com Whisper
                - Documentos: Extração de texto automática
                
                ### 3. 🧠 **Gere análises de AI**
                - **Resumos**: Sínteses inteligentes de cada aula
                - **Insights**: Pontos-chave e aplicações práticas  
                - **Questionários**: Testes para fixação do conhecimento
                
                ### 4. 📊 **Relatórios estratégicos**
                - Análise completa do curso
                - Roadmap de aprendizado
                - Recomendações personalizadas
                
                ## 🎯 **Formatos Suportados:**
                - **Vídeos**: MP4, AVI, MOV, MKV, etc.
                - **Áudios**: MP3, WAV, M4A, etc.
                - **Documentos**: PDF, DOCX, PPTX
                - **Legendas**: SRT, VTT, TXT
                """)

            return

        # Curso carregado - processar e exibir
        try:
            with st.spinner("🔄 Carregando dados do curso..."):
                modulos_mapeados = cached_mapear_modulos(
                    st.session_state.curso_path,
                    st.session_state.get('multiformat_enabled', True)
                )

            if not modulos_mapeados:
                st.error("❌ Nenhum conteúdo encontrado na pasta selecionada.")
                return

            # Calcular duração total (apenas para vídeos)
            dur_total_segundos = 0
            for aulas_list in modulos_mapeados.values():
                for aula_info in aulas_list:
                    if aula_info.get('video_path'):
                        try:
                            duration = extrair_duracao(aula_info['video_path'])
                            if duration:
                                dur_total_segundos += duration
                        except:
                            pass

            # Nome do curso (pasta principal)
            curso_nome = Path(st.session_state.curso_path).name
            base_path = Path(st.session_state.curso_path)

            # Renderizar métricas
            render_course_metrics(modulos_mapeados, dur_total_segundos)

            # Renderizar cards de ação
            render_action_cards(modulos_mapeados, base_path,
                                curso_nome, gpt_model)

            # Mostrar resumo detalhado se solicitado
            if st.session_state.get('show_detailed_summary', False):
                with st.expander("🔍 Escopo Detalhado do Curso", expanded=True):
                    st.markdown(f"## 📊 Análise Detalhada: {curso_nome}")

                    for modulo, aulas_list in modulos_mapeados.items():
                        st.markdown(f"### 📂 {modulo}")

                        for aula_info in aulas_list:
                            col1, col2 = st.columns([3, 1])

                            with col1:
                                # Informações da aula
                                aula_type = aula_info.get('type', 'video')
                                type_icon = {'video': '🎥', 'audio': '🎵', 'document': '📄'}.get(
                                    aula_type, '🎥')

                                st.markdown(
                                    f"**{type_icon} {aula_info['stem']}**")

                                # Mostrar metadados se disponíveis
                                if aula_info.get('metadata'):
                                    metadata = aula_info['metadata']
                                    if 'duration' in metadata:
                                        st.caption(
                                            f"⏱️ Duração: {segundos_para_hms(metadata['duration'])}")
                                    if 'pages' in metadata:
                                        st.caption(
                                            f"📄 Páginas: {metadata['pages']}")
                                    if 'size' in metadata:
                                        st.caption(
                                            f"💾 Tamanho: {format_file_size(metadata['size'])}")

                            with col2:
                                # Status icons
                                icons_html = render_status_icons(
                                    aula_info, base_path, modulo)
                                st.markdown(icons_html, unsafe_allow_html=True)

                # Botão para fechar o resumo detalhado
                if st.button("❌ Fechar Resumo Detalhado"):
                    st.session_state.show_detailed_summary = False
                    st.rerun()

        except Exception as e:
            st.error(f"❌ Erro ao processar curso: {str(e)}")
            st.info(
                "💡 Tente recarregar o curso ou verificar se a pasta contém arquivos válidos.")

    except Exception as e:
        st.error(f"❌ Erro crítico na aplicação: {str(e)}")
        st.info("🔄 Recarregue a página para tentar novamente.")


if __name__ == "__main__":
    load_custom_css()  # Carrega o CSS customizado no início
    main_app()
