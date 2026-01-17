# AGENTS

## Como rodar
- Requer Python 3.11+
- Exemplo (CRM apenas):
  - `python -m core.cli --input-crm tests/fixtures/crm_sample.csv --out-dir out`
- Exemplo (CRM + Google):
  - `python -m core.cli --input-crm tests/fixtures/crm_sample.csv --input-google tests/fixtures/google_sample.csv --out-dir out --label CRM_2025`
- UI (M2):
  - `python main.py`

## Convenções do projeto
- Regra de negócio fica em `core/`; QML não contém lógica de negócio.
- Telefone sempre tratado como string e normalizado para dígitos.
- Nome bom nunca é sobrescrito por `.` ou vazio.
- Saída sempre em lotes (default 3000) e `report.json` é obrigatório.
- Use `snake_case` em módulos e funções.

## Como testar
- Rodar testes unitários:
  - `python -m unittest`
