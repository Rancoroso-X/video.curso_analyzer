#!/bin/bash
# 🎬 CORREÇÃO MOVIEPY - PASTA CORRETA - NASCO v4.0 ULTIMATE

echo "🎬 Corrigindo MoviePy - Estrutura Correta"
echo "========================================="

# Navegar para pasta correta
cd /Users/gabrielnasco/Desktop/AI/PROG/VSCode/PROJETOS/PROJETOS_TESTE/video_analyzer/APP

echo "📁 Pasta atual: $(pwd)"

# Verificar se estamos na pasta certa
if [ ! -f "app.py" ]; then
    echo "❌ app.py não encontrado na pasta atual"
    echo "Verifique se está na pasta correta: video_analyzer/APP"
    exit 1
fi

echo "✅ Pasta correta identificada"

# Ativar ambiente virtual
echo "🔌 Ativando ambiente virtual..."
source venv_nasco_v4/bin/activate

# Verificar ativação
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ Ambiente virtual ativo"
else
    echo "❌ Ambiente virtual não ativou"
    echo "Criando novo ambiente..."
    python3 -m venv venv_nasco_v4
    source venv_nasco_v4/bin/activate
fi

# Atualizar pip
echo "📦 Atualizando pip..."
python -m pip install --upgrade pip

# Instalar FFmpeg se necessário
echo "🎥 Verificando FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg encontrado"
else
    echo "⚠️ Instalando FFmpeg..."
    if command -v brew &> /dev/null; then
        brew install ffmpeg
    else
        echo "❌ Homebrew não encontrado - instale FFmpeg manualmente"
    fi
fi

# Instalar dependências do MoviePy em ordem específica
echo "📹 Instalando dependências do MoviePy..."
pip install imageio>=2.25.0
pip install imageio-ffmpeg>=0.4.8
pip install decorator>=4.4.2

# Instalar MoviePy
echo "🎬 Instalando MoviePy..."
pip install moviepy>=1.0.3

# Testar MoviePy
echo "🧪 Testando MoviePy..."
python -c "
try:
    from moviepy.editor import VideoFileClip
    print('✅ MoviePy importado com sucesso')
    import moviepy
    print(f'✅ MoviePy versão: {moviepy.__version__}')
except Exception as e:
    print(f'❌ Erro no MoviePy: {e}')
    exit(1)
"

# Instalar outras dependências críticas
echo "📋 Instalando dependências críticas..."
pip install streamlit>=1.28.0
pip install openai>=1.3.0
pip install openai-whisper>=20231117
pip install python-dotenv>=1.0.0

# Verificar se requirements.txt existe e instalar
if [ -f "requirements.txt" ]; then
    echo "📄 Instalando requirements.txt..."
    pip install -r requirements.txt
else
    echo "⚠️ requirements.txt não encontrado, continuando..."
fi

# Teste completo das importações
echo "🔍 Teste completo de importações..."
python -c "
critical_modules = [
    ('streamlit', 'Streamlit'),
    ('openai', 'OpenAI'), 
    ('moviepy.editor', 'MoviePy'),
    ('whisper', 'Whisper')
]

failed = []
for module, name in critical_modules:
    try:
        __import__(module)
        print(f'✅ {name}')
    except ImportError as e:
        print(f'❌ {name}: {e}')
        failed.append(name)

if failed:
    print(f'\\nFalharam: {failed}')
else:
    print('\\n🎉 Todas as dependências críticas OK!')
"

# Verificar estrutura de arquivos
echo "📁 Verificando arquivos essenciais..."
files_to_check=("app.py" "analyzer.py" "config.py")
for file in "${files_to_check[@]}"; do
    if [ -f "$file" ]; then
        echo "✅ $file"
    else
        echo "⚠️ $file não encontrado"
    fi
done

# Criar .env se não existir
if [ ! -f ".env" ]; then
    echo "⚙️ Criando arquivo .env..."
    echo "OPENAI_API_KEY=sk-proj-INSIRA_SUA_CHAVE_AQUI" > .env
    echo "⚠️ Configure sua OPENAI_API_KEY no arquivo .env"
fi

echo ""
echo "🎉 CORREÇÃO CONCLUÍDA!"
echo "====================="
echo ""
echo "📁 Pasta atual: $(pwd)"
echo ""
echo "Para executar a aplicação:"
echo "1. Configure sua API key no arquivo .env"
echo "2. Execute: streamlit run app.py"
echo ""
echo "Para reativar o ambiente no futuro:"
echo "cd $(pwd)"
echo "source venv_nasco_v4/bin/activate"