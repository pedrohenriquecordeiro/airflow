# **DAG no Apache Airflow**

Se você já trabalha com o Apache Airflow, sabe que tudo começa pelas **DAGs (Directed Acyclic Graphs)**. Elas são a base da ferramenta e ajudam a organizar o que será feito, quando e em que ordem. Vamos entender o que é uma DAG, os principais parâmetros que você pode configurar, como os decorators se relacionam com a criação de DAGs e, claro, conferir um exemplo prático de código.



## **O que é uma DAG?**

Uma DAG nada mais é do que um gráfico que organiza tarefas dentro de um fluxo de trabalho. Ela define as dependências entre as tarefas e garante que elas sejam executadas na ordem certa. O "Acyclic" do nome significa que não pode haver ciclos, ou seja, uma tarefa não pode depender de si mesma.

<img src="workflow-group-dags.png" alt="dag" width="75%">

Na arquitetura do Airflow:
- O **Scheduler** lê as DAGs e decide quais tarefas precisam ser executadas.
- O **Database** armazena informações como dependências, histórico e status das execuções.
- O **Web Server** exibe as DAGs, mostrando o que está rodando e permitindo interação com eles.



## **Principais Parâmetros de Configuração de um DAG**

Ao criar uma DAG, você pode configurar vários parâmetros importantes. Aqui estão os principais:

1. **`dag_id`**  
   - Nome único para identificar a DAG.

2. **`schedule_interval`**  
   - Define quando a DAG será executada.
   - Exemplos: `"@daily"` (uma vez por dia), `"@hourly"` (uma vez por hora), ou expressões cron como `"0 12 * * *"`.

3. **`start_date`**  
   - Data de início da DAG. Ela só começará a rodar após essa data.

4. **`verbose`**  
   - Define se a DAG terá mais detalhes no log. Geralmente é usado para depuração.

5. **`tags`**  
   - Lista de palavras-chave que ajudam a categorizar as DAGs.
   - Exemplo: `tags=["data-science", "treinamento"]`.

6. **`orientation`**  
   - Controla o layout visual da DAG na interface.
   - Exemplo: `"LR"` (da esquerda para a direita) ou `"TB"` (de cima para baixo).

7. **`catchup`**  
   - Define se a Airflow deve "compensar" execuções pendentes desde o `start_date`.
   - Por padrão, é `True`.

8. **`max_active_runs`**  
   - É usado para controlar o número máximo de execuções paralelas de um fluxo de trabalho.



### **O Que é um Decorator?**

No Python, um **decorator** é uma função que modifica o comportamento de outra função ou método. No Airflow, decorators simplificam a criação de DAGs e tarefas. Por exemplo, ao usar o `@dag` decorator, você pode transformar uma função Python em uma DAG, o que torna o código mais limpo e intuitivo.



### **Exemplo de Código**

Aqui está um exemplo simples de uma DAG no Airflow, usando operadores Bash e Python.

```python
import json
from airflow import DAG                              # Importa a classe DAG para criar o fluxo de trabalho
from airflow.decorators import dag, task             # Importa o decorator @dag para simplificar a criação do DAG
from airflow.operators.bash import BashOperator      # Operador para executar comandos Bash
from airflow.operators.python import PythonOperator  # Operador para usar funções Python
from datetime import datetime, timedelta             # Gerencia datas e intervalos de tempo

# Configura os argumentos padrão para todas as tarefas do DAG
default_args = {
    "owner": "data_team",                   # Nome do responsável ou time que mantém o DAG
    "retries": 3,                           # Número de vezes que a tarefa será reexecutada em caso de falha
    "retry_delay": timedelta(minutes=10),   # Intervalo entre tentativas de reexecução
    "email_on_failure": True,               # Envia e-mail em caso de falha
    "email_on_retry": True,                 # Envia e-mail em caso de reexecução
    "email": ["data.team@example.com"],     # Lista de destinatários para alertas
}

# Criação do DAG com o decorator
@dag(
    dag_id            = "daily_data_pipeline",  # Nome único do DAG
    description       = "Pipeline diário de ingestão e transformação de dados",
    schedule_interval = "@daily",                     # Frequência de execução (uma vez por dia)
    start_date        = datetime(2024, 11, 1),        # Data inicial para execução
    catchup           = False,                        # Não compensa execuções pendentes
    tags              = ["data-engineering", "ETL"],  # Categoriza o DAG
    orientation       = "TB",                         # Layout da visualização (de cima para baixo)
    default_args      = default_args
)
def data_pipeline():

    # Tarefa Bash: Baixa dados de uma API pública
    download_data = BashOperator(
        task_id="baixar_dados",  # Nome da tarefa
        bash_command="curl -o /tmp/data.json https://api.exemplo.com/dados",  # Comando para baixar os dados
    )

    # Tarefa Python: Processa os dados baixados
    def process_data():
        with open("/tmp/data.json", "r") as file:
            data = json.load(file)
            print(f"Processando {len(data)} registros!")

    process_task = PythonOperator(
        task_id="processar_dados",  # Nome da tarefa
        python_callable=process_data,  # Função Python que será executada
    )

    # Tarefa Bash: Move os dados processados para uma pasta de backup
    backup_data = BashOperator(
        task_id="backup_dados",  # Nome da tarefa
        bash_command="mv /tmp/data.json /tmp/backup/data_{{ ds }}.json",  # Comando para mover o arquivo para backup
    )

    # Define a ordem das tarefas: download_data -> process_task -> backup_data
    download_data >> process_task >> backup_data

# Instancia o DAG
dag = data_pipeline()
```



## **Como as DAGs se Integram com o Airflow**

1. O código da DAG é salvo na pasta de DAGs, que o **Scheduler** monitora.
2. O **Scheduler** lê a DAG e organiza as tarefas com base no intervalo configurado.
3. As tarefas são enviadas para a fila e executadas pelos **Workers**.
4. O **Web Server** mostra o status da DAG e das tarefas em tempo real.

