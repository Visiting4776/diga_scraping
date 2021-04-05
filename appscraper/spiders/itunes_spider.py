import scrapy
import csv
import os
import unicodedata
from datetime import datetime
from collections import OrderedDict
from termcolor import cprint

class ITunesSpider(scrapy.Spider):
    name = "itunes"
    DEFAULT_NA = 'N/A'

    OUT_FILE = 'results.csv'
    OUT_FILE_REVIEWS = 'reviews.csv'

    appstore_name = 'Apple App Store'
    start_urls = [
        'https://apps.apple.com/de/app/invirto/id1482760714',
        'https://apps.apple.com/de/app/id1511739470',
        'https://apps.apple.com/de/app/kalmeda-mynoise/id1437379931',
        'https://apps.apple.com/de/app/rehappy/id1357107437',
        'https://apps.apple.com/de/app/vivira-r%C3%BCcken-knie-und-h%C3%BCfte/id1093858117',
        'https://apps.apple.com/de/app/somnio/id1523016446',
        'https://apps.apple.com/de/app/zanadio/id1499824614'
    ]

    def parse(self, response):
        print(f"Parsing {response.url}... ", end='')

        app_id = response.url.split("/")[-1] # letzter Bestandteil der URL

        app_fullname = response.css('.product-header__title::text').get().strip() 
            #get() statt getall() liefert nur das erste Ergebnis statt einer Liste
            #strip() <- entfernt whitespace links und rechts

        appsize_text = response.css('.information-list--app > .information-list__item:nth-child(2) > .information-list__item__definition::text').get()
        app_size = self.DEFAULT_NA # default wert, falls das Extrahieren nicht geklappt hat und appsize_text somit 'null' ist
        if appsize_text:
            app_size = unicodedata.normalize('NFKD', appsize_text) # convert '\xa0' to ' '
        
        #ratings_text = response.xpath("//div[@data-test-rating-count]/text()").get()
        ratings_text = response.css('.we-customer-ratings__count::text').get()
        n_ratings_total = self.DEFAULT_NA
        if ratings_text:
            n_ratings_total = int(ratings_text.split()[0])

        #app_version_text = response.xpath("//p[@data-test-version-number]/text()").get() #outdated!
        app_version_text = response.css('.whats-new__latest__version::text').get()
        app_version = self.DEFAULT_NA
        if app_version_text:
            app_version = app_version_text.split()[-1]

        last_updated_text = response.xpath("//time[@data-test-we-datetime]/text()").get()
        last_updated = self.DEFAULT_NA
        if last_updated_text:
            d = datetime.strptime(last_updated_text, '%d.%m.%Y')
            last_updated = d.strftime('%Y-%m-%d') # Datum in besseres Format umwandeln
            
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
            ('downloads_bin', self.DEFAULT_NA),
            ('average_rating', response.css("span.we-customer-ratings__averages__display::text").get() or self.DEFAULT_NA)
        ])

        if not ratings_text:
            # das parsen der Gesamtbewertungen schlug fehl,
            # deshalb hier schon abbrechen und nicht noch
            # die Balkenlängen auswerten
            for i in range(5):
                details[f'n_ratings_{5-i}'] = self.DEFAULT_NA
            details['average_rating_calculated'] = self.DEFAULT_NA
            self.add_details_to_csv(details, OUT_FILE)
            cprint("Done!", 'green')
            return

        # die Anzahl einzelner Bewertungen von 1-5 Sternen wird nur in Form der Länge eines 
        # Balkens dargestellt, und könnte daher bei größeren Bewertungen etwas ungenau sein
        # die Gesamtanzahl aller Bewertungen sowie die Durchschnittsbewertung sind nicht betroffen
        rating_sum = 0
        for i in range(5): #i=0,1,2,3,4
            element = response.css('.we-star-bar-graph__bar__foreground-bar')[i].get()
            bar_width = float(element.split('%')[0].split()[-1])
            n_ratings = bar_width / 100 * n_ratings_total # divide by 100 to get percentage
            n_ratings = int(round(n_ratings)) # zur nächsten ganzen Zahl auf- oder abrunden

            rating_sum += (5-i)*n_ratings
            details[f'n_ratings_{5-i}'] = n_ratings

        details['average_rating_calculated'] = round(rating_sum / float(n_ratings_total), 1)
        
        self.add_details_to_csv(details, OUT_FILE)
        cprint("Done!", 'green')

    def parse_reviews(self, response):
        #in separate CSV: platform, app, rating, date, title, text
        pass

    def add_details_to_csv(self, details, filename):
        #add a new row to the CSV file. 

        self.log(f'Parsed {details}')

        #filepath = os.path.join('..', filename)
        # create CSV file with head if it doesn't exist yet
        
        header_row = ', '.join(details.keys()) + '\n'
        if not os.path.exists(filename):
            with open(filename, 'w') as f:
                f.write(header_row)
            print(filename + " has been created.")
        
        if 0 == os.path.getsize(filename): # Datei existiert, ist aber leer -> Header-Zeile schreiben
            with open(filename, 'w') as f:
                f.write(header_row)

        # add the new row to the CSV file:
        with open(filename, 'a') as csv_file:
            csv_file.write(', '.join([str(val) for val in details.values()]) + '\n')
            # each value must be converted to string first (some are numbers)
