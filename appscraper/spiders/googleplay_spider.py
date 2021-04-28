'''
DEPRECATED IN FAVOUR OF scrape_appstores.py!
'''

import scrapy
import pandas as pd
import csv
import os
import unicodedata
import locale
from datetime import datetime
from collections import OrderedDict
from termcolor import cprint

class GPlaySpider(scrapy.Spider):
    name = "googleplay"
    DEFAULT_NA = 'N/A'
    OUT_FILE = 'results2.csv'

    appstore_name = 'Google Play Store'
    start_urls = [
        'https://play.google.com/store/apps/details?id=com.sympatient.invirto',
        'https://play.google.com/store/apps/details?id=com.newsenselab.android.m_sense_migraine',
        'https://play.google.com/store/apps/details?id=de.mynoise.kalmeda',
        'https://play.google.com/store/apps/details?id=de.rehappy.app.rehappy',
        'https://play.google.com/store/apps/details?id=de.mementor.somnio',
        'https://play.google.com/store/apps/details?id=de.aidhere.zanadio',
        'https://play.google.com/store/apps/details?id=com.vivira.android'
    ]

    # '&hl=gsw' darf nicht Teil der URL sein!!1!.
    # dadurch wird die Deutsche Seite aufgerufen,
    # und die Elemente können nicht gefunden werden.
    # weil hier nicht nach Element-IDs gesucht wird
    # (wie beim App Store), sondern nach spezifischen
    # Wörtern wie "size" etc

    def parse(self, response):
        print(f"Parsing {response.url}... ", end='')

        app_id = response.url.split("?id=")[-1].split('&')[0] # hinter '?id=', und ggf. vor '&'

        app_fullname = response.css('h1 span::text').get()
        
        app_size = self.DEFAULT_NA # default wert, falls das Extrahieren nicht geklappt hat und appsize_text somit 'null' ist
        appsize_array = response.xpath("//div[contains(text(), 'Size')]/..//text()").getall() 
        if appsize_array:
            app_size = appsize_array[-1]
        
        n_ratings_total = self.DEFAULT_NA
        cwiz_texts = response.css('c-wiz span span::text').getall()
        # example: ['Apps', 'Movies & TV', 'Books', 'Devices', 'Entertainment', 
        # '24', 'Read more', 'Collapse', '24', 'Read more', 'Collapse', 
        # 'March 4, 2021', '31M', '1,000+', '1.8.5', '6.0 and up', 
        # 'In-App Purchases', '€279.99 per item', 'Google Commerce Ltd']
        cwiz_nums = [int(element) for element in cwiz_texts if element.isdigit()] 
        # only look at such texts that are digits. of those, take the first.
        if cwiz_nums:
            n_ratings_total = cwiz_nums[0]

        app_version_arr = response.xpath("//div[contains(text(), 'Current Version')]/..//text()").getall()
        app_version = self.DEFAULT_NA
        if app_version_arr:
            app_version = app_version_arr[1]

        last_updated = self.DEFAULT_NA
        last_updated_arr = response.xpath("//div[contains(text(), 'Updated')]/..//text()").getall() 
        if last_updated_arr:
            locale.setlocale(locale.LC_ALL, 'en_GB.UTF-8') # muss ggf. an verfügbare locale angepasst werden!
            d = datetime.strptime(last_updated_arr[-1], '%B %d, %Y')
            last_updated = d.strftime('%Y-%m-%d') # Datum in besseres Format umwandeln
        
        avg_rating = self.DEFAULT_NA
        avg_rating_text = response.xpath('//div[@role="img"]/@aria-label').get()
        if avg_rating_text:
            avg_rating = avg_rating_text.split()[1]

        downloads = self.DEFAULT_NA
        downloads_text_arr = response.xpath("//div[contains(text(), 'Installs')]/..//text()").getall()
        if downloads_text_arr:
            downloads = downloads_text_arr[1].replace(',', '.')

        details = OrderedDict([
            ('app_name', app_fullname.split()[0]),
            ('app_fullname', app_fullname),
            ('app_id', app_id[2:]), # die ersten beiden Zeichen sind immer "id", daher die entfernen
            ('platform', self.appstore_name), # Apple App Store
            ('scraping_timestamp', datetime.now().replace(microsecond=0).isoformat(' ')), # aktuelle Uhrzeit formatiert nach ISO 8601
            ('app_size', app_size),
            ('version', app_version),
            ('last_updated', last_updated),
            ('n_ratings', n_ratings_total),
            ('downloads_bin', downloads),
            ('average_rating', avg_rating)
        ])


        # Im Play Store gibt es keine Möglichkeit, die Verteilung der einzelnen Bewertungen
        # herauszufinden (geht scheinbar leider nur bei geschriebenen Rezensionen)
        for i in range(5):
            details[f'n_ratings_{5-i}'] = self.DEFAULT_NA
        details['average_rating_calculated'] = self.DEFAULT_NA
        
        self.add_details_to_csv(details, self.OUT_FILE)
        cprint("Done!", 'green')
        return

    def parse_reviews(self, response):
        #in separate CSV: platform, app, rating, date, title, text
        pass

    def add_details_to_csv(self, details, filename):
        #add a new row to the CSV file. 

        header_row = ', '.join(details.keys()) + '\n'
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write(header_row)
            print(filename + " has been created.")
        
        if 0 == os.path.getsize(filename): # Datei existiert, ist aber leer -> Header-Zeile schreiben
            with open(filename, 'w') as f:
                f.write(header_row)

        # # add the new row to the CSV file:
        # with open(filename, 'a') as csv_file:
        #     csv_file.write(', '.join([str(val) for val in details.values()]) + '\n')
        #     # each value must be converted to string first (some are numbers)

    print("ALL DONE")