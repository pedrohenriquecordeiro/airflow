
# Entendendo Sensor, Operator e Hook no Apache Airflow

O Apache Airflow é uma poderosa plataforma de orquestração de dados que nos ajuda a criar, agendar e monitorar fluxos de trabalho. Dentro desse ecossistema, três conceitos fundamentais são **Sensors**, **Operators** e **Hooks**. Vamos entender o que são e como utilizá-los, com exemplos práticos!

---

## 1. Sensors: Espera por Eventos  

Um **Sensor** é um tipo especial de *Operator* que “espera” por um evento específico antes de prosseguir com o fluxo. Ele verifica continuamente se determinada condição foi atendida, como a chegada de um arquivo ou a conclusão de uma tarefa externa.  

### Exemplo prático de Sensor:  

Imagine que você tem uma pipeline que depende da chegada de um arquivo em um bucket S3.

```python
from airflow.providers.amazon.aws.sensors.s3 import S3KeySensor

wait_for_file = S3KeySensor(
    task_id='wait_for_file',
    bucket_name='meu-bucket',
    bucket_key='dados/arquivo.csv',
    aws_conn_id='my_s3_conn',
    poke_interval=60  # verifica a cada 60 segundos
)
```

Esse Sensor só permitirá que o fluxo continue quando o arquivo especificado for encontrado.

## 2. Operators: Executa Tarefas

Operators são responsáveis por realizar tarefas específicas, como rodar uma query SQL, executar um script Python ou até mesmo interagir com APIs externas. Eles são os blocos de construção principais de qualquer DAG no Airflow.

### Exemplo prático de Operator:

Suponha que você precise executar uma query em um banco de dados para carregar novos dados.

```python
from airflow.providers.postgres.operators.postgres import PostgresOperator

run_query = PostgresOperator(
    task_id='run_query',
    postgres_conn_id='my_postgres_conn',
    sql='INSERT INTO vendas (data, valor) SELECT * FROM staging_vendas;'
)
```

Este Operator se conecta ao banco Postgres e executa a query SQL definida.

## 3. Hooks: Conecta a Sistemas Externos

Hooks são interfaces que facilitam a conexão com sistemas externos, como bancos de dados, APIs ou serviços de nuvem. Eles geralmente são usados dentro de Operators para executar ações específicas em sistemas externos.

### Exemplo prático de Hook:

Digamos que você queira escrever dados diretamente em um bucket S3 usando Python.

```python
from airflow.providers.amazon.aws.hooks.s3 import S3Hook

def upload_to_s3():
    s3_hook = S3Hook(aws_conn_id='my_s3_conn')
    s3_hook.load_string(
        string_data='Hello, Airflow!',
        key='uploads/hello.txt',
        bucket_name='nome-bucket'
    )
```

Aqui, o Hook facilita a autenticação e a interação com o S3 para realizar o upload do arquivo.

## Conclusão

Com Sensors, Operators e Hooks, o Airflow oferece a flexibilidade de monitorar eventos, executar tarefas e se conectar a uma variedade de sistemas externos. Eles são peças fundamentais para criar pipelines robustos e escaláveis.
