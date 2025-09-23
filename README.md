# Domain Availability Checker

![Python](https://img.shields.io/badge/python-3.11%2B-blue)
![License](https://img.shields.io/badge/license-MIT-green)
![Packaging](https://img.shields.io/badge/packaging-Poetry-5C5C5C)

A lightweight Python toolkit for **domain availability checking** using raw **WHOIS over TCP (port 43)** with optional **dictionary loading** and **batch checking** persisted in PostgreSQL. Designed to be packaged with **Poetry** and embedded into **Apache Airflow** DAGs or other pipelines.


---

## Table of contents
- [Features](#features)
- [Install](#install)
- [Configuration](#configuration)
- [CLI usage](#cli-usage)
  - [`status`: one-off check](#status-one-off-check)
  - [`status_job`: load & batch-check](#status_job-load--batch-check)
- [Python API](#python-api)
- [Dictionary & database](#dictionary--database)
- [WHOIS behaviour](#whois-behaviour)
- [Airflow integration](#airflow-integration)
- [License](#license)

---

## Features
- **Raw WHOIS over TCP/43** (no third‑party whois libs) with per‑TLD parser classes.
- **Punycode/ASCII handling** helpers for internationalized domains (IDN) (e.g. `się.pl → sie.pl` or `xn--si-gna.pl`).
- **CSV → PostgreSQL** loader to create/update a **dictionary** of candidate domains with frequency/rank.
- **Batch checker** that selects top‑N not‑checked names, performs WHOIS queries with an adjustable interval, and persists results.
- Clean, composable **Python API** + **CLI** entry points for automation.

> Current mapping includes `.pl` via `DomainPL`. Extendable to other TLDs by subclassing `Domain`.

---


## Install

### Using Poetry (recommended)
```bash
poetry install
```

> System deps: for PostgreSQL features install `psycopg2` (or `psycopg2-binary`) and the `libpq` headers on Linux.

---

## Configuration

CLI commands read PostgreSQL settings from **environment variables** (loaded via `.env` if present):

- `PG_USER`
- `PG_PASSWORD`
- `PG_HOST` (default: `localhost`)
- `PG_PORT` (default: `5432`)
- `PG_DATABASE` (default: `domain_checker`)

Example `.env`:
```env
PG_USER=postgres
PG_PASSWORD=secret
PG_HOST=127.0.0.1
PG_PORT=5432
PG_DATABASE=domain_checker
```

---

## CLI usage

### `status`: one-off check
`status.py` prints the resolved **status name** for a single domain.

```bash
python -m domain_availability_checker.status --domain "example.pl"
# OUTPUT: AVAILABLE | REGISTERED | UNKNOWN | ERROR
```

### `status_job`: load & batch-check
`status_job.py` provides two subcommands: `load` and `check`.

#### 1) Load a CSV dictionary into PostgreSQL
```bash
python -m domain_availability_checker.status_job load \
  --dictname polish_dict \
  --path data/domains.csv \
  --namecol name \
  --freqcol freq \
  --tld_suffix ".pl" \
  --prefix "" \
  --overwrite_dict
```
- `--namecol` / `--freqcol` point to CSV columns.
- `--prefix` and `--tld_suffix` let you construct full domain strings from a stem (e.g., `brand` + `.pl`).

#### 2) Batch‑check top‑N by frequency
```bash
python -m domain_availability_checker.status_job check \
  --dictname polish_dict \
  --numchecks 50 \
  --interval 2.0 \
  --print-summary
```
- Picks highest‑frequency rows where `was_checked = false`.
- Sleeps `--interval` seconds between WHOIS queries.
- Prints a status summary when done.


---

## Python API

### Quick example
```python
from domain_availability_checker.check.availability import check_domain

info = check_domain("się.pl").domain_info()
print(info.status.name)  # AVAILABLE | REGISTERED | UNKNOWN | ERROR
```

### Forcing ASCII or Punycode mode
`check_domain()` uses the TLD router and default mode. To force a specific mode (e.g., punycode), instantiate the concrete class:
```python
from domain_availability_checker.check.domains.pl import DomainPL

pl = DomainPL().get("się.pl", mode="punycode")
print(pl.punycode_string)  # xn--si-gna.pl
print(pl.domain_info().status.name)
```

---

## Dictionary & database

The AutoCheck pipeline creates/uses a **dictionary table** (name supplied via `--dictname`). The exact SQLAlchemy model is produced by `initialise_domains_table(name)`, but typical fields include:

| Column           | Type      | Notes                          |
|------------------|-----------|---------------------------------|
| `id`             | int, PK   | Auto‑increment                  |
| `domain`         | text      | Candidate domain (unique)       |
| `frequency`      | numeric   | Rank/score from CSV             |
| `was_checked`    | boolean   | Default `false`                 |
| `status`         | text      | `AVAILABLE/REGISTERED/UNKNOWN/ERROR` |
| `domain_punycode`| text      | Cached punycode form            |
| `domain_ascii`   | text      | Cached ASCII form               |
| `error_message`  | text      | Last error (if any)             |

CSV cleaning (`_load_clean_csv`):
- Keeps only `name_col` and `freq_col`.
- Trims whitespace; drops empty names and non‑numeric frequency.
- Builds full domain as `prefix + name + tld_suffix`.

---

## WHOIS behaviour

- **Transport:** raw TCP to the TLD’s WHOIS host on **port 43**.
- **Query:** the domain string followed by CRLF (`\r\n`).
- **Responses:** vary per registry. Parsers live in `check/domains/*.py` and must implement:
  - `whois_server` property (e.g., `whois.dns.pl`).
  - `_status(response: str) -> DomainStatus`.

### Status values
- `AVAILABLE`
- `REGISTERED`
- `UNKNOWN` (server text ambiguous or format unrecognized)
- `ERROR` (socket/transport issues, etc.)

> Respect registry **rate limits**. Configure `--interval` to avoid being blocked.

---
## Airflow integration

This project is designed to run cleanly inside **Apache Airflow**. Below is a production-friendly DAG using `PythonVirtualenvOperator` that isolates dependencies in a per-task virtualenv and reads DB credentials from an Airflow **Connection** (`conn-pg-domains-db`).

> Create the Postgres connection `conn-pg-domains-db` (Conn Type: Postgres) with `Host`, `Login`, `Password`, `Port`, and `Schema` set. The DAG templates these fields at runtime.

### DAG (drop into `addons/airflow_dags/domains_availability_checker_v01.py`)

```python
import os
from airflow import DAG
from airflow.operators.python import PythonVirtualenvOperator
from datetime import datetime, timedelta


def check_domains(
        pguser: str,
        pgpass: str,
        pghost: str,
        pgport: int,
        pgdb: str,
        dictname: str,
        numrecords: int,
        interval: float,
        print_summary: bool,
):

    from domains.domain_availability_checker.auto_check.check import AutoCheck

    pgport = int(pgport)

    ac = AutoCheck()
    ac.init_postgres(
        user=pguser,
        password=pgpass,
        host=pghost,
        port=pgport,
        database=pgdb,
    )
    ac.check_top_n_names(
        dictionary_name=dictname,
        num_records=numrecords,
        check_interval_s=interval,
        print_summary=print_summary,
    )


default_dag_args = {
    "owner": "ownername",
    "retries": 5,
    "retry_delay": timedelta(minutes=30),
}


with DAG(
    dag_id="domains_availability_checker_v01",
    default_args=default_dag_args,
    start_date=datetime(2025, 9, 22),
    schedule="@hourly",
    catchup=False,
    params={},
) as dag:
    check_domains_availability = PythonVirtualenvOperator(
        task_id="check_domains_availability",
        python_callable=check_domains,
        requirements=[
            "pandas==2.3.2",
            "requests==2.32.5",
            "sqlalchemy==2.0.43",
            "psycopg2-binary==2.9.10",
        ],
        system_site_packages=False,  # keep the environment isolated
        op_kwargs={
            "pguser": "{{ conn['conn-pg-domains-db'].login }}",
            "pgpass": "{{ conn['conn-pg-domains-db'].password }}",
            "pghost": "{{ conn['conn-pg-domains-db'].host }}",
            "pgport": "{{ conn['conn-pg-domains-db'].port }}",
            "pgdb": "{{ conn['conn-pg-domains-db'].schema }}",
            "dictname": "words_tld_pl",
            "numrecords": 50,
            "interval": 60,  # be polite to WHOIS servers
            "print_summary": True,
        },
    )
```
---

## License

MIT. See `LICENSE` for details.

