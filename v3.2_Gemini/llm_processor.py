# video_analyzer/v4/llm_processor.py
import openai
from config import OPENAI_API_KEY
from pathlib import Path
from datetime import datetime

if OPENAI_API_KEY:
    openai.api_key = OPENAI_API_KEY
else:
    print("AVISO: Variável de ambiente OPENAI_API_KEY não configurada. Funcionalidades de IA desabilitadas.")

def _save_content(content: str, save_path: Path):
    """Função utilitária para salvar conteúdo em um arquivo, garantindo a pasta."""
    save_path.parent.mkdir(parents=True, exist_ok=True)
    with open(save_path, "w", encoding="utf-8") as f:
        f.write(content)

def detect_course_type(text: str, module_name: str) -> tuple[str, str]:
    """Detecta automaticamente área do curso e público-alvo baseado no conteúdo."""
    
    text_lower = text.lower()
    module_lower = module_name.lower()
    
    areas = {
        "programação": ["python", "javascript", "código", "programar", "desenvolvimento", "software", "api", "framework", "algoritmo", "backend", "frontend", "devops", "cloud", "dados", "machine learning", "ia", "inteligência artificial", "deep learning", "automação", "robôs"],
        "design": ["design", "photoshop", "ilustração", "cores", "tipografia", "ui", "ux", "branding", "criativos", "imagem", "video", "animação", "render", "3d"],
        "marketing": ["marketing", "vendas", "cliente", "campanha", "estratégia", "marca", "seo", "trafego", "ads", "digital", "conteúdo", "redes sociais"],
        "business": ["negócio", "empresa", "gestão", "liderança", "produtividade", "empreendedorismo", "startup", "inovação", "finanças", "investimento", "mercado"],
        "idiomas": ["inglês", "espanhol", "francês", "gramática", "vocabulário", "fluência", "pronúncia"],
        "saúde": ["saúde", "medicina", "nutrição", "exercício", "bem-estar", "psicologia", "terapia"],
        "finanças": ["finanças", "investimento", "dinheiro", "economia", "banco", "bolsa", "cripto", "ativos", "renda", "orçamento"]
    }
    
    detected_area = "Geral"
    for area, keywords in areas.items():
        if any(keyword in text_lower or keyword in module_lower for keyword in keywords):
            detected_area = area.capitalize()
            break
    
    target_audience = "estudantes intermediários"
    if any(word in text_lower for word in ["iniciante", "básico", "introdução", "primeiros passos", "começar do zero"]):
        target_audience = "iniciantes"
    elif any(word in text_lower for word in ["avançado", "expert", "profissional", "complexo", "deep dive", "otimização"]):
        target_audience = "profissionais avançados"
    
    return detected_area, target_audience


def generate_summary(text: str, aula_stem: str, base_course_path: Path, module_name: str, model: str = "gpt-3.5-turbo", max_tokens: int = 400, temperature: float = 0.3) -> str:
    """Gera um resumo didático otimizado do texto fornecido usando um modelo GPT e salva."""
    if not openai.api_key:
        return "Erro: Chave de API OpenAI não configurada. Resumo não gerado."
    if not text.strip():
        return "Texto vazio para resumir."
    
    try:
        course_area, target_audience = detect_course_type(text, module_name)
        
        prompt_content = f"""# 📝 Resumo Didático da Aula: {aula_stem}
### 📂 Módulo: {module_name} | 🎯 Área: {course_area}

---

**CONTEXTO:** Você é um especialista em {course_area} criando material de estudo para {target_audience}.

**OBJETIVO:** Transforme esta transcrição em um resumo didático estruturado que facilite o aprendizado e revisão.

**DIRETRIZES ESPECÍFICAS:**
• **Estrutura obrigatória:**
  1. 🎯 **Objetivo da Aula** (1-2 frases sobre o que será aprendido)
  2. 📋 **Conceitos-Chave** (3-5 conceitos principais com definições curtas)
  3. 🔗 **Conexões** (como se relaciona com o módulo {module_name} e com o curso em geral)
  4. 💡 **Pontos de Atenção** (detalhes importantes que não podem ser esquecidos, armadilhas comuns)
  5. 📝 **Resumo Executivo** (síntese em 2-3 parágrafos, concluindo a aula)

• **Tamanho:** Entre 200-350 palavras (aprox.)
• **Tom:** Didático, direto, envolvente e inspirador, como um bom professor explicaria.
• **Foco:** Compreensão profunda e aplicação prática, não apenas memorização.
• **Formatação:** Use Markdown para cabeçalhos, listas de tópicos e negrito para clareza, como um documento do Notion. Inclua emojis relevantes se apropriado.

**TRANSCRIÇÃO DA AULA:**
{text[:8000]}

---
**IMPORTANTE:** Se a transcrição estiver incompleta ou com baixa qualidade, foque nos conceitos mais claros e indique áreas que podem precisar de material complementar ou que não foram abordadas."""

        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"Você é um especialista em {course_area} e educação, criando materiais didáticos excepcionais. Seu objetivo é facilitar o aprendizado através de resumos estruturados e práticos."},
                {"role": "user", "content": prompt_content}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        summary = response.choices[0].message.content.strip()
        
        # ✅ CORREÇÃO: Estrutura correta sem pasta extra "resumos"
        summary_dir = base_course_path / "analises_ia" / module_name / aula_stem
        summary_filename = "RESUMO.md"
        summary_save_path = summary_dir / summary_filename
        _save_content(summary, summary_save_path)
        
        return summary
    except openai.APIError as e:
        return f"Erro da API OpenAI ao gerar resumo: {e}"
    except Exception as e:
        return f"Erro inesperado ao gerar resumo: {e}"


