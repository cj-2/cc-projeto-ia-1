# Controle de Gastos Pessoais

## Descrição do projeto

API REST para controle de gastos pessoais: permite registrar transações financeiras (entradas e
saídas), consultá-las, categorizá-las e obter resumos/saldos. Projeto construído de forma
incremental, uma feature por "aula" (ver `specs/`).

## Stack

- Python 3.11+
- FastAPI
- SQLite (acesso via `sqlite3`, módulo padrão do Python — sem ORM)
- Pydantic (schemas de request/response)

## Como rodar

```bash
python -m venv venv
venv\Scripts\activate        # Windows
source venv/bin/activate     # Linux/Mac

pip install -r requirements.txt
uvicorn app.main:app --reload
```

A API sobe em `http://127.0.0.1:8000`; documentação interativa em `/docs`.

O banco SQLite (`gastos.db`) é criado automaticamente na raiz do projeto na inicialização do
servidor, caso não exista.

## Estrutura de pastas

```
app/
├── __init__.py
├── main.py          # instância do FastAPI, startup (init_db) e registro dos routers
├── database.py      # get_connection() e init_db() — acesso ao SQLite
├── models.py         # schemas Pydantic (request/response)
└── routes/
    └── ...            # routers da API, um módulo por recurso
requirements.txt
CLAUDE.md
docs/                  # roteiro de prompts do curso
specs/                 # spec de cada aula/feature
```

## Convenções do projeto

- **Datas**: sempre no formato ISO `YYYY-MM-DD`.
- **Valores monetários**: sempre com 2 casas decimais.
- **Campo `tipo`**: sempre `"entrada"` ou `"saida"` (sem outros valores).
- **Erros de validação**: HTTP 422, corpo `{ "erro": "<mensagem clara>" }` (não usar o formato
  padrão `{"detail": [...]}` do FastAPI/Pydantic).
- **`categoria_id` na transação**: opcional (nullable). Justificativa: transações das Aulas 1–2 já
  existem sem categoria e precisam continuar válidas; além disso, o usuário pode querer lançar um
  gasto rapidamente sem categorizar no ato.
- **Filtro `GET /transacoes?categoria=<inexistente>`**: retorna lista vazia com HTTP 200, nunca 404.
  Justificativa: `categoria` é um parâmetro de filtro sobre uma coleção, não um recurso acessado por
  ID — uma consulta que não encontra resultados é um caso válido, não um erro.
- **Banco de dados**: SQLite em arquivo local (`gastos.db`), criado na inicialização do servidor
  se não existir. Acesso via `sqlite3` (stdlib), sempre com **SQL parametrizado** — nunca
  concatenar valores diretamente na query.
- **Organização do código**: separado em módulos por responsabilidade — rotas (`app/routes/`),
  modelos/schemas (`app/models.py`), acesso a dados (`app/database.py`).
- **Git**: meta de um commit por aula/feature implementada, mas o commit nunca é automático —
  peça confirmação do usuário antes de criar cada commit, mesmo ao final de uma spec.

## Status da implementação

- [x] Aula 1 — Registrar e listar transações (`specs/aula-1-transacoes.md`)
- [x] Aula 2 — CRUD completo e validação (`specs/aula-2-crud-validacao.md`)
- [x] Aula 3 — Categorias (`specs/aula-3-categorias.md`)
- [x] Aula 4 — Saldo e resumo (`specs/aula-4-saldo-resumo.md`)
- [x] Aula 5 — Filtros e testes (`specs/aula-5-filtros-testes.md`)
- [ ] Aula 6 — Export e dashboard (`specs/aula-6-export-dashboard-deploy.md`)
