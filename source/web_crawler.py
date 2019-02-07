import sys
import validators
import urllib.parse
import urllib.request
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from urllib.error import URLError


def site_map(url):
    """This function produces map of urls on given site with titles of each site which is reachable within the domain"""
    __validate_url(url)
    parsed_url = urllib.parse.urlparse(url)
    domain = '{url.scheme}://{url.netloc}/'.format(url=parsed_url)
    dictionary = dict()
    links = {url}

    while links:
        link = links.pop()
        # unreachable link is saved to dictionary with a note and it continues to the next link
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
        new_links = __find_links(html, link, domain)
        dictionary[link] = {'title': title, 'links': new_links}

        # define new links set as set sum of links and new_links with omitting already defined in dictionary links
        links |= new_links
        links = links.difference(dictionary.keys())

    return dictionary


def __find_links(html, link, domain):
    """Looks for all links on given site and returns only this that are in the same domain"""
    new_links = set()
    for href in html.findAll('a'):
        new_link = href.get('href')
        if not new_link:
            continue
        if new_link.startswith(domain):
            if validators.url(new_link):
                new_links.add(new_link)
        else:
            proper_link = urljoin(link, new_link)
            if (validators.url(proper_link) or proper_link.startswith("http://0.0.0.0:8000"))\
                    and proper_link.startswith(domain):
                new_links.add(proper_link)
    return new_links


def __validate_url(url):
    """Checks if url is valid and reachable. Exits if it's not"""
    if not validators.url(url) and not url.startswith("http://0.0.0.0:8000"):
        sys.exit("URL address provided is not correct")
    try:
        code = urllib.request.urlopen(url).code
        if code >= 400:
            sys.exit("Error occurred while reaching the page")
    except URLError:
        sys.exit("Error occurred while reaching the page")
