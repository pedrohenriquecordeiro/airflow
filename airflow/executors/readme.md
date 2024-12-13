# **Tipos de Executores no Apache Airflow**

Se você já trabalhou com Apache Airflow, sabe que a escolha do executor certo faz toda a diferença no desempenho e escalabilidade dos seus pipelines de dados. Neste post, vamos explorar os principais *executores* disponíveis, suas diferenças, os cenários ideais para cada um e como configurá-los usando **Docker Compose** e **Helm**.

---

## **1. Sequential Executor**

**O que é?**  
O *Sequential Executor* é o mais básico. Ele executa uma tarefa de cada vez, de forma sequencial, usando um único processo.

**Quando usar?**  
Ótimo para testes locais ou para ambientes de desenvolvimento simples, onde você não precisa de paralelismo.

**Configuração no Docker Compose:**  
```yaml
executor: SequentialExecutor
```

**Configuração no Helm:**  
```yaml
executor: SequentialExecutor
```

---

## **2. Local Executor**

**O que é?**  
Permite a execução paralela de várias tarefas em uma única máquina, aproveitando múltiplos processos.

**Quando usar?**  
Ideal para ambientes de desenvolvimento ou produções menores que precisam de um pouco mais de performance sem sair de um único nó.

**Configuração no Docker Compose:**  
```yaml
executor: LocalExecutor
```

**Configuração no Helm:**  
```yaml
executor: LocalExecutor
```

---

## **3. Celery Executor**

**O que é?**  
Distribui tarefas entre múltiplos *workers* usando uma fila de mensagens, como **Redis** ou **RabbitMQ**. Altamente escalável e perfeito para grandes cargas.

**Quando usar?**  
Se você está rodando o Airflow em produção e precisa lidar com um alto volume de tarefas, essa é a escolha certa.

**Configuração no Docker Compose:**  
```yaml
executor: CeleryExecutor
```

Adicione também um serviço de fila, como Redis:  
```yaml
services:
  redis:
    image: redis
    ports:
      - "6379:6379"
```

**Configuração no Helm:**  
```yaml
executor: CeleryExecutor
redis:
  enabled: true
```

---

## **4. Kubernetes Executor**

**O que é?**  
Cada tarefa roda em um pod Kubernetes isolado, garantindo máximo isolamento e escalabilidade.

**Quando usar?**  
Perfeito para quem já está em um ambiente Kubernetes e precisa de flexibilidade e escalabilidade máximas.

**Configuração no Helm:**  
```yaml
executor: KubernetesExecutor
```

---
