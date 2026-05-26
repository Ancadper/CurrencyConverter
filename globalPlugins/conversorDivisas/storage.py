# -*- coding: utf-8 -*-

import json
import os

import config


try:
    _
except NameError:
    _ = lambda text: text

DATA_DIR_NAME = "conversorDivisas"
DATA_FILE_NAME = "settings.json"
SESSION_HISTORY = []
SESSION_LAST_RESULT = None


def get_data_file():
    try:
        base_dir = config.getUserDefaultConfigPath()
    except Exception:
        base_dir = os.path.expanduser("~")

    data_dir = os.path.join(base_dir, DATA_DIR_NAME)
    os.makedirs(data_dir, exist_ok=True)
    return os.path.join(data_dir, DATA_FILE_NAME)


DATA_FILE = get_data_file()


def default_data():
    return {
        "last_amount": "1",
        "last_source": "EUR",
        "last_target": "USD",
    }


def load_data():
    if not os.path.isfile(DATA_FILE):
        return default_data()

    try:
        with open(DATA_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
    except Exception:
        return default_data()

    if not isinstance(data, dict):
        return default_data()

    result = default_data()
    for key in result:
        if key in data:
            result[key] = data[key]

    return result


def save_data(data):
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    clean_data = default_data()

    for key in clean_data:
        if key in data:
            clean_data[key] = data[key]

    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(clean_data, f, ensure_ascii=False, indent=2)


def add_history_item(message, limit=20):
    global SESSION_LAST_RESULT
    SESSION_LAST_RESULT = message
    SESSION_HISTORY.append(message)
    del SESSION_HISTORY[:-limit]


def get_history():
    return list(SESSION_HISTORY)


def get_last_result_message():
    if SESSION_LAST_RESULT:
        return SESSION_LAST_RESULT
    return _("There are no conversions yet.")