def generate_quiz_questions(text: str, aula_stem: str, base_course_path: Path, module_name: str, num_questions: int = 5, model: str = "gpt-3.5-turbo", max_tokens: int = 700, temperature: float = 0.3) -> str:
    """Gera questionário educacional avançado baseado na taxonomia de Bloom e salva."""
    if not openai.api_key:
        return "Erro: Chave de API OpenAI não configurada. Questionário não gerado."
    if not text.strip():
        return "Texto vazio para gerar questionário."
    
    try:
        course_area, _ = detect_course_type(text, module_name)
        difficulty = "intermediário"
        
        prompt_content = f"""# ❓ Avaliação Educacional: {aula_stem}
### 📂 Módulo: {module_name} | 🎯 Área: {course_area} | 📊 Nível: {difficulty}

---

**CONTEXTO:** Você é um especialista em avaliação educacional criando questões que testem diferentes níveis de compreensão para o curso de {course_area}.

**OBJETIVO:** Criar {num_questions} questões diversificadas seguindo a Taxonomia de Bloom.

**DISTRIBUIÇÃO OBRIGATÓRIA (se possível, ajuste se o conteúdo for limitado):**
• 40% - **Compreensão** (entender conceitos principais, ex: "O que é X?")
• 30% - **Aplicação** (usar conhecimento em situações práticas, ex: "Como você aplicaria X em Y?")
• 20% - **Análise** (quebrar informações em partes, identificar relações, ex: "Qual a relação entre X e Y?")
• 10% - **Síntese/Avaliação** (combinar elementos, fazer julgamentos, ex: "Qual a melhor abordagem para X, e por quê?")

**FORMATO RIGOROSO (use exatamente este template para cada questão):**
Questão [N] - [NÍVEL: Compreensão/Aplicação/Análise/Síntese/Avaliação]
Pergunta: [Pergunta clara e específica relacionada ao conteúdo da aula]

A) [Opção plausível mas incorreta]
B) [Opção correta - deve ser inequívoca e baseada no texto]
C) [Opção plausível mas incorreta]
D) [Opção obviamente incorreta para eliminar chutes]

✅ Resposta Correta: [Letra da opção correta, ex: B]
📝 Justificativa: [Explicação concisa (1-2 frases) do porquê a resposta está correta, referenciando o conteúdo da aula.]


**CRITÉRIOS DE QUALIDADE:**
• Questões práticas, não decorativas, diretamente relacionadas ao texto fornecido.
• Opções de tamanho similar.
• Evitar "todas as anteriores" ou "nenhuma das anteriores".
• Cenários realistas quando possível.
• Linguagem clara, sem ambiguidades.
• Certifique-se de que a resposta correta e a justificativa estão INEQUIVOCAMENTE presentes no texto da aula.

**CONTEÚDO DA AULA:**
{text[:8000]}

---
**IMPORTANTE:** Se o conteúdo for insuficiente para {num_questions} questões de qualidade e diversidade, crie menos questões mas com alta qualidade pedagógica, mantendo o formato rigoroso."""

        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"Você é um especialista em avaliação educacional para a área de {course_area}, criando questionários desafiadores e com justificativas detalhadas. Seu objetivo é garantir a máxima clareza e fidelidade ao conteúdo da aula."},
                {"role": "user", "content": prompt_content}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        questions = response.choices[0].message.content.strip()
        
        # ✅ CORREÇÃO: Estrutura correta sem pasta extra "questionarios"
        quiz_dir = base_course_path / "analises_ia" / module_name / aula_stem
        quiz_filename = "QUESTIONARIO.md"
        quiz_save_path = quiz_dir / quiz_filename
        _save_content(questions, quiz_save_path)
        return questions
    except openai.APIError as e:
        return f"Erro da API OpenAI ao gerar questionário: {e}"
    except Exception as e:
        return f"Erro inesperado ao gerar questionário: {e}"


