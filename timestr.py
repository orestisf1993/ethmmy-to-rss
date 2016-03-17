"""
Module that handles thread-safe locale setting & converting time strings from Greek to English.
"""
import locale
import threading
from datetime import datetime
from contextlib import contextmanager

import constants

LOCALE_LOCK = threading.Lock()


@contextmanager
def setlocale(name):
    with LOCALE_LOCK:
        saved = locale.setlocale(locale.LC_ALL)
        try:
            yield locale.setlocale(locale.LC_ALL, name)
        finally:
            locale.setlocale(locale.LC_ALL, saved)


def el_to_en(date):
    correct_short_months = {"Μαρ": "Μάρ", "Νοε": "Νοέ", "Ιουλ": "Ιούλ", "Ιουν": "Ιούν", "Αυγ": "Αύγ", "Μαϊ": "Μάι"}
    with setlocale('el_GR.UTF-8'):
        for wrong, correct in correct_short_months.items():
            date = date.replace(wrong, correct)
        datetime_date = datetime.strptime(date, constants.ETHMMY_TIME_FORMAT)
    return datetime_date.strftime(constants.RSS_TIME_FORMAT)
