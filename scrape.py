import datetime
import zoneinfo
import requests
from lxml import html
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time
import json

from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")

pacific = zoneinfo.ZoneInfo('Canada/Pacific')
now = datetime.datetime.now(pacific)

search_terms = ['https://vancouver.craigslist.org/search/apa?sort=date']
search_terms.append('hasPic=1')
search_terms.append('min_price=3700')
search_terms.append('max_price=6200')
search_terms.append('min_bedrooms=2')
search_terms.append('max_bedrooms=4')
# search_terms.append('min_bathrooms=2')
search_terms.append('minSqft=900')
search_terms.append('maxSqft=3000')
# search_terms.append('lat=49.2479')
# search_terms.append('lon=-123.1739')
# search_terms.append('search_distance=4.9') # miles

base_url = '&'.join(search_terms)

location_regions = []
location_regions.append((49.3, -123.3, 49.2, -123.055, 1))

# location_regions.append((49.29, -123.3, 49.2, -123.177, 1))
# location_regions.append((49.296, -123.095, 49.229, -123.0357, 3))
# location_regions.append((49.27049, -123.177, 49.2, -123.076, 2))
# location_regions.append((49.279, -123.177, 49.27049, -123.1388, 2))
# location_regions.append((49.2759, -123.1388, 49.27049, -123.1324, 2))
# location_regions.append((49.27266, -123.11738, 49.27049, -123.095, 2))
# location_regions.append((49.4, -123.129, 49.295, -122.93, 4))
# location_regions.append((49.4, -123.3, 49.298, -123.129, 5))
# location_regions.append((49.31, -123.17, 49.26, -123.09, 6))

furnished_ids = []
unfurnished_ids = {}

# driver = webdriver.Firefox()
driver = webdriver.Chrome(options=chrome_options)

def search(is_furnished):
    for page in range(10):
        url = base_url
        if is_furnished:
            url = f'{url}&is_furnished=1'
        url = f'{url}#search=1~list~{page}~0'

        print(f'url = {url}')

        driver.get(url)

        time.sleep(5)

        soup = BeautifulSoup(driver.page_source, "html.parser")

        elements = soup.find_all('a', class_='titlestring', href=True)

        for element in elements:
            href = element['href']
            match = re.search('/([0-9]+)\.html', href)
            id = match.groups()[0]
            yield (href, id)

for (_, id) in search(is_furnished=True):
    furnished_ids.append(id)

for (href, id) in search(is_furnished=False):
    if id not in furnished_ids:
        print('f[{id}] Unfurnished')
        unfurnished_ids[id] = href
    else:
        print(f'[{id}] Furnished')

print(f'Furnished Items: {len(furnished_ids)}')
print(f'Unfurnished Items: {len(unfurnished_ids)}')

driver.quit()

script_file = open('website/index.js', 'w')
script_file.write('function initMap() {\n')
script_file.write('const vancouver = { lat: 49.25, lng: -123.15 };\n')
script_file.write('const map = new google.maps.Map(document.getElementById("map"), { zoom: 12, center: vancouver, });\n')

index_file = open('website/index.html', 'w')
index_file.write('<head>\n')
index_file.write('<link rel="icon" type="image/png" href="https://baileylofamily.github.io/housesearch/home_128.png">\n')
index_file.write('<link rel="apple-touch-icon" type="image/png" href="https://baileylofamily.github.io/housesearch/home_128.png">\n')
index_file.write('<script src="https://polyfill.io/v3/polyfill.min.js?features=default"></script>\n')
index_file.write('<link rel="stylesheet" type="text/css" href="./style.css" />\n')
index_file.write('<script type="module" src="./index.js"></script>\n')
index_file.write('<title>House Search</title>\n')
index_file.write('<header><h1>House Search</h1></header>\n')
index_file.write('</head>\n')
index_file.write('<body>\n')
index_file.write('<p></p>\n')
index_file.write('<div id="map"></div>\n')
index_file.write('<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAI95bvyZO7clR-Lldk_Z46CrS9UyI4N9I&callback=initMap&v=weekly" defer></script>\n')
index_file.write('<p></p>\n')

index_file.write('<ol>\n')

queries = len(unfurnished_ids)

def add_listings(show_apartments=False):

    items = 1

    for (id, href) in unfurnished_ids.items():
        listing = requests.get(href)

        soup = BeautifulSoup(listing.content, "html.parser")

        price = soup.find('span', class_='price').get_text()
        area = soup.find('span', class_='housing').get_text().split('-')[1].strip()

        element = soup.find('script', id='ld_posting_data')

        contents = json.loads(element.get_text())

        title = contents['name']
        type = contents['@type']
        bedrooms = contents['numberOfBedrooms']
        bathrooms = contents['numberOfBathroomsTotal']
        latitude = float(contents['latitude'])
        longitude = float(contents['longitude'])

        if type.lower() == 'apartment' and show_apartments == False:
            continue
        if type.lower() != 'apartment' and show_apartments == True:
            continue

        region = None

        for (lat1, long1, lat2, long2, region_id) in location_regions:
            if latitude <= lat1 and latitude > lat2 and longitude >= long1 and longitude < long2:
                region = region_id
                break
        
        if not region:
            print(f'[{id}] Outside Zone Of Interest')
            continue

        len(soup.find_all('a', class_='manga_img'))
        elements = soup.find_all('time', class_="date timeago")
        recent_seconds = 3600 * 24 * 30 # 1 month ago
        for element in elements:
            posted_time_str = element.get_text().strip()
            posted_time = datetime.datetime.strptime(posted_time_str, "%Y-%m-%d %H:%M").replace(tzinfo=pacific)
            seconds = (now - posted_time).total_seconds()
            if seconds < recent_seconds:
                recent_seconds = seconds
        # ignore if posting is older than seven days
        if recent_seconds > 3600 * 24 * 7:
            print(f'[{id}] Old Post')
            continue

        relative_time = ''
        if recent_seconds < 3600:
            relative_time = '< 1 hour'
        else:
            relative_time = '%s hours' % int(recent_seconds / 3600)

        print(f'Adding Listing - {title}')

        index_file.write('<li>\n')
        index_file.write(f'<a href="{href}">{id}</a>\n')
        index_file.write(f'<span font-weight:bold">{price}</span>\n')
        index_file.write('<span>\n')
        index_file.write(f'({area} {bedrooms}bed {bathrooms}bath) - {title[:20]}... \n')
        index_file.write('</span>\n')
        index_file.write(f' [{relative_time}]\n')
        index_file.write('</li>\n')
        index_file.write('</br>\n')

        if show_apartments == False:
            script_file.write(f'const pos{items} = {{ lat: {latitude}, lng: {longitude} }};\n')
            script_file.write(f'const marker{items} = new google.maps.Marker({{position: pos{items}, map: map, icon: "https://raw.githubusercontent.com/Concept211/Google-Maps-Markers/master/images/marker_red{items}.png"}});\n')

        items += 1

        time.sleep(1)

index_file.write('<h1>Houses</h1>\n')
add_listings(False)
index_file.write('<h1>Apartments</h1>\n')
add_listings(True)

index_file.write('</ol>\n')
index_file.write('<p></p>\n')
now = datetime.datetime.now(pacific)
time_str = now.strftime('%X %x %Z')
index_file.write(f'Filtered {queries} items at {time_str}')
index_file.write('</body>\n')
index_file.close()

script_file.write('}\n')
script_file.write('window.initMap = initMap;\n')
script_file.close()
