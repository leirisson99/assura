# Assura

Plataforma de gestão e auditoria de SGI. Princípios do projeto em [contitutions.md](contitutions.md).

## Requisitos

- Python 3.14
- Node.js 24
- Docker

## Ambiente de desenvolvimento

### Banco de dados

```sh
docker compose up -d
```

PostgreSQL 17 em `localhost:5433` (usuário, senha e banco: `assura`).

### Backend (FastAPI)

```sh
cd backend
python -m venv .venv
.venv\Scripts\activate          # Linux/macOS: source .venv/bin/activate
pip install -e ".[dev]"
copy .env.example .env          # Linux/macOS: cp .env.example .env
alembic upgrade head
uvicorn assura.main:app --reload
```

API em http://localhost:8000 (documentação em `/docs`).

Qualidade (obrigatória antes de cada entrega):

```sh
ruff format .
ruff check .
mypy
pytest
```

Os testes de integração usam o banco `assura_teste` no mesmo PostgreSQL do `docker compose`. O `pytest` cria esse banco e aplica as migrações automaticamente; cada teste roda numa transação desfeita no fim. Para usar outro banco, defina `ASSURA_URL_BANCO_DE_DADOS_DE_TESTE`.

### Frontend (Next.js)

```sh
cd frontend
npm install
npm run dev
```

Aplicação em http://localhost:3000.
