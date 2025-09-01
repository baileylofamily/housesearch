import datetime
import zoneinfo
import requests
from lxml import html
from selenium import webdriver
from bs4 import BeautifulSoup
import re
import time
import json
import sys
import random

from selenium.webdriver.chrome.options import Options
chrome_options = Options()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--user-agent=Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-blink-features=AutomationControlled")
chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
chrome_options.add_experimental_option('useAutomationExtension', False)

pacific = zoneinfo.ZoneInfo('Canada/Pacific')
now = datetime.datetime.now(pacific)

search_terms = ['https://vancouver.craigslist.org/search/apa?sort=date']
search_terms.append('hasPic=1')
search_terms.append('min_price=3500')
search_terms.append('max_price=5000')
search_terms.append('min_bedrooms=2')
search_terms.append('max_bedrooms=3')
# search_terms.append('min_bathrooms=2')
search_terms.append('minSqft=900')
search_terms.append('maxSqft=2000')
search_terms.append('lat=49.2529')
search_terms.append('lon=-123.127')
search_terms.append('search_distance=2') # miles

base_url = '&'.join(search_terms)

location_regions = []

location_regions.append((49.2695, -123.1365, 49.2324, -123.1134, 1)) # oakridge area
location_regions.append((49.2575, -123.1580, 49.2341, -123.1310, 2)) # kerrisdale area
location_regions.append((49.2722, -123.1162, 49.2687, -123.1007, 3)) # olympic village area

# Create a session with realistic headers to avoid being detected as a bot
session = requests.Session()
session.headers.update({
    'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'Accept-Language': 'en-US,en;q=0.9',
    'Accept-Encoding': 'gzip, deflate, br',
    'DNT': '1',
    'Connection': 'keep-alive',
    'Upgrade-Insecure-Requests': '1'
})

furnished_ids = []
unfurnished_ids = {}

def respectful_delay():
    """Add a random delay between 1-3 seconds to be respectful to the server"""
    delay = random.uniform(1.0, 3.0)
    print(f"Waiting {delay:.1f}s to be respectful...")
    time.sleep(delay)

# driver = webdriver.Firefox()
driver = webdriver.Chrome(options=chrome_options)

# Make browser less detectable
driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
driver.execute_cdp_cmd('Network.setUserAgentOverride', {
    "userAgent": 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
})

def search(is_furnished):
    for page in range(10):
        url = base_url
        if is_furnished:
            url = f'{url}&is_furnished=1'
        url = f'{url}#search=1~list~{page}~0'

        print(f'url = {url}')

        print("Loading search page...")
        driver.get(url)

        # Wait for page to load
        time.sleep(5)
        print("Page loaded, parsing content...")

        soup = BeautifulSoup(driver.page_source, "html.parser")

        # Check if we got blocked
        if "blocked" in driver.page_source.lower() or "your request has been blocked" in driver.page_source.lower():
            print("⚠️  DETECTED: Request has been blocked by Craigslist!")
            print("This is normal when scraping. The block is usually temporary.")
            print("Consider:")
            print("1. Waiting a few hours before trying again")
            print("2. Using a VPN to change IP address")
            print("3. Running smaller batches with longer delays")
            return []

        elements = soup.find_all('div', class_='cl-search-result')

        print('Elements: ', len(elements))

        # Extract href and id from each search result
        for element in elements:
            link = element.find('a', href=True)
            if link:
                href = link['href']
                print(f"Found href: {href}")
                match = re.search('/([0-9]+)\.html', href)
                if match:
                    id = match.groups()[0]
                    print(f"Extracted ID: {id}")
                    yield (href, id)
                else:
                    print(f"No ID found in href: {href}")
            else:
                print("No link found in element")

        # If no elements found, let's debug the page structure
        if len(elements) == 0:
            print("No cl-search-result elements found. Let's check what's actually on the page:")
            all_lis = soup.find_all('li')
            print(f"Total <li> elements found: {len(all_lis)}")
            for i, li in enumerate(all_lis[:5]):  # Show first 5 li elements
                print(f"Li {i}: class='{li.get('class')}', content preview: {str(li)[:100]}...")

            # Also check for any links
            all_links = soup.find_all('a', href=True)
            print(f"Total <a> elements with href found: {len(all_links)}")
            for i, link in enumerate(all_links[:3]):  # Show first 3 links
                print(f"Link {i}: href='{link['href']}'")

for (_, id) in search(is_furnished=True):
    furnished_ids.append(id)

