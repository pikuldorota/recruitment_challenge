import urllib.request
from bs4 import BeautifulSoup


def site_map(url):
    dictionary = dict()
    links = {url}
    while links:
        link = links.pop()
        with urllib.request.urlopen(link) as response:
            html = BeautifulSoup(response.read(), features='lxml')

        title = html.find('title').renderContents().decode()
        new_links = set()
        for href in html.findAll('a'):
            new_link = href.get('href')
            if url in new_link:
                new_links.add(new_link)
            elif new_link.startswith('/'):
                proper_link = '{}{}'.format(url, new_link)
                new_links.add(proper_link)

        dictionary[link] = {'title': title, 'links': new_links}
        links |= new_links
        links = links.difference(dictionary.keys())

    return dictionary


if __name__ == "__main__":
    print(site_map('http://0.0.0.0:8000'))
