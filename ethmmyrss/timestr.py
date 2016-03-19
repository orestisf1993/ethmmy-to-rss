"""
Module that uses icu & datetime to convert time string. from eTHMMY's (Greek) locale to english rss-friendly time
strings.
"""

from datetime import datetime

from ethmmyrss import constants

TIME_TRANSLATE = {
    'Ιαν': 'Jan',
    'Φεβ': 'Feb',
    'Μαρ': 'Mar',
    'Απρ': 'Apr',
    'Μαϊ': 'May',
    'Ιουν': 'Jun',
    'Ιουλ': 'Jul',
    'Αυγ': 'Aug',
    'Σεπ': 'Sep',
    'Οκτ': 'Oct',
    'Νοε': 'Nov',
    'Δεκ': 'Dec',
    'μμ': 'pm',
    'πμ': 'am'
}


def el_to_datetime(date):
    """
    Convert a date string retrieved from ethmmy from Greek to English.

    :param date: The Greek date string.
    :type date: str
    :return: The date object.
    :rtype: datetime.datetime
    """
    for greek, english in TIME_TRANSLATE.items():
        date = date.replace(greek, english)
    return datetime.strptime(date, constants.ETHMMY_TIME_FORMAT)


def datetime_to_rss(date):
    """
    Convert a datetime object to English rss-accepted date string.
    :param date: The date.
    :type date: datetime.datetime
    :return: The rss-accepted date string.
    :rtype: str
    """
    return date.strftime(constants.RSS_TIME_FORMAT)
