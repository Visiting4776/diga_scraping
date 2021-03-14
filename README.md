Setup:

1) Eine virtuelle Umgebung erstellen, in den die Pakete installiert werden: https://docs.python.org/3/library/venv.html
2) Diese virtuelle Umgebung aktivieren. In macOS/UNIX z.B. via `source <pfad_zum_environment>/bin/activate`
3) Die Pakete aus requirements.txt installieren: `python3 -m pip install -r requirements.txt`
4) Um die Crawling-Skripte auszuführen: `scrapy crawl [itunes|googleplay]`
5) Die Ergebnisse sollten in results.csv erscheinen. Falls diese Datei noch nicht existiert, wird sie erstellt.
6) Die Apps, die gecrawlt werden sollen, sind in den jeweiligen Dateien (`appscraper/spiders/xyz_spider.py`) in der Liste `start_urls` angegeben