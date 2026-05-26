# -*- coding: utf-8 -*-

import json
import urllib.parse
import urllib.request


try:
    _
except NameError:
    _ = lambda text: text

API_BASE_URL = "https://api.frankfurter.dev/v1/latest"
CURRENCIES_URL = "https://api.frankfurter.dev/v1/currencies"
_CURRENCY_CACHE = None

FALLBACK_CURRENCIES = [
    ("EUR", "Euro"),
    ("USD", "US Dollar"),
    ("GBP", "Pound Sterling"),
    ("JPY", "Japanese Yen"),
    ("CHF", "Swiss Franc"),
    ("CAD", "Canadian Dollar"),
    ("AUD", "Australian Dollar"),
    ("NZD", "New Zealand Dollar"),
    ("MXN", "Mexican Peso"),
    ("ARS", "Argentine Peso"),
    ("BRL", "Brazilian Real"),
    ("CLP", "Chilean Peso"),
    ("COP", "Colombian Peso"),
    ("PEN", "Peruvian Sol"),
    ("UYU", "Uruguayan Peso"),
    ("CNY", "Chinese Yuan"),
    ("HKD", "Hong Kong Dollar"),
    ("SGD", "Singapore Dollar"),
    ("SEK", "Swedish Krona"),
    ("NOK", "Norwegian Krone"),
    ("DKK", "Danish Krone"),
    ("PLN", "Polish Zloty"),
    ("CZK", "Czech Koruna"),
    ("HUF", "Hungarian Forint"),
    ("TRY", "Turkish Lira"),
    ("INR", "Indian Rupee"),
    ("ZAR", "South African Rand"),
]


def currency_label(code, name):
    return f"{code} - {name}"


def sort_currencies(currencies):
    return sorted(
        currencies,
        key=lambda item: currency_label(item[0], item[1]).casefold()
    )


def fetch_currencies(timeout=10):
    request = urllib.request.Request(
        CURRENCIES_URL,
        headers={"User-Agent": "NVDA conversorDivisas add-on"},
    )

    with urllib.request.urlopen(request, timeout=timeout) as response:
        data = json.loads(response.read().decode("utf-8"))

    if not isinstance(data, dict):
        raise RuntimeError(_("The API did not return a valid currency list."))

    currencies = []

    for code, name in data.items():
        code = str(code).upper().strip()
        name = str(name).strip()

        if code and name:
            currencies.append((code, name))

    if not currencies:
        raise RuntimeError(_("The API did not return any available currencies."))

    return sort_currencies(currencies)


def get_currencies(refresh=False):
    global _CURRENCY_CACHE

    if _CURRENCY_CACHE is not None and not refresh:
        return list(_CURRENCY_CACHE)

    try:
        _CURRENCY_CACHE = fetch_currencies()
    except Exception:
        _CURRENCY_CACHE = sort_currencies(FALLBACK_CURRENCIES)

    return list(_CURRENCY_CACHE)


def currency_choices():
    return [currency_label(code, name) for code, name in get_currencies()]


def code_from_choice(choice):
    if not choice:
        return ""
    return choice.split("-", 1)[0].strip().upper()


def format_number(value):
    try:
        number = float(value)
    except Exception:
        return str(value)

    text = f"{number:,.4f}".rstrip("0").rstrip(".")
    return text.replace(",", " ")


def parse_amount(text):
    value = text.strip().replace(" ", "").replace(",", ".")

    if not value:
        raise ValueError(_("Enter an amount."))

    try:
        amount = float(value)
    except Exception:
        raise ValueError(_("The amount is not valid."))

    if amount <= 0:
        raise ValueError(_("The amount must be greater than zero."))

    return amount


def convert(amount, source, target, timeout=10):
    source = source.upper().strip()
    target = target.upper().strip()

    if not source or not target:
        raise ValueError(_("Select source and target currencies."))

    if source == target:
        return {
            "amount": amount,
            "source": source,
            "target": target,
            "result": amount,
            "date": _("same currency"),
        }

    params = urllib.parse.urlencode({
        "amount": amount,
        "from": source,
        "to": target,
    })
    url = f"{API_BASE_URL}?{params}"

    request = urllib.request.Request(
        url,
        headers={"User-Agent": "NVDA conversorDivisas add-on"},
    )

    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            data = json.loads(response.read().decode("utf-8"))
    except Exception as e:
        raise RuntimeError(
            _("Could not get the exchange rate. Check your Internet connection or try again later.")
        ) from e

    rates = data.get("rates", {})

    if target not in rates:
        raise RuntimeError(_("The API did not return the target currency."))

    return {
        "amount": amount,
        "source": source,
        "target": target,
        "result": rates[target],
        "date": data.get("date", _("no date")),
    }


def result_message(result):
    return _("{amount} {source} is approximately {result} {target}. Exchange rate date: {date}.").format(
        amount=format_number(result["amount"]),
        source=result["source"],
        result=format_number(result["result"]),
        target=result["target"],
        date=result["date"],
    )
