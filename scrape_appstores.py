import pandas as pd
import requests
import re
import os
from bs4 import BeautifulSoup
from datetime import datetime

NA = 'NA'

urls = {
    'google_play': [
        'https://play.google.com/store/apps/details?id=com.sympatient.invirto',
        'https://play.google.com/store/apps/details?id=com.newsenselab.android.m_sense_migraine',
        'https://play.google.com/store/apps/details?id=de.mynoise.kalmeda',
        'https://play.google.com/store/apps/details?id=de.rehappy.app.rehappy',
        'https://play.google.com/store/apps/details?id=de.mementor.somnio',
        'https://play.google.com/store/apps/details?id=de.aidhere.zanadio',
        'https://play.google.com/store/apps/details?id=com.vivira.android'
    ],
    'itunes': [
        'https://apps.apple.com/de/app/invirto/id1482760714',
        'https://apps.apple.com/de/app/id1511739470',
        'https://apps.apple.com/de/app/kalmeda-mynoise/id1437379931',
        'https://apps.apple.com/de/app/rehappy/id1357107437',
        'https://apps.apple.com/de/app/vivira-r%C3%BCcken-knie-und-h%C3%BCfte/id1093858117',
        'https://apps.apple.com/de/app/somnio/id1523016446',
        'https://apps.apple.com/de/app/zanadio/id1499824614'
    ]
}

def extract_from_soup(soup, url):
    app_fullname = NA
    app_id = NA
    app_size = NA
    app_version = NA
    last_updated = NA
    n_ratings = NA
    downloads = NA
    avg_rating = NA
    platform = NA

    if 'play.google.com' in url:
        platform = 'google_play'

        app_fullname = soup.select('h1 span')[0].text
        app_id = url.split("?id=")[-1].split('&')[0] # letzter Bestandteil der URL

        try:
            app_size = list(soup.find_all(text=re.compile('Size'))[0].parent.next_siblings)[-1].text
            app_version = list(soup.find_all(text=re.compile('Current Version'))[0].parent.next_siblings)[0].text
            last_updated = list(soup.find_all(text=re.compile('Updated'))[0].parent.next_siblings)[0].text
            downloads = list(soup.find_all(text=re.compile('Installs'))[0].parent.next_siblings)[0].text
            n_ratings = [int(span.text) for span in soup.select('c-wiz span span') if span.text.isdigit()][0]
            avg_rating = [div['aria-label'] for div in soup.select('div') if div.has_attr('aria-label') and "stars out of" in div['aria-label']][0].split()[1]

        except Exception as e:
            print(f"Error parsing {url}: {e}")

    elif 'apps.apple.com' in url:
        platform = 'itunes'

        app_id = url.split("/")[-1][2:]

    return {
        'app_name': re.findall(r"[\w']+|$", app_fullname)[0], # first word
        'app_fullname': app_fullname,
        'app_id': app_id,
        'platform': platform,
        'scraping_timestamp': datetime.now().replace(microsecond=0).isoformat(' '), # aktuelle Uhrzeit formatiert nach ISO 861
        'app_size': app_size,
        'version': app_version,
        'last_updated': last_updated,
        'downloads_bin': downloads,
        'n_ratings': n_ratings,
        'average_rating': avg_rating
    }

rows = []
for url in [url for store in urls for url in urls[store]]:
    r = requests.get(url)
    soup = BeautifulSoup(r.text, 'html.parser')

    rows.append(extract_from_soup(soup, url))

out_path = 'app_results.csv'
df = pd.DataFrame(rows)
df.to_csv(out_path, 
    index = False,
    mode = 'a',
    header = not os.path.exists(out_path)) # add header only if file didn't exist before