FROM apache/airflow:2.8.1
USER root
WORKDIR /opt/airflow/
RUN apt-get update \
    && apt-get install -y gcc \
    && apt-get install -y python3.9 \
    && apt-get install -y libpq-dev
USER airflow
RUN pip install psycopg2-binary==2.9.9 \
    && pip install boto3 \
    && pip install dbt-core==1.7.5 \
    && pip install dbt-postgres==1.7.5 \
    && pip install requests==2.31.0 \
    && pip install requests-oauthlib==1.3.1 \
    && pip install boto3==1.34.26 \
    && pip install botocore==1.34.26 \
    && pip install connexion[swagger-ui] # --no-cache-dir
ENV PYTHONPATH="${PYTHONPATH}:${AIRFLOW_PROJ_DIR}"
