import sys
import validators
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.error import URLError


def site_map(url):

    __validate_url(url)

    dictionary = dict()
    links = {url}

    while links:
        link = links.pop()
        try:
            with urllib.request.urlopen(link) as response:
                html = BeautifulSoup(response.read(), features='lxml')
        except URLError:
            print("{} not reachable".format(link), file=sys.stderr)
            dictionary[link]: "Page not reachable"
            links = links.difference(dictionary.keys())
            continue

        if html.find('title'):
            title = html.find('title').renderContents().decode()
        else:
            title: ''
        new_links = __find_links(html, url)
        dictionary[link] = {'title': title, 'links': new_links}

        links |= new_links
        links = links.difference(dictionary.keys())

    return dictionary


def __find_links(html, url):
    new_links = set()
    for href in html.findAll('a'):
        new_link = href.get('href')
        if not new_link:
            continue
        if url in new_link and new_link.startswith('http'):
            if validators.url(new_link):
                new_links.add(new_link)
        else:
            proper_link = urljoin(url, new_link)
            if validators.url(new_link) and proper_link.startswith(url):
                new_links.add(proper_link)
    return new_links


def __validate_url(url):
    if not validators.url(url):
        sys.exit("URL address provided is not correct")
    try:
        code = urllib.request.urlopen(url).code
        if code >= 400:
            sys.exit("Error occurred while reaching the page")
    except URLError:
        sys.exit("Error occurred while reaching the page")
