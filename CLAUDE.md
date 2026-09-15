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

A API sobe em `http://127.0.0.1:8000`; documentação interativa em `/docs`; dashboard em `/`
(ou `/dashboard`).

O banco SQLite (`gastos.db`) é criado automaticamente na raiz do projeto na inicialização do
servidor, caso não exista.

## Deploy

### Variáveis de ambiente

- `PORT`: porta em que o Uvicorn escuta. Plataformas como Render, Railway e Heroku injetam
  essa variável automaticamente — normalmente não é preciso defini-la manualmente.
- `DB_PATH`: caminho do arquivo SQLite (default: `gastos.db` na raiz do projeto). Só precisa
  ser definida se o banco tiver que morar em outro lugar (ex.: um disco persistente).

Nenhuma credencial é usada pelo projeto (sem autenticação nesta fase), então não há segredo
para configurar.

### Passo a passo (padrão genérico, válido para Render/Railway/Heroku e afins)

1. **Suba o código para um repositório Git remoto** (GitHub, por exemplo) — a maioria dessas
   plataformas faz deploy a partir de um repo conectado.
2. **Crie um "Web Service"/app na plataforma** e aponte para o repositório.
3. **Build command:** `pip install -r requirements.txt`.
4. **Start command:** a maioria dessas plataformas detecta o `Procfile` da raiz
   automaticamente (`web: uvicorn app.main:app --host 0.0.0.0 --port $PORT`); se a plataforma
   não ler `Procfile`, cole esse mesmo comando manualmente no campo de start command.
5. **Env vars:** normalmente nenhuma é obrigatória (ver acima); defina `DB_PATH` só se for
   usar um disco persistente.
6. **Deploy** e abra a URL pública gerada — confira `/docs` (Swagger) e `/` (dashboard).

### Atenção: persistência do SQLite

O `gastos.db` é um arquivo local. Na maioria dos free tiers (Render, Railway, Heroku), o
sistema de arquivos é **efêmero**: a cada novo deploy (ou reinício do container) os dados
gravados localmente são perdidos. Para persistir de verdade entre deploys:

- Anexe um **disco/volume persistente** oferecido pela plataforma e aponte `DB_PATH` para um
  caminho dentro dele (ex.: `DB_PATH=/data/gastos.db`); ou
- Aceite que, num free tier sem disco persistente, o banco reseta a cada deploy — ok para
  fins de demonstração/portfólio deste projeto, mas não para uso real.

Trocar o SQLite por um banco externo gerenciado está fora de escopo desta aula (ver
`specs/aula-6-export-dashboard-deploy.md`, "Fora de escopo").

## Como rodar os testes

```bash
pytest
```

Cada teste usa um banco SQLite isolado em diretório temporário (fixture `client` em
`tests/conftest.py`, que sobrescreve `database.DB_PATH` por teste) — não toca no `gastos.db`
de desenvolvimento.

## Estrutura de pastas

```
app/
├── __init__.py
├── main.py          # instância do FastAPI, startup (init_db) e registro dos routers
├── database.py      # get_connection() e init_db() — acesso ao SQLite
├── models.py         # schemas Pydantic (request/response)
├── routes/
│   └── ...            # routers da API, um módulo por recurso
└── static/
    └── dashboard.html  # página HTML estática do dashboard (Chart.js via CDN)
tests/
├── conftest.py         # fixture `client` (TestClient com banco isolado por teste)
├── test_transacoes.py  # CRUD de transações (Aulas 1–2)
├── test_categorias.py  # categorias (Aula 3)
├── test_resumo.py       # saldo e resumo mensal (Aula 4)
├── test_filtros.py      # filtros de GET /transacoes (Aula 5)
├── test_export.py       # GET /export.csv (Aula 6)
└── test_dashboard.py    # GET / e GET /dashboard (Aula 6)
requirements.txt
Procfile
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
- [x] Aula 6 — Export e dashboard (`specs/aula-6-export-dashboard-deploy.md`)
