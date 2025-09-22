from dotenv import load_dotenv
import argparse

from domain_availability_checker.check.availability import check_domain


def load_args():
    load_dotenv()

    parser =  argparse.ArgumentParser()
    parser.add_argument(
        "--domain", 
        type=str, 
        help="Check if domain is available")
    return parser.parse_args()


def main():
    args = load_args()
    print(check_domain(args.domain).domain_info().status.name)


if __name__ == "__main__":
    main()