import os
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator

from datetime import datetime,  timedelta

def check_domains(
        pguser:str,
        pgpass:str,
        pghost:str,
        pgport:int,
        pgdb:str,
        dictname:str,
        numrecords:int,
        interval:float,
        print_summary:bool
):
    from domains.domain_availability_checker.auto_check.check import AutoCheck

    pgport = int(pgport)

    ac = AutoCheck()
    ac.init_postgres(
        user=pguser,
        password=pgpass,
        host=pghost,
        port=pgport,
        database=pgdb
    )
    ac.check_top_n_names(
        dictionary_name=dictname,
        num_records=numrecords,
        check_interval_s=interval,
        print_summary=print_summary
    )


default_dag_args = {
    "owner":"pomeran",
    "retries":5,
    "retry_delay":timedelta(minutes=30)
}


with DAG(
    dag_id="dag_check_domains_pl_dict_v07",
    default_args=default_dag_args,
    start_date=datetime(2025,9,22),
    schedule="@hourly",
    catchup=False,
    params={}
) as dag:
    check_domains_availability = PythonVirtualenvOperator(
        task_id="check_domains_availability",
        python_callable=check_domains,
        requirements=[
            "pandas==2.3.2",
            "requests==2.32.5",
            "sqlalchemy==2.0.43",
            "psycopg2-binary==2.9.10"
        ],
        system_site_packages=False,
        op_kwargs={
            "pguser": "{{ conn['conn-pg-domains-db'].login}}",
            "pgpass": "{{ conn['conn-pg-domains-db'].password}}",
            "pghost": "{{ conn['conn-pg-domains-db'].host}}",
            "pgport": "{{ conn['conn-pg-domains-db'].port}}",
            "pgdb": "{{ conn['conn-pg-domains-db'].schema}}",
            "dictname":"words_tld_pl",
            "numrecords":5,
            "interval":300,
            "print_summary":True,

        }
    )