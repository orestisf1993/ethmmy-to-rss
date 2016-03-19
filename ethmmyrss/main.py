#!/usr/bin/env python
"""
Main module with program logic.
"""
import sys
import json
import logging
import argparse

from bs4 import BeautifulSoup
import requests
import keyring  # gnome keyring requires python-secretestorage

from . import html_parse
from . import constants

logger = None


def handle_credentials(username=None):
    """
    Handle the login credentials.

    :param username: The username to use for login.
    :type username: str
    :return: The username and password combo.
    :rtype: (str, str)
    """
    if username is None:
        password = None
        msg = 'No credentials found.\n'
    else:
        password = keyring.get_password(constants.KEYRING_SERVICE, username)
        msg = 'No password found for username {}.\n'.format(username)
    if not password:
        print(msg, end='')
        username, password = set_credentials()
    return username, password


def set_credentials(username=None):
    """
    Ask user for credentials and save them via keyring module.

    :param username: The username to use.
    :type username: str
    :return: The username and password combo.
    :rtype: (str, str)
    """
    import getpass
    if username is None:
        username = input('Username:')
    new_password = getpass.getpass()
    keyring.set_password(constants.KEYRING_SERVICE, username, new_password)
    return username, new_password


def load_username():
    """
    Load the saved username from the config file.

    :return: The username if found, None otherwise.
    :rtype: str or None
    """
    try:
        with open(constants.CONFIG_FILE_NAME, 'r') as file_obj:
            logger.info("Load username from file %s.", constants.CONFIG_FILE_NAME)
            return json.load(file_obj)['username']
    except FileNotFoundError:
        return None


def login(username, password):
    """
    Start a new session with ethmmy.

    :param username: The username to use.
    :type username: str
    :param password: The password to use.
    :type password: str
    :return: The session and the response.
    :rtype: (requests.Session, requests.Response)
    """
    # Start a session so we can have persistent cookies.
    session = requests.session()

    # This is the form data that the page sends when logging in.
    login_data = {
        'username': username, 'password': password, 'submit': 'Υποβολή',
    }

    # Authenticate.
    logger.info("Sending login data to ethmmy")
    response = session.post(constants.LOGIN_URL, data=login_data)
    return session, response


def save_username(username):
    """
    Save the username to the config file.
    :param username: The username.
    :type username: str
    :return: None.
    :rtype: None
    """
    with open(constants.CONFIG_FILE_NAME, 'w') as file_obj:
        logging.info("Saving username %s at file %s.", username, constants.CONFIG_FILE_NAME)
        json.dump({'username': username}, file_obj)


def parse_args():
    """
    Parse arguments from stdin.

    :return: argparse object that stores attributes parsed.
    :rtype: argparse.Namespace
    """
    parser = argparse.ArgumentParser()
    parser.add_argument('-d', '--debug', help="Print lots of debugging statements", action="store_const",
                        dest="log_level", const=logging.DEBUG, default=logging.WARNING, )
    parser.add_argument('-v', '--verbose', help="Be verbose.", action="store_const", dest="log_level",
                        const=logging.INFO, )
    parser.add_argument('-q', '--quiet', help="Only print errors.", action="store_const", dest="log_level",
                        const=logging.ERROR)
    parser.add_argument('-n', '--new-login', help="Forget old username and enter a new one.", action="store_true",
                        dest="new_login", default=False)
    return parser.parse_args()


def main():
    """
    Main function that submits username & password and creates the connection with ethmmy.

    :return: 0 on successful execution.
    :rtype: int
    """

    args = parse_args()
    global logger
    logging.basicConfig(level=args.log_level)
    logger = logging.getLogger(__name__)
    logger.debug("Initialized logger at log_level:%s", str(args.log_level))

    if args.new_login:
        username = None
    else:
        username = load_username()
    logger.info("Acquiring username & password.")
    username, password = handle_credentials(username)
    logger.info("Saving username.")
    save_username(username)
    logger.info("Attempting login.")
    session, response = login(username, password)

    soup = BeautifulSoup(response.text, "html.parser")
    url_texts, urls = html_parse.find_all_course_urls(soup)
    for name, url in zip(url_texts, urls):
        logger.info("Downloading course page for %s at %s.", name, url)
        response = session.get(url)
        course_page = BeautifulSoup(response.text, "html.parser")
        logger.info("Searching for announcement url for %s.", name)
        announcement_url = html_parse.get_announcement_page_url(course_page)
        logger.info("Downloading announcement page for %s from %s.", name, announcement_url)
        response = session.get(announcement_url)
        announcement_page = BeautifulSoup(response.text, "html.parser")
        logger.info("Extracting announcements for %s.", name)
        html_parse.extract_announcements(announcement_page, name)

    return 0


if __name__ == '__main__':
    sys.exit(main())
