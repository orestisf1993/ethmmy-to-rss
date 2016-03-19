"""
Module that uses icu & datetime to convert time string. from eTHMMY's (Greek) locale to english rss-friendly time
strings.
"""

from datetime import datetime
import icu

from ethmmyrss import constants

ETHMMY_LOCALE = icu.Locale('el_GR')
ETHMMY_DATE_PARSER = icu.SimpleDateFormat(constants.ETHMMY_TIME_FORMAT, ETHMMY_LOCALE)


def el_to_datetime(date):
    """
    Convert a date string retrieved from ethmmy from Greek to English.

    :param date: The Greek date string.
    :type date: str
    :return: The date object.
    :rtype: datetime.datetime
    """
    return datetime.fromtimestamp(ETHMMY_DATE_PARSER.parse(date))


def datetime_to_rss(date):
    """
    Convert a datetime object to English rss-accepted date string.
    :param date: The date.
    :type date: datetime.datetime
    :return: The rss-accepted date string.
    :rtype: str
    """
    return date.strftime(constants.RSS_TIME_FORMAT)
