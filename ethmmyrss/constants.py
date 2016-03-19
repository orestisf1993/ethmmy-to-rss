"""
Module with various used constants.
"""
KEYRING_SERVICE = 'ethmmy-rss'
CONFIG_FILE_NAME = 'settings.json'
URL_BASE = r'https://alexander.ee.auth.gr:8443/eTHMMY/'
LOGIN_URL = r'https://alexander.ee.auth.gr:8443/eTHMMY/loginAction.do'
# d: Day of the month as a decimal number [01,31].
# MMM: Locale’s abbreviated month name.
# y: Year with century as a decimal number.
# h: Hour (12-hour clock) as a decimal number [01,12].
# m: Minute as a decimal number [00,59].
# a: Locale’s equivalent of either AM or PM.
ETHMMY_TIME_FORMAT = r'd MMM y h:m a'
RSS_TIME_FORMAT = r'%a, %d %b %Y %H:%M:%S %z'
