import pandas as pd
import requests
import re, sys, os
import unicodedata
from bs4 import BeautifulSoup
from datetime import datetime

NA = 'NA'

urls = [
    'https://play.google.com/store/apps/details?id=com.sympatient.invirto',
    'https://play.google.com/store/apps/details?id=com.newsenselab.android.m_sense_migraine',
    'https://play.google.com/store/apps/details?id=de.mynoise.kalmeda',
    'https://play.google.com/store/apps/details?id=de.rehappy.app.rehappy',
    'https://play.google.com/store/apps/details?id=de.mementor.somnio',
    'https://play.google.com/store/apps/details?id=de.aidhere.zanadio',
    'https://play.google.com/store/apps/details?id=com.vivira.android',
    'https://apps.apple.com/de/app/invirto/id1482760714',
    'https://apps.apple.com/de/app/id1511739470',
    'https://apps.apple.com/de/app/kalmeda-mynoise/id1437379931',
    'https://apps.apple.com/de/app/rehappy/id1357107437',
    'https://apps.apple.com/de/app/vivira-r%C3%BCcken-knie-und-h%C3%BCfte/id1093858117',
    'https://apps.apple.com/de/app/somnio/id1523016446',
    'https://apps.apple.com/de/app/zanadio/id1499824614'
]

def extract_from_soup(soup, url):
    app_data = {
        'app_fullname': NA,
        'app_name': NA,
        'app_id': NA,
        'platform': NA,
        'scraping_timestamp': datetime.now().replace(microsecond=0).isoformat(' '), # aktuelle Uhrzeit formatiert nach ISO 861
        'app_size': NA,
        'version': NA,
        'last_updated': NA,
        'downloads_bin': NA,
        'n_ratings': NA,
        'average_rating': NA
    }

    if 'play.google.com' in url:
        app_data['platform'] = 'google_play'

        try:
            app_data['app_fullname'] = soup.select('h1 span')[0].text
            app_data['app_id'] = url.split("?id=")[-1].split('&')[0] # letzter Bestandteil der URL
            app_data['app_size'] = list(soup.find_all(text=re.compile('Size'))[0].parent.next_siblings)[-1].text
            app_data['version'] = list(soup.find_all(text=re.compile('Current Version'))[0].parent.next_siblings)[0].text
            app_data['last_updated'] = list(soup.find_all(text=re.compile('Updated'))[0].parent.next_siblings)[0].text
            app_data['downloads_bin'] = list(soup.find_all(text=re.compile('Installs'))[0].parent.next_siblings)[0].text
            app_data['n_ratings'] = [int(span.text) for span in soup.select('c-wiz span span') if span.text.isdigit()][0]
            app_data['average_rating'] = [div['aria-label'] for div in soup.select('div') if div.has_attr('aria-label') and "stars out of" in div['aria-label']][0].split()[1]

        except Exception as e:
            print(f"Error parsing {url}: {e}")

    elif 'apps.apple.com' in url:
        app_data['platform'] = 'itunes'

        try:
            app_data['app_fullname'] = soup.select('.product-header__title')[0].find(text=True, recursive=False).strip()
            app_data['app_id'] = url.split("/")[-1][2:]
            app_data['app_size'] = unicodedata.normalize('NFKD', soup.select('.information-list--app > .information-list__item:nth-child(2) > .information-list__item__definition')[0].text)
            app_data['version'] = soup.select('.whats-new__latest__version')[0].text.split()[-1]
            app_data['last_updated'] = [t for t in soup.select('time') if t.has_attr('data-test-we-datetime')][0].text
            app_data['n_ratings'] = soup.select('.we-customer-ratings__count')[0].text.split()[0]
            app_data['average_rating'] = soup.select('.we-customer-ratings__averages__display')[0].text

        except Exception as e:
            print(f"Error parsing {url}: {e}")
    
    """ app_name should be the first word. split at whitespace. sometimes, the first
    word ends with a ':' or similar, so remove the last character if it's not a letter."""

    app_data['app_name'] = app_data['app_fullname'].split()[0] # first word of the long name
    if not app_data['app_name'][-1].isalpha():
        app_data['app_name'] = app_data['app_name'][:-1]

    return app_data

if __name__ == '__main__':
    if len(sys.argv) > 1:
        print(f"Reading URLs from {sys.argv[1]}... ", end='', flush=True)
        try:
            with open(sys.argv[1]) as f:
                urls = [line.rstrip('\n') for line in f if not line.startswith('#')]
                print(f"Read {len(urls)} URLs.")
        except FileNotFoundError:
            print("Error loading file!")
            exit(1)

    else:
        print("No URL file provided, using default URLs.")

    rows = []
    for url in urls:
        print(url)
        try:
            r = requests.get(url)
            soup = BeautifulSoup(r.text, 'html.parser')
        except Exception as e:
            print(e)
            continue        

        rows.append(extract_from_soup(soup, url))

    out_path = 'appstore_data.csv'
    df = pd.DataFrame(rows)
    df.to_csv(out_path, 
        index = False,
        mode = 'a',
        header = not os.path.exists(out_path) # add header only if file didn't exist before
    )
