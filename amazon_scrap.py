from selectorlib import Extractor
import requests 
import json 
from time import sleep
from re import sub
from decimal import Decimal


# Create an Extractor by reading from the YAML file
e = Extractor.from_yaml_file('amazon_temp.yml')

def scrape(url, page):  
    if page % 5 == 0:
        print('Waiting for 5 sec')
        sleep(5)
    headers = {
        'dnt': '1',
        'upgrade-insecure-requests': '1',
        'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.61 Safari/537.36',
        'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9',
        'sec-fetch-site': 'same-origin',
        'sec-fetch-mode': 'navigate',
        'sec-fetch-user': '?1',
        'sec-fetch-dest': 'document',
        'referer': 'https://www.amazon.eg/',
        'accept-language': 'en-GB,en-US;q=0.9,en;q=0.8',
    }

    # Download the page using requests
    print("Downloading page {}".format(page))
    r = requests.get(url, {'page':page}, headers=headers)
    print(r.url)
    # Simple check to check if page was blocked (Usually 503)
    if r.status_code > 500:
        if "To discuss automated access to Amazon data please contact" in r.text:
            print("Page %s was blocked by Amazon. Please try using better proxies\n"%url)
        else:
            print("Page %s must have been blocked by Amazon as the status code was %d"%(url,r.status_code))
        return None
    # Pass the HTML of the page and create 
    return e.extract(r.text)

final_products = []
url = input("Enter url\n")
x = int(input("Enter page numbers\n"))
for p in range(x):
	data = scrape(url, p+1)
	if data:
            for product in data['products']:
                if product.get('old_price'):
                    old_price = float(Decimal(sub(r'[^\d.]', '', product['old_price'])))
                    new_price = float(Decimal(sub(r'[^\d.]', '', product['new_price'])))
                    discount = int(((old_price - new_price) / old_price ) * 100.0)
                    final_products.append({
                    'product':product['name'],
                    'discount':discount,
                    'price':'new: {} , old: {}'.format(new_price, old_price)
                    })
print(json.dumps(sorted(final_products, key=lambda k: k['discount'], reverse=True), indent=4))