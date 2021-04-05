# TODO
# alles in eine Datei schreiben, dabei Duplikate überspringen
# „"" etc filtern
# Apps ohne Rezensionen ohne Fehler überspringen

import requests
import json
import datetime
import pandas as pd
from time import sleep

AUTH_STR = 'Bearer eyJhbGciOiJFUzI1NiIsInR5cCI6IkpXVCIsImtpZCI6IlU4UlRZVjVaRFMifQ.eyJpc3MiOiI3TktaMlZQNDhaIiwiaWF0IjoxNjE2MDA5OTg1LCJleHAiOjE2MTkwMzM5ODV9.imRWFJ8QhkAfSBJFczXw4wlvsJOTuGuD8Go85hGL9gTmPCWUCktSxdtzpOrMIJGCqhvuSvXvR3Bkatfk8UR8nA'
BASE_URL = "https://amp-api.apps.apple.com{}&platform=web&additionalPlatforms=appletv%2Cipad%2Ciphone%2Cmac"

app_ids = [
    1482760714,
    1511739470,
    1437379931,
    #1357107437,
    1093858117,
    1523016446,
    1499824614,
]

reviews = []

for app_id in app_ids:
    print(f"### {app_id} ###")
    url_piece = f"/v1/catalog/de/apps/{app_id}/reviews?l=de-DE"

    while True:
        response = requests.request(
            method = "GET",
            url = BASE_URL.format(url_piece),
            headers = {'Authorization': AUTH_STR}
        )
        
        response_data = json.loads(response.text)
        
        reviews.extend([
            dict(app_id=app_id, **r['attributes'])
            for r in response_data['data']
        ])

        print(f"{response.url}: {response.status_code}, n={len(reviews)}")

        # break out of the loop if this was the last URL to be requested
        if 'next' not in response_data:
            break
        
        url_piece = response_data['next']

df = pd.DataFrame(reviews)
now = datetime.datetime.now().replace(microsecond=0).isoformat()

# 'developerResponse' ist entweder False oder ein dict, das die Antwort enthält
df['developerResponse'] = df['developerResponse'].apply(lambda cell: '' if pd.isna(cell) else cell['body'])
df.to_pickle(f'itunes-reviews-{now}.pkl')

# Make some changes to dataframe before exporting to csv:
df.replace(to_replace=[r"\\t|\\n|\\r", "\t|\n|\r"], value=[" "," "], regex=True, inplace=True)
df.to_csv(f'itunes-reviews-{now}.csv', index=False)