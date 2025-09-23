
from time import sleep
import pandas as pd
import numpy as np
from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from .postgres.sink_table import initialise_domains_table

from ..check.domains.base import Domain
from ..check.domains.domain_info import DomainStatus
from ..check.availability import check_domain

class Summary:
    def __init__(self):
        self._statuses = {
            DomainStatus.AVAILABLE:0,
            DomainStatus.UNKNOWN:0,
            DomainStatus.ERROR:0,
            DomainStatus.REGISTERED:0
        }

    def __str__(self):
        lines = ["Summary of domain checks:"]
        for status, count in self._statuses.items():
            lines.append(f"  {status.name:<10} : {count}")
        return "\n".join(lines)

    def add_status(self, status:DomainStatus):
        self._statuses[status] += 1

class AutoCheck:
    def __init__(self):
        self._source_path:str = None
        self._source_name:str = None
        self._sink_path:str = None
        self._sink_name:str = None

        self._pg_engine = None
        self._pg_records_table:str = None
        self._dictionary_tables:dict = {}

    def init_postgres(
            self,
            user:str,
            password:str,
            host:str="localhost",
            port:int=5432,
            database:str = "domain_checker",
            echo:bool=False
        ):
        url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        self._pg_engine = create_engine(url, echo=echo, future=True)

    def load_file_to_postgres_dictionary(
            self,
            file_path:str,
            name_col:str,
            frequency_col:str,
            dictionary_table_name:str,
            name_prefix:str="",
            tld_suffix:str="",
            overwrite_dictionary_table:bool=False
    ):
        print(f"Initialising table {dictionary_table_name}")
        DomainsTable = initialise_domains_table(dictionary_table_name)
        if overwrite_dictionary_table:
            print("Overwriting exising table")
            DomainsTable.__table__.drop(self._pg_engine, checkfirst=True)
        DomainsTable.__table__.create(self._pg_engine, checkfirst=True)
        self._dictionary_tables[dictionary_table_name] = DomainsTable

        df = self._load_clean_csv(
            file_path, 
            name_col, 
            frequency_col,
            prefix=name_prefix,
            tld_suffix=tld_suffix)
        print("Generating records for database")
        records = [
            DomainsTable(
                domain=row[name_col], 
                frequency=row[frequency_col]
                ) 
            for _, row in df.iterrows()
            ]
        
        print("Loading local dictionary data into database")
        with Session(self._pg_engine) as session:
            session.add_all(records)
            session.commit()
            print("Records were committed to db")

    @staticmethod
    def _load_clean_csv(
        path:str,
        name_col:str,
        freq_col:str,
        prefix:str,
        tld_suffix:str
    ) -> pd.DataFrame:
        print("Converting CSV to DataFrame")
        df = pd.read_csv(path)
        print("Cleaning data")
        df = df.filter(items=[name_col, freq_col])
        df[name_col] = df[name_col].astype("string").str.strip()
        df[name_col] = df[name_col].replace({"":np.nan})
        df[name_col] = prefix + df[name_col] + tld_suffix
        df[freq_col] = pd.to_numeric(df[freq_col], errors="coerce")
        df = df.dropna(subset=[name_col, freq_col])
        df = df.sort_values(freq_col, ascending=False)\
                .drop_duplicates(subset=[name_col], keep="first")
        print("Returning cleaned DataFrame")
        return df
    
    def _get_table(
            self,
            table_name:str):
        if table_name not in self._dictionary_tables:
            table = initialise_domains_table(table_name)
            self._dictionary_tables[table_name] = table
            return table
        return self._dictionary_tables[table_name]

    def check_top_n_names(self, 
                          dictionary_name:str, 
                          num_records:int=5, 
                          check_interval_s:float=5,
                          print_summary=True,
                          recheck_unknown:bool=True):
        print(f"Initialising connection to table {dictionary_name}")
        DomainsTable = self._get_table(dictionary_name)
        stmt = (
            select(DomainsTable)
            .where(DomainsTable.was_checked.is_(False))
            .order_by(DomainsTable.frequency.desc())
            .limit(num_records)
        )
        print(f"Querying top {num_records} to check")
        summary = Summary()
        with Session(self._pg_engine) as session:
            result = session.scalars(stmt).all()
            total = len(result)
            for i, row in enumerate(result):
                print(f"Checking record {i+1}/{total}", end="\r", flush=True)

                domain = check_domain(row.domain)
                row.was_checked=True
                row.status = domain.domain_info().status.name
                row.domain_punycode = domain.punycode_string
                row.domain_ascii = domain.ascii_string
                row.error_message = domain.error_message
                session.commit()
                summary.add_status(domain.domain_info().status)
                if check_interval_s:
                    sleep(check_interval_s)
        print("Finished checking domain avaiability")
        if print_summary:
            print(summary)
    



