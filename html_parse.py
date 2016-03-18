"""
Module that holds functions that handle the parsing of ethmmy pages.
"""
import operator
import os
import re
import logging

try:
    import urlparse
except ImportError:
    import urllib.parse as urlparse

import jinja2

import constants
import timestr

logger = logging.getLogger(__name__)


def get_absolute_url(url):
    """
    Ensure that a URL is absolute.

    :param url: The URL.
    :type: str
    :return: The absolute URL.
    :rtype: str
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


def find_all_course_urls(main_page, regex=re.compile(r'/eTHMMY/cms\.course\.login\.do'),
                         ignore=('φοιτητικοι διαγωνισμοι',)):
    """
    Find all the URLs to point to a course page from a page.
    :param main_page: The page to search the URLs in.
    :type main_page: bs4.BeautifulSoup
    :param regex: The regex to use for searching.
    :param ignore: Courses to ignore.
    :type ignore: iterable
    :return: The course names + URLs.
    :rtype: [list, list]
    """
    # Search all links.
    search_results = main_page.find_all('a', href=regex)
    # Remove ignored courses.
    search_results = [result for result in search_results if result.text.lower() not in ignore]
    # Keep only those having the image, to avoid adding the current course link.
    search_results = [result for result in search_results if result.img]
    # Remove unneeded whitespace in course names.
    url_texts = [result.text.replace('\n', ' ').replace('\r', '').replace('\t', ' ') for result in search_results]
    url_texts = [re.sub(r'\s+', ' ', text).strip() for text in url_texts]
    # Get the URLs from search_results and convert them to absolute.
    urls = [result.get('href') for result in search_results]
    urls = [get_absolute_url(url) for url in urls]
    return url_texts, urls


def get_announcement_page_url(course_page, regex=re.compile(r'/eTHMMY/cms\.announcement\.data\.do')):
    """
    Get the URL for the announcement page from a course page.

    :param course_page: The course page.
    :type course_page: bs4.BeautifulSoup
    :param regex: The regex to use for searching.
    :return: The URL.
    :rtype: str
    """
    return get_absolute_url(course_page.find('a', href=regex).get('href'))


def extract_announcements(announcement_page, course_name):
    """
    Save all announcements from a specified announcement page in rss .xml format in specified file in exported/ folder.

    :param announcement_page: The announcement page.
    :param course_name: The course name. Also used for the filename.
    :return: None.
    :rtype: None
    """
    from xml.sax.saxutils import escape
    feed_file_name = os.path.join("exported", course_name + '.xml')
    os.makedirs("exported", exist_ok=True)
    titles = announcement_page.find_all('p', {'class': 'listLabel'})
    logger.debug("Got %d titles for %s.", len(titles), course_name)

    str_dates = [x.parent.find_all('p')[1].find_all('b')[0].text for x in titles]
    dates = [timestr.el_to_datetime(date) for date in str_dates]
    rss_dates = [timestr.datetime_to_rss(date) for date in dates]
    logger.debug("Found dates:\n%s\nConverted to datetime objects:\n%s\nConverted to rss dates:\n%s", str(str_dates),
                 str(dates), str(rss_dates))
    titles_str = [escape(''.join(title.stripped_strings)) for title in titles]
    messages = [title.parent for title in titles]
    # Delete announcement name from each message:
    for message in messages:
        message.p.extract()

    # Convert messages to HTML strings.
    messages = [str(message).strip() for message in messages]

    feed_items = [{'title': title, 'text': text, 'date': date} for title, text, date in
                  zip(titles_str, messages, rss_dates)]
    # Sort according to date list. reverse=True => newer are at the beginning.
    feed_items = [x for (_, x) in sorted(zip(dates, feed_items), key=operator.itemgetter(0), reverse=True)]

    logger.debug("Loading jinja2 template.")
    env = jinja2.Environment(loader=jinja2.FileSystemLoader("."))
    result = env.get_template('feed-template.xml').render(items=feed_items, title=course_name, url=constants.URL_BASE)
    with open(feed_file_name, 'w') as file_obj:
        logger.info("Saving feed for %s at file %s.", course_name, feed_file_name)
        file_obj.write(result)
