# SmartTasks — Rastreabilidade e verificação

## Matriz de requisitos funcionais
| US | RF | Critério resumido | Teste automatizado |
| --- | --- | --- | --- |
| US-01, US-05 | RF-01 | Lista vazia e tarefas existentes | test_list_empty; test_create_and_list; test_multiple_tasks |
| US-02 | RF-02 | Título obrigatório, descrição opcional, estado Aberta | test_create_and_list; test_create_with_description; test_invalid_title |
| US-03 | RF-03 | Concluir e refletir estado | test_complete_and_reopen; test_missing_task |
| US-04 | RF-04 | Reabrir e refletir estado | test_complete_and_reopen; test_missing_task |
| US-01 a US-06 | RF-05 | API HTTP com respostas e erros apropriados | test_list_empty; test_create_and_list; test_complete_and_reopen; test_invalid_title; test_missing_task |
| US-06 | RF-06 | GET /health devolve HTTP 200 | test_health |

## Requisitos não funcionais
| RNF | Evidência / verificação | Estado |
| --- | --- | --- |
| RNF-01 | Abrir http://localhost:8080 após Docker Compose | Manual, pendente |
| RNF-02 | docker compose config; build; up; confirmar um serviço e 127.0.0.1:8080:8000 | Manual, pendente |
| RNF-03 | test_html_interface; experimentar formulário e botões no browser | Parcial: teste automatizado de HTML; browser pendente |
| RNF-04 | Inspeção de app/main.py, app/models.py e app/store.py | Inspeção estrutural |
| RNF-05 | test_memory_isolated_between_clients; reiniciar container e confirmar lista vazia | Simulação automatizada; reinício real pendente |
| RNF-06 | Docstrings com US/RF/RNF; revisão dos testes e README | Inspeção documental |

## Execução e limitações
A suite local foi executada com `python -m pytest -q`: **13 testes passaram**. Este resultado não comprova a execução real do Docker ou a interação num browser. A prova de reinício em teste substitui o armazenamento, simulando um processo novo; não substitui a verificação manual de reinício de container.

## Validação manual sugerida
1. `docker compose config` e `docker compose build`.
2. `docker compose up -d`; abrir http://localhost:8080 e criar, listar, concluir e reabrir.
3. `curl http://localhost:8080/health` e verificar HTTP 200.
4. Criar uma tarefa, reiniciar o container e verificar que a lista regressa a vazia.
5. `docker compose down`.

**Fora do âmbito:** PostgreSQL, volumes, filas, login, notificações, CI/CD e serviços pagos.
