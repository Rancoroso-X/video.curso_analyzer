#!/bin/bash
# 🎓 CORREÇÃO RÁPIDA - NASCO v4.0 ULTIMATE macOS

echo "🎓 NASCO v4.0 ULTIMATE - Correção de Instalação macOS"
echo "=================================================="

# Verificar se está no diretório correto
if [ ! -f "requirements.txt" ]; then
    echo "❌ requirements.txt não encontrado"
    echo "Execute este script na pasta raiz do projeto"
    exit 1
fi

# 1. Limpar ambiente antigo
echo "🧹 Limpando ambiente antigo..."
deactivate 2>/dev/null || true
rm -rf venv
rm -rf venv_nasco_v4

# 2. Verificar Python
echo "🐍 Verificando Python..."
if ! command -v python3 &> /dev/null; then
    echo "❌ Python3 não encontrado"
    echo "Instale Python 3.8+ primeiro"
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "✅ Python $PYTHON_VERSION encontrado"

# 3. Criar novo ambiente virtual
echo "🏗️ Criando novo ambiente virtual..."
python3 -m venv venv_nasco_v4

# 4. Ativar ambiente
echo "🔌 Ativando ambiente virtual..."
source venv_nasco_v4/bin/activate

# 5. Verificar ativação
echo "🔍 Verificando ativação..."
which python
which pip

# 6. Atualizar pip
echo "📦 Atualizando pip..."
python -m pip install --upgrade pip

# 7. Instalar dependências essenciais primeiro
echo "⚡ Instalando dependências essenciais..."
pip install streamlit>=1.28.0
pip install openai>=1.3.0
pip install python-dotenv>=1.0.0

# 8. Verificar instalação básica
echo "✅ Testando instalação básica..."
python -c "import streamlit; print('✅ Streamlit OK')"
python -c "import openai; print('✅ OpenAI OK')"
python -c "from dotenv import load_dotenv; print('✅ DotEnv OK')"

# 9. Instalar requirements completo
echo "📋 Instalando requirements completo..."
pip install -r requirements.txt

# 10. Verificar FFmpeg
echo "🎬 Verificando FFmpeg..."
if command -v ffmpeg &> /dev/null; then
    echo "✅ FFmpeg encontrado"
else
    echo "⚠️ FFmpeg não encontrado"
    echo "Instale com: brew install ffmpeg"
fi

# 11. Criar .env se não existir
if [ ! -f ".env" ]; then
    echo "⚙️ Criando arquivo .env..."
    cp .env.template .env 2>/dev/null || echo "OPENAI_API_KEY=sk-proj-INSIRA_SUA_CHAVE_AQUI" > .env
    echo "⚠️ Configure sua OPENAI_API_KEY no arquivo .env"
fi

# 12. Testar estrutura
echo "📁 Verificando estrutura..."
if [ -d "video_analyzer/v4" ]; then
    echo "✅ Estrutura v4.0 encontrada"
else
    echo "⚠️ Criando estrutura v4.0..."
    mkdir -p video_analyzer/v4
fi

# 13. Teste final
echo "🧪 Teste final..."
streamlit --version

echo ""
echo "🎉 INSTALAÇÃO CORRIGIDA!"
echo "========================"
echo ""
echo "📋 Próximos passos:"
echo "1. Configure sua API key no arquivo .env"
echo "2. Execute: cd video_analyzer/v4"
echo "3. Execute: streamlit run app.py"
echo ""
echo "🔧 Para ativar o ambiente no futuro:"
echo "source venv_nasco_v4/bin/activate"
echo ""
echo "Para verificar se tudo está OK:"
echo "python quick_check.py"