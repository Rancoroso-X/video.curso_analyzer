# 🎬 Video Analyzer v4 – Analisador Inteligente de Cursos em Vídeo

O **Video Analyzer v4 ULTIMATE** é uma aplicação web Python para **transcrição, organização e análise de cursos em vídeo**. Com suporte a **IA generativa**, extrai áudios, gera transcrições com Whisper, organiza conteúdo educacional e permite análises via GPT.

## 🚀 Funcionalidades

- 🎧 Extração automática de áudio com FFmpeg (.wav/.mp3)
- ✍️ Transcrição precisa com Whisper (OpenAI)
- 📄 Geração de `.srt` e `.txt`
- ⚙️ Processamento paralelo com feedback visual
- 📚 Organização por módulos e aulas
- 🤖 Análise com IA (GPT via API)
- 💻 Interface Web (Streamlit)

## 📦 Instalação

```bash
git clone https://github.com/Rancoroso-X/video.curso_analyzer.git
cd video.curso_analyzer
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.template .env  # edite sua API KEY aqui
```

## ▶️ Uso

```bash
python main.py
```

## 🔧 Estrutura

```
📁 video.curso_analyzer/
├── main.py
├── app.py
├── analyzer.py
├── file_processor.py
├── orchestrated_processor.py
├── llm_processor.py
├── ...
```

## 🤝 Contribuição

Contribuições são bem-vindas! Relate bugs ou envie melhorias via Pull Request.

## 📄 Licença

MIT
