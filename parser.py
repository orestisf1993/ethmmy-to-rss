import re
import os

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import jinja2

import constants
import timestr


def get_absolute_url(url):
    """
    Ensure that a URL is absolute.

    :param url: The URL.
    :type: str
    :return: The absolute URL.
    """
    return url if is_absolute(url) else urlparse.urljoin(constants.URL_BASE, url)


def is_absolute(url):
    """
    Check if URL is absolute.

    :param url: The URL.
    :type: str
    :return: True if URL is absolute, False otherwise.
    :rtype: bool
    """
    return bool(urlparse.urlparse(url).netloc)


def find_all_course_urls(
        main_page,
        regex=re.compile(r'/eTHMMY/cms\.course\.login\.do'),
        ignore=('φοιτητικοι διαγωνισμοι',)):
    # TODO: explain
    search_results = main_page.find_all('a', href=regex)
    search_results = [result for result in search_results if result.text.lower() not in ignore]
    search_results = [result for result in search_results if result.img]
    url_texts = [result.text.replace('\n', ' ').replace('\r', '').replace('\t', ' ') for result in search_results]
    url_texts = [re.sub(r'\s+', ' ', text).strip() for text in url_texts]
    urls = [result.get('href') for result in search_results]
    urls = [get_absolute_url(url) for url in urls]
    return url_texts, urls


def get_announcement_page_url(course_page, regex=re.compile(r'/eTHMMY/cms\.announcement\.data\.do')):
    return get_absolute_url(course_page.find('a', href=regex).get('href'))


def extract_announcements(announcement_page, course_name):
    # TODO: feed title & links.
    from xml.sax.saxutils import escape
    feed_file_name = os.path.join("exported", course_name + '.xml')
    os.makedirs("exported", exist_ok=True)
    titles = announcement_page.find_all('p', {'class': 'listLabel'})
    str_dates = [x.parent.find_all('p')[1].find_all('b')[0].text for x in titles]
    en_str_dates = [timestr.el_to_en(date) for date in str_dates]
    titles_str = [escape(''.join(title.stripped_strings)) for title in titles]
    messages = [title.parent for title in titles]
    # Delete announcement name from each message:
    [message.p.extract() for message in messages]
    # TODO: rss compatible html?
    messages = [str(message.text) for message in messages]
    # TODO: better .xml template with named fields not indeces.
    list_lists = [[title, constants.URL_BASE, message, date] for title, message, date in
                  zip(titles_str, messages, en_str_dates)]

    env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
    result = env.get_template('feed-template.xml').render(items=list_lists)
    with open(feed_file_name, 'w') as file_obj:
        file_obj.write(result)
