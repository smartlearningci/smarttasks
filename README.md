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
```bash
docker compose build
docker compose up -d
```
Abrir **http://localhost:8080**. Criar uma tarefa, concluir e reabrir. O Compose liga apenas a `127.0.0.1:8080`.

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

## Organização e responsabilidades
- `docs/`: contexto, User Stories, requisitos, arquitetura e rastreabilidade.
- `app/main.py`: rotas HTTP; `app/models.py`: validação; `app/store.py`: dados em memória.
- `app/static/index.html`: interface web e chamadas à API.
- `tests/test_api.py`: testes automatizados.
- `Dockerfile`, `compose.yaml`, `.dockerignore`: construção e execução.

## Limites
Sem login, PostgreSQL, persistência, notificações, filas, serviços externos ou pagos. A demonstração de Docker e browser deve ser validada no computador dos formandos.
