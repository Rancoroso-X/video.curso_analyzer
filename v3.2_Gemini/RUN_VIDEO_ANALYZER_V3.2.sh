#!/bin/bash

# Local do diretório do seu projeto (ajuste se a pasta "v3_Gemini" for renomeada)
PROJECT_DIR="/Users/gabrielnasco/Desktop/AI/PROG/VSCode/PROJETOS/PROJETOS_TESTE/video_analyzer/v3_Gemini"

# Navega para o diretório do projeto
cd "$PROJECT_DIR" || { echo "Erro: Diretório do projeto não encontrado. Verifique o caminho."; exit 1; }

# Ativa o ambiente virtual
# Verifica se o venv existe antes de ativar
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
else
    echo "Erro: Ambiente virtual 'venv' não encontrado. Por favor, execute 'python3 -m venv venv' e 'pip install -r requirements.txt' primeiro."
    exit 1
fi

# Inicia o aplicativo Streamlit
echo "Iniciando o Analisador de Cursos NASCO..."
streamlit run app.py

echo "Pressione [Enter] para fechar esta janela do terminal..."
read -r # Espera o usuário pressionar Enter antes de fechar o terminal