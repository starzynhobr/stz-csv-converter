# Roadmap: Conversor/Mesclador de CSV para Google Contatos (PySide6 + QML)

Objetivo: importar **CSV do CRM** + (opcional) **CSV exportado do Google Contatos**, **normalizar**, **mesclar**, **deduplicar** e **gerar CSVs** prontos para importar no Google, com controle fino via UI QML.

> Observação de limites (impacta o design): o Google costuma limitar importação via CSV a ~**3.000 contatos por arquivo**, então o app deve **fatiar a saída em lotes**. citeturn0search0turn0search15  
> Também existe limite total em torno de **25.000 contatos** por conta (e limites de armazenamento). citeturn0search19turn0search1

---

## Stack recomendada

### UI / App
- **Python 3.11+**
- **PySide6 (Qt for Python)**
- **QML (Qt Quick)** para a interface
- **Qt Quick Dialogs** para seleção de arquivos/pasta (FileDialog). citeturn0search2turn0search6

### Core (conversão/merge)
- `csv` (stdlib) para leitura/escrita estável e rápida.
- Opcional:
  - `charset-normalizer` (detecção de encoding) ou estratégia “tentativa controlada”.
  - `ftfy` (conserto de mojibake) se você quiser um botão “Corrigir acentos”.
- `re` para normalização de telefone (somente dígitos).

### Concorrência (não travar a UI)
- Executar processamento em **worker thread** e comunicar progresso com **signals/slots** (thread-safe). citeturn0search10turn0search14

---

## Arquitetura (pra já nascer escalável)

### Regra de ouro
**UI não faz regra de negócio.** UI só:
- coleta configurações
- dispara execução
- exibe progresso/preview/relatório

### Módulos sugeridos
- `io/`
  - `read_crm_csv.py`
  - `read_google_csv.py`
  - `write_google_csv.py`
- `normalize/`
  - `phone.py` (somente dígitos, DDI padrão, etc.)
  - `name.py` (trim, tratar '.' como vazio)
  - `textfix.py` (opcional: “corrigir acentos”)
- `merge/`
  - `dedupe.py` (índice por telefone)
  - `merge_rules.py` (regras de “melhor nome”, concatenar notes, etc.)
- `app/`
  - `controller.py` (ponte QML → core, signals)
  - `models.py` (modelos para preview/duplicados)
  - `worker.py` (QThread/QThreadPool)

---

## Definições e regras (bem objetivas)

### Normalização de telefone
- Transformar em **string** (nunca número).
- Remover tudo que não é dígito.
- Se faltar DDI, assumir `55` (configurável).
- Formato final interno: **`55` + número** (sem espaços), para dedupe consistente.
- Na exportação, permitir escolher:
  - `55...` (sem `+`)
  - `+55...` (padrão internacional, se você preferir)
> Importante: consistência interna > estética do formato.

### Deduplicação
- Chave: **telefone normalizado**.
- Merge:
  - **Nome**: nunca substituir um nome “bom” por `.`/vazio.
  - **Notes**: concatenar (Tags, Atendente, Criado em, origem do arquivo).
  - **Labels/Grupos**: adicionar uma label (ex: `CRM_2025`) para rastrear e desfazer.

### Saída em lotes
- Exportar em arquivos `saida_001.csv`, `saida_002.csv`…
- Tamanho padrão: **3000** (configurável). citeturn0search0turn0search15

---

## UI QML: telas e botões (controle sem bagunça)

### Tela 1: Importação
**Objetivo:** selecionar arquivos e validar colunas.

Componentes:
- Botões:
  - **Selecionar CSV do CRM…** (FileDialog) citeturn0search2
  - **Selecionar CSV do Google (opcional)…**
  - **Auto-detectar separador/encoding**
  - **Pré-visualizar 50 linhas**
  - **Validar colunas**
- Campos:
  - Separador: Auto / `;` / `,` / `\t`
  - Encoding: Auto / UTF-8 / UTF-8 BOM / Latin-1/Win-1252
- Alertas/Badges:
  - “Coluna de telefone encontrada: OK”
  - “X linhas sem telefone (serão ignoradas)”
  - “Caracteres suspeitos detectados (Ã, â, �)”

