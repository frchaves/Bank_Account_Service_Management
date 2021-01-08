from flask import abort
import requests


def check_valid_currency(new_currency):
    if new_currency != ("EUR" and "USD"):
        return abort(406, f"currency {new_currency} is not valid. Please insert either EUR or USD")
    else:
        return True


def check_valid_iban(iban):
    iban_check = iban.replace(" ", "")
    openiban_url = f"https://openiban.com/validate/{iban_check}?getBIC=true&validateBankCode=true"
    response = requests.get(url=openiban_url).json()

    if response['valid'] is False:
        return abort(406, f"Openiban says account with iban {iban} is not valid")
    else:
        return True


def convert_amount_currency(amount, currency_sender, currency_receiver):
    fixerio_url = "http://data.fixer.io/api/latest?access_key=a0e8ce1d522c77e3e72266d3dc8ced36&format=1"
    response = requests.get(url=fixerio_url).json()
    ex_rate = response['rates']['USD']
    if currency_sender == "EUR" and currency_receiver == "USD":
        converted_currency_to_usd = amount * ex_rate
        return converted_currency_to_usd
    if currency_sender == "USD" and currency_receiver == "EUR":
        converted_currency_to_eur = amount / ex_rate
        return converted_currency_to_eur
    else:
        return amount
