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

## Como Usar (Desenvolvimento)

1.  **Instale as dependências**:
    ```bash
    pip install -r requirements.txt
    ```

2.  **Execute a aplicação**:
    ```bash
    python main.py
    ```

## Como Usar (Versão Executável)

1.  Baixe o arquivo `.zip` da última release.
2.  Extraia o conteúdo do arquivo em uma pasta no seu computador.
3.  Execute o arquivo `main.exe` que está dentro da pasta `main.dist`.

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
- `dist/`: Contém os arquivos da versão compilada (executável).
- `requirements.txt`: Dependências da aplicação.