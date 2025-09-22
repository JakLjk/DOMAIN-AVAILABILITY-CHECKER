import argparse

from domain_availability_checker.check.domains.pl import DomainPL
from domain_availability_checker.check.availability import check_domain
from domain_availability_checker.auto_check.check import AutoCheck

path = "/home/thinkpad/shared_folder/PROJECTS_2/DOMAIN-AVAILABILITY-CHECKER/domain_availability_checker/auto_check/dictionaries/slownik_pl.csv"

# d = DomainPL()
# d.get("lej1323213123k.pl")
# print(d.domain_info().status.name)

# print(check_domain("sdasdak1.pl").domain_info().status.name)

d = AutoCheck()
d.init_postgres(
    user="docker",
    password="docker",
    host="192.168.0.12",
    port=5432,
    database="domains"
)
# d.load_file_to_postgres_dictionary(
#     path,
#     "Unnamed: 0",
#     "freq",
#     "words_pl",
#     "",
#     ".pl",
#     True
# )
d.check_top_n_names("words_pl", 5, 5)


def arguments():


def check_domain_status(domain:str):
    return check_domain(domain).domain_info().status.name


def main():
    pass


if __name__ == "__main__":
    main()