#!/bin/bash

# Local do seu ambiente virtual (ajuste se o nome ou caminho for diferente)
VENV_PATH="./venv_nasco_v4"

echo "=== Forçando Reinstalação de MoviePy 1.0.3 ==="
echo "Verificando e ativando ambiente virtual..."

# Navega para o diretório do projeto se não estiver já
# Certifique-se que o script é executado do diretório onde venv_nasco_v4 está
if [ ! -d "$VENV_PATH" ]; then
    echo "❌ Ambiente virtual '$VENV_PATH' não encontrado no diretório atual."
    echo "Por favor, execute este script na pasta raiz do seu projeto (onde 'venv_nasco_v4' está)."
    exit 1
fi

# Ativa o ambiente virtual
source "$VENV_PATH/bin/activate" || { echo "Erro ao ativar o ambiente virtual."; exit 1; }
echo "✅ Ambiente virtual ativado."

echo "Desinstalando moviepy existente..."
pip uninstall moviepy -y || true # Use true para não falhar se não estiver instalado

echo "Limpando cache do pip..."
pip cache purge

echo "Instalando moviepy==1.0.3 e suas dependências específicas..."
# Instalar dependências que moviepy 1.0.3 precisa, na ordem e versões corretas,
# para garantir que não haja conflitos com versões mais recentes.
pip install --no-cache-dir "imageio==2.8.0" # moviepy 1.0.3 é mais compatível com imageio 2.8.0, não 2.37.0
pip install --no-cache-dir "imageio-ffmpeg==0.4.8" # Versão mais antiga para compatibilidade
pip install --no-cache-dir "decorator==4.4.0" # moviepy 1.0.3 usa decorator < 5.0.0
pip install --no-cache-dir "proglog==0.1.9" # moviepy 1.0.3 usa proglog <= 1.0.0
pip install --no-cache-dir "numpy>=1.17.3,<1.25.0" # Restringir numpy para versões mais antigas
pip install --no-cache-dir "pillow>=8.3.2,<10.0.0" # Restringir pillow

# Agora instale o moviepy 1.0.3 exato
pip install --no-cache-dir "moviepy==1.0.3" --upgrade --force-reinstall

echo "Verificando instalação de moviepy..."
pip show moviepy

echo "Testando importação de moviepy.editor..."
python -c "from moviepy.editor import VideoFileClip; print('✅ MoviePy.editor OK!')"

if [ $? -eq 0 ]; then # Verifica o status de saída do comando anterior
    echo "🎉 MoviePy 1.0.3 instalado e funcionando corretamente!"
    echo "Agora você pode rodar: streamlit run app.py"
else
    echo "❌ ERRO: MoviePy.editor ainda não pôde ser importado."
    echo "Por favor, verifique as mensagens de erro acima."
fi

# Mantém o terminal aberto para o usuário ver a saída
echo "Pressione [Enter] para fechar esta janela..."
read -r