for (href, id) in search(is_furnished=False):
    if id not in furnished_ids:
        print(f'[{id}] Unfurnished')
        unfurnished_ids[id] = href
    else:
        print(f'[{id}] Furnished')

print(f'Furnished Items: {len(furnished_ids)}')
print(f'Unfurnished Items: {len(unfurnished_ids)}')

driver.quit()

script_file = open('website/index.js', 'w')
script_file.write('// Initialize Google Maps\n')
script_file.write('function initMap() {\n')
script_file.write('  const vancouver = { lat: 49.25, lng: -123.139 };\n')
script_file.write('  const map = new google.maps.Map(document.getElementById("map"), { zoom: 13, center: vancouver });\n')
script_file.write('\n')
script_file.write('  // Add hard-coded blue markers\n')
script_file.write('  const manualPos1 = { lat: 49.228, lng: -123.119 };\n')
script_file.write('  const manualMarker1 = new google.maps.Marker({position: manualPos1, map: map, icon: "https://raw.githubusercontent.com/Concept211/Google-Maps-Markers/master/images/marker_blue1.png"});\n')
script_file.write('  const manualPos2 = { lat: 49.236260, lng: -123.123232 };\n')
script_file.write('  const manualMarker2 = new google.maps.Marker({position: manualPos2, map: map, icon: "https://raw.githubusercontent.com/Concept211/Google-Maps-Markers/master/images/marker_blue2.png"});\n')
script_file.write('\n')

index_file = open('website/index.html', 'w')
index_file.write('<!DOCTYPE html>\n')
index_file.write('<html lang="en">\n')
index_file.write('<head>\n')
index_file.write('<link rel="icon" type="image/png" href="https://baileylofamily.github.io/housesearch/home_128.png">\n')
index_file.write('<link rel="apple-touch-icon" type="image/png" href="https://baileylofamily.github.io/housesearch/home_128.png">\n')
index_file.write('<script src="https://polyfill.io/v3/polyfill.min.js?features=default"></script>\n')
index_file.write('<link rel="stylesheet" type="text/css" href="./style.css" />\n')
index_file.write('<script src="./index.js"></script>\n')
index_file.write('<title>House Search</title>\n')
index_file.write('</head>\n')
index_file.write('<body>\n')
index_file.write('<header><h1>House Search</h1></header>\n')
index_file.write('<p></p>\n')
index_file.write('<div id="map"></div>\n')
index_file.write('<p></p>\n')

index_file.write('<ol>\n')

queries = len(unfurnished_ids)