### Tela 2: Regras
**Objetivo:** definir como normalizar/mesclar.

Seções:
- **Telefone**
  - [x] Remover não-dígitos
  - DDI padrão: `55`
  - [x] Assumir DDI quando faltar
- **Nome**
  - [x] Tratar `.` como vazio
  - [x] Não sobrescrever nome existente por vazio
- **Deduplicação**
  - [x] Deduplicar por telefone
  - Merge strategy (dropdown):
    - “Melhor nome + concat notes”
    - “Sempre manter nome do Google”
    - “Sempre manter nome do CRM”
- **Saída**
  - Label/Grupo: `CRM_2025`
  - Lote por arquivo: `3000`
  - Formato telefone: `55...` / `+55...`

### Tela 3: Resultado / Auditoria
**Objetivo:** confiança antes de importar.

- Cards de números:
  - Lidos: N
  - Sem telefone: N
  - Duplicados fundidos: N
  - Saídas geradas: N arquivos
- Tabela “Top problemas”:
  - Telefones curtos/longos
  - Linhas com nome quebrado (se detectado)
- Botões:
  - **Dry-run (só relatório)**  
  - **Gerar CSVs**
  - **Abrir pasta de saída**
  - **Exportar relatório (JSON/CSV)**

### Extra (opcional, mas poderoso)
- Tela “Resolver duplicados manualmente”:
  - lista de conflitos (mesmo telefone, nomes diferentes)
  - botões: “manter A”, “manter B”, “mesclar notes”
> Só vale fazer se você realmente precisar de curadoria. Senão, automático é rei.

---

## Progresso, logs e cancelamento (não travar e não perder controle)

- Rodar processamento em thread de trabalho.
- Emitir signals:
  - `progress(percent)`
  - `status(text)`
  - `finished(result)`
  - `error(message, details)`
- Botão **Cancelar**: setar um flag `cancelled` verificado a cada X linhas.
- UI deve permanecer responsiva (scroll, filtros, etc.). citeturn0search10turn0search14

---

## Boas práticas de dados (pra não se arrepender depois)

- **Nunca editar o CSV original**: sempre trabalhar em cópia/memória.
- Salvar “configurações da última execução” em `config.json`.
- Manter um `report.json` com:
  - contagens
  - amostras de entradas descartadas
  - parâmetros usados
- Versionar o template do Google (cabeçalho) dentro do projeto.

---

## Plano de execução (milestones)

### M0: Base do projeto
- Estrutura de pastas + CLI mínima (`--input-crm`, `--input-google`, `--out-dir`).
- Leitura robusta de CSV (separador/encoding).
- Normalização de telefone.
- Escrita do CSV no template Google.

### M1: Deduplicação e merge
- Índice por telefone.
- Regras de “melhor nome”.
- Notes agregadas.
- Relatório JSON.

### M2: UI QML (MVP)
- FileDialog (selecionar arquivos) citeturn0search2
- Tela de regras + preview 50 linhas.
- Barra de progresso + cancelar.
- Gerar CSVs em lotes (3000). citeturn0search0

### M3: Auditoria e qualidade
- Tabela de “suspeitos” (telefones inválidos, nomes quebrados).
- Botão “Corrigir acentos” (opcional).
- Exportar relatório.

### M4: Refinos de produto
- “Resolver duplicados manualmente” (se fizer sentido).
- Perf/UX (virtualização de listas, filtros rápidos).
- Empacotamento (Windows): gerar .exe.

---

## Checklist de “não quebra isso”
- [ ] Telefone sempre como **string**
- [ ] Dedupe sempre em cima de telefone **normalizado**
- [ ] Não sobrescrever nome bom por vazio/ponto
- [ ] Saída em lotes (3000) pra não bater limite de import citeturn0search0
- [ ] Processamento fora da thread da UI citeturn0search10turn0search14

---

## Convenção sugerida (pra você não se perder)
- `core/` não importa nada de UI.
- `ui/` não contém regra de negócio.
- Tudo configurável via `Config` (dataclass) serializável em JSON.
