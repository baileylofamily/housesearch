
# delete previous venv

rm -rf scraper

# create new venv

python3 -m venv scraper

# go into venv

source scraper/bin/activate

# install Scrapy

pip install Scrapy

# run scraping

scrapy runspider scrape.py

# view index.html
