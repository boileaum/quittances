#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Generateur automatique de quittances de loyer
"""

from dateutil.rrule import rrule, MONTHLY
from datetime import datetime
from calendar import monthrange
from jinja2.loaders import FileSystemLoader
from latex.jinja2 import make_env
from latex import build_pdf
import locale
import os
import shutil
import yaml

locale.setlocale(locale.LC_ALL, "fr_FR.UTF-8")

MANDATORY_INPUT_KEYS = set(("address_street",
                            "address_city",
                            "landlord",
                            "landlord_street",
                            "landlord_city",
                            "tenants",
                            "total_amount_letters",
                            "rent",
                            "charges",
                            "first_date",
                            "last_date",
                            "sign_city"))


def read_yaml(yamlfile="quittances.yml"):
    """Read yaml file and return a dict"""
    with open(yamlfile, encoding="utf-8") as stream:
        return yaml.load(stream)


def check_input(input_dict):
    """Return True if keys from input_keys are INPUT_KEYS"""
    input_dict_keys = input_dict.keys()
    for key in MANDATORY_INPUT_KEYS:
        if key not in input_dict_keys:
            raise KeyError("Input parameter {} not found in input dictionnary."
                           .format(key))


def de_elision(word):
    """Prepend word with "d'" or "de" according to first letter"""
    if word[0].lower() in ('a', 'e', 'o', 'u', 'y'):
        return "d'" + word
    else:
        return "de " + word


def generate_quittance(input_dict):

    check_input(input_dict)

    first_date = datetime.strptime(input_dict['first_date'], '%m %Y')
    last_date = datetime.strptime(input_dict['last_date'], '%m %Y')

    rent = float(input_dict['rent'])
    charges = float(input_dict['charges'])
    total_amount = rent + charges
    input_dict['total_amount'] = locale.currency(total_amount, symbol=False)
    input_dict['rent'] = locale.currency(rent, symbol=False)
    input_dict['charges'] = locale.currency(charges, symbol=False)

    tenants = input_dict['tenants'].split(",")
    # Elision du locataire
    dtenants = [de_elision(tenants[0])] + tenants[1:]
    if len(tenants) > 1:
        dtenants = " et ".join(dtenants)
        tenants = " et ".join(tenants)
        pronoun = "leur"
    else:
        dtenants = dtenants[0]
        tenants = tenants[0]
        pronoun = "lui"

    # Get sign_date or return today
    sign_date = input_dict.get('sign_date', "{0:%d} {0:%B} {0:%Y}".format(
                              datetime.now()))

    for d in rrule(MONTHLY, dtstart=datetime(first_date.year, first_date.month,
                                             1),
                   until=datetime(last_date.year, last_date.month, 1)):
        file_name = "{0:%Y}_{0:%m}_quittance.pdf".format(d)
        directory = "quittances"
        if not os.path.exists(directory):
            os.makedirs(directory)
        file_path = os.path.join(directory, file_name)

        mois_de = de_elision("{:%B}".format(d))  # Elision du mois

        start_date = "1er {0:%B} {0:%Y}".format(d)
        end_date = "{1} {0:%B} {0:%Y}".format(d, monthrange(d.year,
                                                            d.month)[1])
        doc_date = "{}-{}".format(d.year, d.month)

        m_dict = {}
        m_dict.update(input_dict)
        m_dict.update({'tenant': tenants,
                       'dtenant': dtenants,
                       'pronoun': pronoun,
                       'month': mois_de,
                       'year': "{:%Y}".format(d),
                       'start': start_date,
                       'end': end_date,
                       'pay_date': start_date,
                       'sign_date': sign_date,
                       'doc_date': doc_date})

        env = make_env(loader=FileSystemLoader('.'))
        tpl = env.get_template('template.tex')
        latex_file = tpl.render(**m_dict)
        pdf = build_pdf(latex_file)
        pdf.save_to(file_path)
        print(file_path)


def make_zip(dir_name="quittances"):
    shutil.make_archive(dir_name, 'zip', dir_name)
    print("Archive stored in {}.zip.".format(dir_name))


if __name__ == '__main__':
    yaml_dict = read_yaml()
    generate_quittance(yaml_dict)
    make_zip()
