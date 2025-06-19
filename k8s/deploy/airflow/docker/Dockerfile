FROM apache/airflow:2.10.5-python3.12

# install your pip packages
RUN pip install --no-cache-dir \
    apache-airflow-providers-apache-kafka==1.8.0 \
    apache-airflow-providers-cncf-kubernetes==10.4.2 \
    apache-airflow-providers-redis==4.0.2 \
    redis==5.2.1

ENV AIRFLOW__CORE__TEST_CONNECTION=Enabled
