#!/usr/bin/env python
"""
Main module with program logic.
"""
# TODO: docstrings
# TODO: main logic to combine parser
# TODO: pylint
import sys
import json
# TODO: logging

from bs4 import BeautifulSoup
import requests
import keyring  # gnome keyring requires python-secretestorage

import parser
import constants


def handle_credentials(username=None):
    """
    Handle the login credentials.

    :param username:
    :return:
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

    :return:
    """
    import getpass
    if username is None:
        username = input('Username:')
    new_password = getpass.getpass()
    keyring.set_password(constants.KEYRING_SERVICE, username, new_password)
    return username, new_password


def load_username():
    try:
        with open(constants.CONFIG_FILE_NAME, 'r') as file_obj:
            return json.load(file_obj)['username']
    except FileNotFoundError:
        return None


def login(username, password):
    # Start a session so we can have persistent cookies.
    session = requests.session()

    # This is the form data that the page sends when logging in.
    login_data = {
        'username': username,
        'password': password,
        'submit': 'Υποβολή',
    }

    # Authenticate.
    response = session.post(constants.LOGIN_URL, data=login_data)
    return session, response


def save_username(username):
    with open(constants.CONFIG_FILE_NAME, 'w') as file_obj:
        json.dump({'username': username}, file_obj)


def main():
    """
    Main function that submits username & password and creates the connection with ethmmy.

    :return:
    """

    # TODO: argparse
    # --one-file vs --multi-file

    username = load_username()
    username, password = handle_credentials(username)
    save_username(username)
    session, response = login(username, password)
    # TODO: error checking.

    soup = BeautifulSoup(response.text, "html.parser")
    url_texts, urls = parser.find_all_course_urls(soup)
    for name, url in zip(url_texts, urls):
        response = session.get(url)
        course_page = BeautifulSoup(response.text, "html.parser")
        announcement_url = parser.get_announcement_page_url(course_page)
        response = session.get(announcement_url)
        announcement_page = BeautifulSoup(response.text, "html.parser")
        parser.extract_announcements(announcement_page, name)

    # TODO: delete
    # Start IPython for debugging.
    # __import__("IPython").embed()

    return 0


if __name__ == '__main__':
    sys.exit(main())