def extract_keywords_and_insights(text: str, aula_stem: str, base_course_path: Path, module_name: str, model: str = "gpt-3.5-turbo", max_tokens: int = 600, temperature: float = 0.3, practical_focus: bool = True) -> str:
    """Extrai palavras-chave e insights principais do texto usando um modelo GPT e salva."""
    if not openai.api_key: return "Erro: Chave de API OpenAI não configurada. Insights não gerados."
    if not text.strip(): return "Texto vazio para extrair insights."
    
    try:
        course_area, _ = detect_course_type(text, module_name)
        
        practical_instruction = f"""
## 🚀 Aplicações Práticas
[3-4 exemplos concretos de como aplicar o conhecimento da aula em cenários reais de {course_area} ou trabalho]
• **[Exemplo 1]:** [Como aplicar]
• **[Exemplo 2]:** [Como aplicar]
...

## 🛠️ Projetos Sugeridos
[2-3 ideias de exercícios práticos ou mini-projetos para fixar o aprendizado]
• **[Ideia 1]:** [Descrição breve + tecnologias/conceitos envolvidos]
• **[Ideia 2]:** [Descrição breve + tecnologias/conceitos envolvidos]
...""" if practical_focus else ""
        
        prompt_content = f"""# 💡 Análise Estratégica da Aula: {aula_stem}
### 📂 Módulo: {module_name} | 🎯 Área: {course_area}

---

**CONTEXTO:** Você é um consultor educacional e estrategista em {course_area} identificando os elementos mais valiosos para acelerar o aprendizado.

**OBJETIVO:** Extrair insights estratégicos que conectem teoria com prática e facilitem a retenção e uso do conhecimento.

**ESTRUTURA OBRIGATÓRIA:**

## 🎯 Conceitos Fundamentais
[Liste 4-6 conceitos que são pilares para o entendimento desta aula. Para cada um:]
• **[Conceito-chave]:** [Definição concisa (1 linha) + por que é fundamental para esta aula.]

## 🔗 Mapa de Conexões
[Identifique relações importantes desta aula com o contexto maior.]
• **Pré-requisitos:** [O que o aluno idealmente precisa saber antes desta aula.]
• **Conecta com:** [Outros tópicos/módulos dentro do curso ou em outras áreas de {course_area} relacionados a esta aula.]
• **Prepara para:** [Próximos conceitos ou habilidades que esta aula habilita o aluno a aprender.]

## ⚡ Insights de Alto Impacto
[3-4 percepções que fazem diferença real no entendimento ou na forma de abordar o assunto. Não óbvios.]
• **[Insight Principal]:** [Como essa percepção muda a perspectiva ou otimiza a aplicação prática. Use emojis para destacar.]

{practical_instruction}

## 🎓 Dicas de Estudo
[Estratégias para otimizar o aprendizado e retenção.]
• **Para fixar:** [Técnica de estudo específica para memorizar/entender o conteúdo desta aula.]
• **Comum confundir:** [Erros típicos que os estudantes cometem e como evitá-los. Use ⚠️ emoji.]
• **Maneira fácil:** [Analogia ou método simples e criativo para lembrar um conceito complexo.]

## 📊 Relevância no Módulo
**Peso:** [Alto/Médio/Baixo] | **Complexidade:** [Básico/Intermediário/Avançado]
**Por que importa:** [1-2 frases sobre o impacto direto e a importância desta aula no módulo {module_name} e no aprendizado geral.]

**CONTEÚDO DA AULA:**
{text[:8000]}

---
**FOCO:** Priorize insights que realmente aceleram o aprendizado, a aplicação e a retenção, e que são específicos ao conteúdo da aula. Mantenha a formatação Markdown perfeita, incluindo quebras de linha para legibilidade."
"""
        response = openai.chat.completions.create(
            model=model,
            messages=[
                {"role": "system", "content": f"Você é um consultor educacional e estrategista focado em {course_area}, com foco em extrair valor prático e insights acionáveis, formatando-os impecavelmente em Markdown."},
                {"role": "user", "content": prompt_content}
            ],
            max_tokens=max_tokens,
            temperature=temperature
        )
        insights = response.choices[0].message.content.strip()
        
        # ✅ CORREÇÃO: Estrutura correta sem pasta extra "insights"
        insights_dir = base_course_path / "analises_ia" / module_name / aula_stem
        insights_filename = "INSIGHTS.md"
        insights_save_path = insights_dir / insights_filename
        _save_content(insights, insights_save_path)
        return insights
    except openai.APIError as e:
        return f"Erro da API OpenAI ao extrair insights: {e}"
    except Exception as e:
        return f"Erro inesperado ao extrair insights: {e}"