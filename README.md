# SmartTasks — MVP pedagógico

Aplicação web da TaskFlow para criar, listar, concluir e reabrir tarefas. Os dados são guardados **em memória** e perdem-se quando o processo reinicia.

## Requisitos
Git e Docker com Docker Compose.

## Clonar
```bash
git clone https://github.com/smartlearningci/smarttasks.git
cd smarttasks
```

## Construir e iniciar

### 1. Preparar a configuração local

```bash
cp .env.example .env
```

Editar o ficheiro `.env` e substituir `SUBSTITUIR_LOCALMENTE` por uma password local. Não publicar `.env` no GitHub. A variável `POSTGRES_PASSWORD` é necessária para iniciar PostgreSQL.

### 2. Construir e iniciar os dois serviços

```bash
docker compose build
docker compose up -d
```
### 3. Verificar os serviços

```bash
docker compose ps
docker compose exec db pg_isready -U smarttasks -d smarttasks
```

Abrir **http://localhost:8080**. Criar uma tarefa, concluir e reabrir. O Compose liga apenas a `127.0.0.1:8080`.

O serviço `db` utiliza PostgreSQL 17, a base `smarttasks` e o utilizador `smarttasks`. Ambos os serviços partilham a rede padrão do Compose: `db` é o hostname interno da base de dados. **A porta 5432 não está publicada no host.**

**Importante:** a aplicação ainda guarda as tarefas em memória; não estabelece ligação ao PostgreSQL. O volume nomeado `postgres_data` conserva os dados da base de dados entre reinícios e recriações dos containers, mas não as tarefas da aplicação.

## Verificar a API
```bash
curl http://localhost:8080/health
curl http://localhost:8080/api/tasks
```
Documentação automática FastAPI: http://localhost:8080/docs.

## Testes automatizados
```bash
docker compose run --rm --no-deps smarttasks python -m pytest -q
```
Os testes em `tests/test_api.py` identificam **US, RF/RNF, objetivo e resultado esperado**. Consultar `docs/04_rastreabilidade_e_testes.md` para a matriz e os testes manuais pendentes.

## Parar
```bash
docker compose down
```

Não executar `docker compose down -v` se pretender conservar os dados do volume PostgreSQL.

## Organização e responsabilidades
- `docs/`: contexto, User Stories, requisitos, arquitetura e rastreabilidade.
- `app/main.py`: rotas HTTP; `app/models.py`: validação; `app/store.py`: dados em memória.
- `app/static/index.html`: interface web e chamadas à API.
- `tests/test_api.py`: testes automatizados.
- `Dockerfile`, `compose.yaml`, `.dockerignore`: construção e execução.

## Limites
Sem login, persistência de tarefas, notificações, filas ou serviços externos pagos. PostgreSQL está disponível apenas como infraestrutura, **sem integração com a aplicação**. A demonstração de Docker e browser deve ser validada no computador dos formandos.
