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


    load_p = subparsers.add_parser("load", parents=[common], help="Load dictionary")
    load_p.add_argument("--path", default=os.getenv(), type=Path, required=True)
    load_p.add_argument("--namecol", type=str, required=True)
    load_p.add_argument("--freqcol", type=str, required=True)
    load_p.add_argument("--tld_suffix", type=str, required=True)
    load_p.add_argument("--prefix", type=str, default="")
    load_p.add_argument("--overwrite_dict", action="store_true")  # boolean flag


    check_p = subparsers.add_parser("check", parents=[common], help="Check availability")
    check_p.add_argument("--numchecks", type=int, default=5)
    check_p.add_argument("--interval", type=float, default=5.0)
    check_p.add_argument("--print_summary", action="store_true")
    check_p.add_argument("--no-print_summary", dest="print_summary", action="store_false")
    check_p.set_defaults(print_summary=True)


def main():
    args = load_args()
    auto_check = AutoCheck()
    auto_check.init_postgres(
        user=os.getenv("PG_USER"),
        password=os.getenv("PG_PASSWORD"),
        host=os.getenv("PG_HOST"),
        port=int(os.getenv("PG_PORT")),
        database=os.getenv("PG_DATABASE")
    )
    if args.command == "load":
        auto_check.load_file_to_postgres_dictionary(
            file_path=args.load.path,
            name_col=args.namecol,
            frequency_col=args.freqcol,
            dictionary_table_name=args.dictname,
            name_prefix=args.prefix,
            tld_suffix=args.tld_suffix,
            overwrite_dictionary_table=args.overwrite_dict
        )
    if args.command == "check":
        auto_check.check_top_n_names(
            dictionary_name=args.dictname,
            num_records=args.numchecks,
            check_interval_s=args.interval,
            print_summary=args.print_summary
        )
        




if __name__ == "__main__":
    main()