import json
import logging

import keyring

logger = logging.getLogger(__name__)


def handle_credentials(keyring_service, username=None, use_keyring=True):
    """
    Handle the login credentials.

    :param keyring_service: The service that the keyring uses.
    :param username: The username to use for login.
    :type username: str
    :param use_keyring: True if the keyring is to be used to save the user's password.
    :type use_keyring: bool
    :return: The username and password combo.
    :rtype: (str, str)
    """
    if username is None:
        password = None
        msg = 'No credentials found.\n'
    else:
        if use_keyring:
            password = keyring.get_password(keyring_service, username)
        else:
            password = None
        msg = 'No password found for username {}.\n'.format(username)
    if not password:
        print(msg, end='')
        username, password = set_credentials(keyring_service, username, use_keyring=use_keyring)
    return username, password


def set_credentials(keyring_service, username=None, use_keyring=True):
    """
    Ask user for credentials and save them via keyring module.

    :param keyring_service: The service that the keyring uses.
    :param username: The username to use.
    :type username: str
    :param use_keyring: True if the keyring is to be used to save the user's password.
    :type use_keyring: bool
    :return: The username and password combo.
    :rtype: (str, str)
    """
    import getpass
    if username is None:
        username = input('Username:')
    new_password = getpass.getpass()
    if use_keyring:
        keyring.set_password(keyring_service, username, new_password)
    return username, new_password


def load_username(file_name):
    """
    Load the saved username from the config file.

    :param file_name: Name of the file that holds the username.
    :type file_name: str
    :return: The username if found, None otherwise.
    :rtype: str or None
    """
    try:
        with open(file_name, 'r') as file_obj:
            logger.info("Load username from file %s.", file_name)
            return json.load(file_obj)['username']
    except FileNotFoundError:
        return None


def save_username(username, file_name):
    """
    Save the username to the config file.

    :param file_name: Name of the file that holds the username.
    :type file_name: str
    :param username: The username.
    :type username: str
    :return: None.
    :rtype: None
    """
    with open(file_name, 'w') as file_obj:
        logger.info("Saving username %s at file %s.", username, file_name)
        json.dump({'username': username}, file_obj)