def add_listings(show_apartments=False):
    # Limit to first 50 listings to be respectful to the server
    MAX_LISTINGS = 5000

    items = 1
    processed = 0

    for (id, href) in unfurnished_ids.items():
        if processed >= MAX_LISTINGS:
            print(f"\n⚠️  Reached maximum of {MAX_LISTINGS} listings to be respectful to the server")
            print("To process more listings, wait a few hours and run again")
            break

        processed += 1
        print(f"Processing listing {id}...")

        # Add respectful delay before each request
        respectful_delay()

        try:
            listing = session.get(href, timeout=10)
            if listing.status_code == 403:
                print(f"[{id}] Request blocked (403), skipping to avoid further blocks")
                continue
            elif listing.status_code != 200:
                print(f"[{id}] HTTP {listing.status_code}, skipping")
                continue
        except requests.exceptions.RequestException as e:
            print(f"[{id}] Request failed: {e}, skipping")
            continue

        soup = BeautifulSoup(listing.content, "html.parser")

        price_element = soup.find('span', class_='price')
        if not price_element:
            print(f"[{id}] No price found, skipping")
            continue
        price = price_element.get_text()

        housing_element = soup.find('span', class_='housing')
        if not housing_element or '-' not in housing_element.get_text():
            print(f"[{id}] No housing area found, skipping")
            continue
        area = housing_element.get_text().split('-')[1].strip()

        element = soup.find('script', id='ld_posting_data')

        contents = json.loads(element.get_text())

        title = contents['name']
        type = contents['@type']
        bedrooms = contents['numberOfBedrooms']
        try:
            bathrooms = contents['numberOfBathroomsTotal']
        except KeyError:
            bathrooms = '?'
        latitude = float(contents['latitude'])
        longitude = float(contents['longitude'])

        if type.lower() == 'apartment' and show_apartments == False:
            print(f'[{id}] Ignoring Apartment')
            continue
        if type.lower() != 'apartment' and show_apartments == True:
            print(f'[{id}] Ignoring House')
            continue

        region = None

        for (lat1, long1, lat2, long2, region_id) in location_regions:
            if latitude <= lat1 and latitude > lat2 and longitude >= long1 and longitude < long2:
                region = region_id
                break

        if not region:
            print(f'[{id}] Outside Zone Of Interest')
            continue
        else:
            print(f'[{id}] Inside Zone Of Interest')

        len(soup.find_all('a', class_='manga_img'))
        elements = soup.find_all('time', class_="date timeago")
        print(f'[{id}] Elements {elements}')
        recent_seconds = 3600 * 24 * 30 # 1 month ago
        print(f'[{id}] Recent Seconds {recent_seconds}')

        # Store the datetime attribute for relative time calculation
        datetime_for_display = None

        for element in elements:
            # Get the datetime attribute for filtering
            posted_time_str = element.get_text().strip()
            posted_time = datetime.datetime.strptime(posted_time_str, "%Y-%m-%d %H:%M").replace(tzinfo=pacific)
            seconds = (now - posted_time).total_seconds()
            if seconds < recent_seconds:
                recent_seconds = seconds

            # Get the datetime attribute for display (use the first one found)
            if datetime_for_display is None:
                datetime_attr = element.get('datetime')
                if datetime_attr:
                    # Parse the ISO format datetime (e.g., "2025-08-28T17:49:11-0700")
                    try:
                        datetime_for_display = datetime.datetime.fromisoformat(datetime_attr.replace('Z', '+00:00'))
                        if datetime_for_display.tzinfo is None:
                            datetime_for_display = datetime_for_display.replace(tzinfo=pacific)
                    except ValueError:
                        # Fallback to text content if datetime attribute parsing fails
                        datetime_for_display = posted_time
        # ignore if posting is older than seven days
        if recent_seconds > 3600 * 24 * 3:
            print(f'[{id}] Old Post')
            continue
        else:
            print(f'[{id}] New Post')

        # Calculate relative time using the datetime attribute for display
        if datetime_for_display:
            display_seconds = (now - datetime_for_display).total_seconds()
            if display_seconds < 3600:
                relative_time = '< 1 hour'
            else:
                relative_time = '%s hours' % int(display_seconds / 3600)
        else:
            # Fallback to recent_seconds if no datetime attribute found
            relative_time = ''
            if recent_seconds < 3600:
                relative_time = '< 1 hour'
            else:
                relative_time = '%s hours' % int(recent_seconds / 3600)

        print(f'[{id}] Adding Listing - {title}')

        index_file.write('<li>\n')
        index_file.write(f'<a href="{href}">{id}</a>\n')
        index_file.write(f'<span font-weight:bold">{price}</span>\n')
        index_file.write('<span>\n')
        index_file.write(f'({area} {bedrooms}bed {bathrooms}bath) - {title[:20]}... \n')
        index_file.write('</span>\n')
        index_file.write(f' [{relative_time}]\n')
        index_file.write('</li>\n')
        index_file.write('</br>\n')

        # Generate marker for ALL listings (both houses and apartments)
        script_file.write(f'const pos{id}_{items} = {{ lat: {latitude}, lng: {longitude} }};\n')

        # Use red markers for houses, yellow markers for apartments
        if type.lower() == 'apartment':
            script_file.write(f'const marker{id}_{items} = new google.maps.Marker({{position: pos{id}_{items}, map: map, icon: "https://raw.githubusercontent.com/Concept211/Google-Maps-Markers/master/images/marker_yellow{items}.png"}});\n')
        else:
            script_file.write(f'const marker{id}_{items} = new google.maps.Marker({{position: pos{id}_{items}, map: map, icon: "https://raw.githubusercontent.com/Concept211/Google-Maps-Markers/master/images/marker_red{items}.png"}});\n')

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

# Load Google Maps API after the JavaScript file to ensure initMap is defined
index_file.write('<script src="https://maps.googleapis.com/maps/api/js?key=AIzaSyAePfX-nxnVhshl1eKbg_MVdntdTkhTEdk&callback=initMap&v=weekly" defer></script>\n')
index_file.write('</body>\n')
index_file.write('</html>\n')
index_file.close()

# Properly close the initMap function and expose it globally
script_file.write('}\n')
script_file.write('\n')
script_file.write('// Expose initMap globally for Google Maps API callback\n')
script_file.write('window.initMap = initMap;\n')
script_file.close()
