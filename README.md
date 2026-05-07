# Robo Rename

Automação para separar, organizar e renomear PDFs de forma padronizada.

O projeto foi criado para facilitar o processamento de documentos do setor sem necessidade de abrir terminal, programar ou utilizar interface gráfica.

---

# Como funciona

1. Coloque os PDFs na pasta `entrada`
2. Execute o arquivo `RoboRename.exe`
3. Os arquivos processados serão enviados para a pasta `saida`

---

# Estrutura do projeto

```text
Robo-Rename
│
├── RoboRename.exe
├── robo.py
├── requirements.txt
├── build_exe.bat
├── entrada
├── saida
└── logs

## Instalação do ambiente

Abra o Prompt de Comando na pasta do projeto e execute:

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

Executando pelo Python

Com arquivos PDF dentro da pasta entrada, execute:
python robo.py

## Gerando o executável (.exe)

Execute:
build_exe.bat

Ou manualmente:
pyinstaller --onefile --name RoboRename robo.py

O executável será criado em:
dist/RoboRename.exe
Copie o arquivo .exe para a raiz do projeto.

## Como usar o executável

Estrutura recomendada:
Robo-Rename
│
├── RoboRename.exe
├── entrada
├── saida
└── logs

## Passos:

1- Coloque os PDFs na pasta entrada
2 - Execute RoboRename.exe
3 - Aguarde o processamento
4 - Verifique os arquivos gerados em saida

Logs

Os logs de execução são salvos automaticamente na pasta: logs

Tecnologias utilizadas
- Python
- PyPDF2
- PyInstaller

## Objetivo:

Padronizar e automatizar o tratamento de PDFs do setor, reduzindo trabalho manual e minimizando erros operacionais.

Melhorias futuras
Interface gráfica
Processamento automático em segundo plano
Configuração de regras por arquivo JSON
Histórico de execuções
Suporte a múltiplos layouts de documento

## 🧑‍💻 Desenvolvido por:

Ingrid Aylana | Desenvolvedora Full-Stack | Linkedin: www.linkedin.com/in/ingryd-aylana-silva-dos-santos-4a2701158 | Instagram: https://www.instagram.com/ingrydai_/#