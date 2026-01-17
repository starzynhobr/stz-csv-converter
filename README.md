# STZ CSV Converter

O STZ CSV Converter é uma ferramenta de desktop desenvolvida em Python com PySide6 (Qt for Python) e QML para processar, limpar e converter arquivos CSV de contatos, preparando-os para importação em outros sistemas, com foco especial no formato do Google Contacts.

## Funcionalidades

A aplicação oferece uma interface gráfica para facilitar a conversão de arquivos CSV, com as seguintes funcionalidades:

- **Seleção de Arquivos**: Permite selecionar um arquivo CSV de um CRM genérico e/ou um arquivo CSV do Google Contacts como entrada.
- **Diretório de Saída**: O usuário pode escolher onde os arquivos processados serão salvos.
- **Processamento Configurável**: Oferece diversas opções para customizar o processamento dos dados:
    - **Normalização de Telefones**: Adiciona um DDI padrão, remove caracteres inválidos e padroniza o formato dos números.
    - **Deduplicação**: Identifica e mescla contatos duplicados com base no número de telefone.
    - **Enriquecimento de Nomes**: Protege nomes bem formatados e renomeia nomes que se parecem com números de telefone.
    - **"Explosão" de Contatos**: Cria múltiplas entradas de contato a partir de uma única linha que contenha vários números de telefone.
    - **Mapeamento de Colunas**: Permite que o usuário especifique quais colunas do CSV de entrada correspondem a campos como `Nome`, `Telefone`, `DDI`, `Tags`, etc.
- **Validação de Dados**: Antes de executar o processamento completo, a ferramenta realiza uma validação rápida:
    - Mostra uma pré-visualização dos dados como serão lidos.
    - Detecta possíveis problemas de codificação de caracteres (mojibake).
    - Apresenta informações sobre as colunas detectadas.
- **Execução em Segundo Plano**: O processamento dos arquivos é feito em uma thread separada para não bloquear a interface do usuário.
- **Modos de Execução**:
    - **Dry Run (Simulação)**: Executa todo o pipeline de processamento sem salvar os arquivos de saída, permitindo verificar o resultado e os logs.
    - **Run (Execução Real)**: Processa e salva os arquivos CSV convertidos no diretório de saída.
- **Relatórios Detalhados**: Ao final do processamento, gera um relatório em formato JSON com estatísticas, avisos e uma lista de contatos "suspeitos" que podem precisar de correção manual. Um resumo também é apresentado na tela.

## Como Usar

1.  **Instale as dependências**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Execute a aplicação**:
    ```bash
    python main.py
    ```

3.  **Na interface da aplicação**:
    - **Passo 1: Importação**:
        - Clique em "Selecionar CSV do CRM" e/ou "Selecionar CSV do Google" para escolher seus arquivos de entrada.
        - Clique em "Selecionar Pasta de Saída" para definir onde os resultados serão salvos.
        - Clique em "Validar Entradas" para verificar seus arquivos. A aplicação mostrará uma prévia e informações sobre os dados.
    - **Passo 2: Regras**:
        - Ajuste as regras de processamento conforme sua necessidade (DDI padrão, tamanho do telefone, etc.).
        - Se necessário, mapeie manualmente as colunas do seu CSV para os campos esperados pela aplicação.
    - **Passo 3: Execução**:
        - Verifique os logs e o status da validação.
        - Clique em "Iniciar Simulação" para testar suas configurações.
        - Se a simulação ocorrer como esperado, clique em "Iniciar Execução" para gerar os arquivos finais.
    - **Passo 4: Resultados**:
        - Veja o resumo do processamento.
        - Abra o diretório de saída ou o relatório JSON diretamente pelos botões na interface.
        - Copie o resumo para a área de transferência.

## Estrutura do Projeto

- `main.py`: Ponto de entrada da aplicação. Inicializa o ambiente Qt/QML.
- `app/`: Contém a lógica da interface gráfica.
    - `controller.py`: A classe principal que conecta a interface QML com a lógica de negócio (backend).
    - `models.py`: Modelos de dados para preencher as listas e tabelas na interface QML.
    - `worker.py`: Workers que executam a validação e o pipeline de processamento em threads separadas.
- `core/`: Contém a lógica de negócio principal para o processamento dos dados.
    - `pipeline.py`: Orquestra as etapas de leitura, normalização, merge e escrita.
    - `io/`: Módulos para leitura e escrita de arquivos CSV.
    - `normalize/`: Módulos para normalização de dados (nomes, telefones, etc.).
    - `merge/`: Módulos para deduplicação e fusão de contatos.
    - `config.py`: Classes de configuração.
- `ui/qml/`: Arquivos QML que definem a interface do usuário.
    - `Main.qml`: Arquivo principal da interface.
    - `pages/`: As diferentes telas (páginas) da aplicação.
    - `components/`: Componentes reutilizáveis da interface.
- `tests/`: Testes unitários para a lógica de negócio.
- `.venv/`: Ambiente virtual do Python.
- `requirements.txt`: Dependências da aplicação.
- `contacts.csv`: Arquivo de exemplo (não incluído no repositório).
