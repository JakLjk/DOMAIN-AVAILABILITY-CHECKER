
import socket
import requests
import pandas as pd
from sqlalchemy import create_engine

from domain_availability_checker.domains.base import DomainBase
from domain_availability_checker.domains.pl import DomainPL
from domain_availability_checker.domains.functions import domain_to_punycode, domain_tld

DOMAIN_MAPPINGS = {
    "pl": DomainPL
}

class Availibility:
    def __init__(self):
        self._source_path:str = None
        self._source_name:str = None
        self._sink_records_table:str = None
        self._pg_engine = None

    def init_postgres(
            self,
            user:str,
            password:str,
            host:str="localhost",
            port:int=5432,
            database:str = "domain_checker",
            sink_table:str = "checked_domains",
            echo:bool=False
        ):
        self._sink_records_table = sink_table
        url = f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}"
        self._pg_engine = create_engine(url, echo=echo, future=True)
    
    def load_source_csv(
            self,
            path:str,
            domain_col_name:str,
            frequency_col_name:str
        ):
        pass


    def _normalise_frequency_col(self):
        pass

    
    def check_top_n_names_from_csv(
            check_n_names:int=10,
            tld_extension:str="pl",
            name_prefix:str=None,
            name_suffix:str=None,
            by_frequency:bool=True,
            ignore_already_checked:bool=True,
            check_if_registered_to_expired:bool=True,
            save_result_to_pg:bool=True,
            print_result:bool=True,
            check_interval_s:float=15.0
    ):
        pass

    def check_name(
            name:str,
            tld_extension:str="pl",
            save_result_to_pg:bool=True,
            print_result:bool=True
    ):
        pass
        
    def _check_name_from_source(
            self,
            name,
            tld_extension,
    ) -> DomainBase:
        domain_name = name + "." + tld_extension
        domain_name = domain_to_punycode(domain_name)
        domain = DOMAIN_MAPPINGS[tld_extension.trim().lower()]
        domain = domain()
        domain.get(domain_name)
        return domain
    
    
    def top_n_avaiable_domains_by_freq(
            top_n:int=10,
            offset_n:int=0,
            name_length_min:int=0,
            name_length_max:int=255
    ):
        pass



