from airflow import DAG
from airflow.operators.bash import BashOperator
from datetime import datetime, timedelta
from airflow.utils.dates import days_ago
import os

'''
get current working directory and use in the bash operator
'''
cwd = os.getcwd()

args={
    'retries': 0,
    'max_active_runs': 1
}

dag = DAG(
    'get_spotify_recently_played_data_test',
    description='Get Spotify data and export to a local file',
    schedule_interval=timedelta(minutes=20),
    default_args=args,
    catchup=False,
    start_date=days_ago(1),
)

t1 = BashOperator(
    task_id='print_date',
    bash_command='date',
    dag=dag,
)

t2 = BashOperator(
    task_id='sleep',
    depends_on_past=True,
    bash_command='sleep 3',
    dag=dag,
)

t3 = BashOperator(
    task_id='run_spotify_test_script',
    start_date=days_ago(1),
    depends_on_past=True,
    bash_command='python3 ' + cwd + '/scripts/get_spotify_recently_played_scratch.py airflow',
    dag=dag,
)

t4 = BashOperator(
    task_id='end',
    start_date=days_ago(1),
    depends_on_past=True,
    bash_command='echo \'end\'',
    dag=dag,
)

t1 >> t2
t2 >> t3
t3 >> t4