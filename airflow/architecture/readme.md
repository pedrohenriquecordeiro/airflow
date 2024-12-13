### Arquitetura do Apache Airflow

O **Apache Airflow** conecta vários componentes que trabalham juntos para orquestrar, executar e monitorar fluxos de trabalho de forma eficiente. Aqui vai uma explicação de como tudo isso acontece.

<img src="airflow.JPG" alt="Arquitetura Airflow" width="50%">

Tudo começa com o **Web Server**, onde os usuários interagem com o Airflow. É ali que você gerencia e monitora os DAGs (os fluxos de trabalho) e suas tarefas. Dá pra iniciar ou pausar workflows, consultar logs e acompanhar o status de cada execução. Em segundo plano, o Web Server puxa informações do **Database**, que guarda tudo: DAGs, tarefas, logs e histórico de execuções.

O **Scheduler** é o cérebro do Airflow. Ele decide quais tarefas precisam ser executadas e quando, lendo os DAGs no Database e enviando as tarefas para uma **fila de mensagens** (Queue). Aqui entra o **Executor**, que distribui as tarefas para os **Workers** — os responsáveis por botar a mão na massa e executar o que foi programado.

A **Queue**, normalmente operando com Redis ou RabbitMQ, garante que as tarefas sejam processadas na ordem certa. Os **Workers** pegam essas tarefas, executam o que for necessário (como rodar scripts ou consultas SQL) e depois atualizam o **Database** com o status da execução — seja sucesso ou falha.

No fim das contas, tudo isso se integra perfeitamente: os usuários gerenciam os DAGs pelo Web Server, o Scheduler cuida de organizar e agendar as tarefas, e os Workers executam o que foi pedido. Essa estrutura modular e escalável permite que você use o Airflow tanto para projetos simples quanto para pipelines massivos.

### Docker Compose 

Aqui está um exemplo de um arquivo `docker-compose.yaml` que reflete a arquitetura do Airflow.

```yaml
version: '3.8'

services:
  # Web Server: Interface gráfica do Airflow
  webserver:
    image: apache/airflow:2.6.1
    container_name: airflow_webserver
    depends_on:
      - scheduler
      - postgres
    ports:
      - "8080:8080"  # Porta para acessar a interface do Airflow
    environment:
      - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
      - AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
      - AIRFLOW__CELERY__RESULT_BACKEND=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
    command: >
      bash -c "airflow db init &&
               airflow webserver"

  # Scheduler: Organiza e agenda as tarefas dos DAGs
  scheduler:
    image: apache/airflow:2.6.1
    container_name: airflow_scheduler
    depends_on:
      - postgres
      - redis
    environment:
      - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
      - AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
      - AIRFLOW__CELERY__RESULT_BACKEND=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
    command: airflow scheduler

  # Redis: Fila de mensagens usada pelo Executor
  redis:
    image: redis:6.2
    container_name: airflow_redis
    ports:
      - "6379:6379"  # Porta padrão do Redis

  # Database: Armazena metadados e logs de execução
  postgres:
    image: postgres:13
    container_name: airflow_postgres
    environment:
      POSTGRES_USER: airflow
      POSTGRES_PASSWORD: airflow
      POSTGRES_DB: airflow
    ports:
      - "5432:5432"  # Porta padrão do PostgreSQL

  # Workers: Executam as tarefas enviadas pelo Executor
  worker:
    image: apache/airflow:2.6.1
    container_name: airflow_worker
    depends_on:
      - redis
      - postgres
    environment:
      - AIRFLOW__CORE__EXECUTOR=CeleryExecutor
      - AIRFLOW__CORE__SQL_ALCHEMY_CONN=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
      - AIRFLOW__CELERY__BROKER_URL=redis://redis:6379/0
      - AIRFLOW__CELERY__RESULT_BACKEND=postgresql+psycopg2://airflow:airflow@postgres:5432/airflow
    command: airflow celery worker

volumes:
  # Volume para persistir os DAGs e logs do Airflow
  airflow_data:
```

Esse `docker-compose.yaml` é um exemplo prático que implementa a arquitetura do Airflow, pronto para ser usado e ajustado conforme a necessidade.
