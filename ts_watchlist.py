import requests
import json

td_key = '3FNC1AKHGOYAXNRVCTNPAIX7TG9Y2MVG'

endpoint = 'https://api.tdameritrade.com/v1/marketdata/{stock_ticker}/quotes?'

full_url = endpoint.format(stock_ticker='AAL')

page = requests.get(url=full_url,
                    params={'apikey' : td_key})

content = json.loads(page.content)

print(content)

watchlist = 'https://api.tdameritrade.com/v1/accounts/{accountId}/watchlists/{watchlistId}'