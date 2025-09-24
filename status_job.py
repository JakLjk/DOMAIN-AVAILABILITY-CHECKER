from dotenv import load_dotenv
import argparse
import os
from pathlib import Path

from domain_availability_checker.auto_check.check import AutoCheck


def load_args():
    load_dotenv()

    parser =  argparse.ArgumentParser()
    subparsers = parser.add_subparsers(dest="command")

    common = argparse.ArgumentParser(add_help=False)
    common.add_argument("--dictname", type=str, help="Dictionary table name", required=True)
    common.add_argument("--pguser", type=str, default=os.getenv("PG_USER"),required=False)
    common.add_argument("--pgpass", type=str, default=os.getenv("PG_PASSWORD"), required=False)
    common.add_argument("--pghost", type=str, default=os.getenv("PG_HOST"), required=False)
    common.add_argument("--pgport", type=int, default=int(os.getenv("PG_PORT")), required=False)
    common.add_argument("--pgdb", type=str, default=os.getenv("PG_DATABASE"), required=False)



    load_p = subparsers.add_parser("load", parents=[common], help="Load dictionary")
    load_p.add_argument("--path", type=Path, required=True)
    load_p.add_argument("--namecol", type=str, required=True)
    load_p.add_argument("--freqcol", type=str, required=True)
    load_p.add_argument("--tld-suffix", type=str, required=True)
    load_p.add_argument("--prefix", type=str, default="")
    load_p.add_argument("--overwrite-dict", action="store_true")


    check_p = subparsers.add_parser("check", parents=[common], help="Check availability")
    check_p.add_argument("--numchecks", type=int, default=5)
    check_p.add_argument("--interval", type=float, default=5.0)
    check_p.add_argument("--print-summary", action="store_true")
    check_p.add_argument("--no-print-summary", dest="print-summary", action="store_false")
    check_p.set_defaults(print_summary=True)

    return parser.parse_args()


def main():
    args = load_args()
    auto_check = AutoCheck()
    auto_check.init_postgres(
        user=args.pguser,
        password=args.pgpass,
        host=args.pghost,
        port=args.pgport,
        database=args.pgdb
    )
    if args.command == "load":
        auto_check.load_file_to_postgres_dictionary(
            file_path=str(args.path),
            name_col=args.namecol,
            frequency_col=args.freqcol,
            dictionary_table_name=args.dictname,
            name_prefix=args.prefix,
            tld_suffix=args.tld_suffix,
            overwrite_dictionary_table=args.overwrite_dict
        )
    elif args.command == "check":
        auto_check.check_top_n_names(
            dictionary_name=args.dictname,
            num_records=args.numchecks,
            check_interval_s=args.interval,
            print_summary=args.print_summary
        )
        




if __name__ == "__main__":
    main()