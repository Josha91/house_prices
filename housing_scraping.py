"""
Get information on house listings (both buy and rent) in 
Heidelberg, Germany.

Output: 
.csv file with:
-- house size
-- house price
-- location
-- building year (if available)
-- Energy label (if available)
-- Energy usage (if available)
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import IPython
import numpy as np
import matplotlib.pyplot as plt 
from selenium.webdriver import Chrome, Firefox
from selenium.webdriver.common.keys import Keys
import time
import re

def get_house_info(url):
	result = requests.get(url)
	src = result.text
	soup = BeautifulSoup(src,'lxml')

	df = {}

	loc = soup.find('div',class_='location').text
	loc = re.search('\n(.*)\n(.*)',loc).group(1)
	postcode = int(loc.split()[0])
	df['location'] = loc
	df['postcode'] = postcode

	hardfacts = soup.find_all('div',class_='hardfact')
	df['price'] = int(hardfacts[0].text.split()[0].replace('.',''))
	df['price unit'] = hardfacts[0].text.split()[1]
	df['price description'] = re.search('\n(.*)\n',hardfacts[0].findChild('div',class_='hardfactlabel').text).group(1).lstrip()

	df['size'] = float(hardfacts[1].text.split()[0].replace(',','.'))
	df['size unit'] = hardfacts[1].text.split()[1]

	df['rooms'] = float(hardfacts[2].text.split()[0].replace(',','.'))

	try: #Usually not available for rentals
		for lab in soup.find_all('span',class_='datalabel'):
			if lab.text == 'Energieeffizienzklasse':
				df['Energy label'] = lab.findNext().text
	except:
		df['Energy label'] = " "

	try:
		for lab in soup.find_all('span',class_='datalabel'):
			if lab.text == 'Endenergieverbrauch':
				tmp = lab.findNext().text.split()
				df['Final energy usage'] = float(tmp[0].replace(',','.'))
				df['Energy usage unit'] = tmp[1]
	except:
		df['Final energy usage'] = np.nan
		df['Energy usage unit'] = " "

	try:
		t.findChildren('div',class_="section_content iw_right")
		j = t.findChildren('div',class_="section_content iw_right")
		df['Building year'] = int(j[2].text.split()[1])
	except:
		df['Building year'] = np.nan

	return pd.Series(df)
	#Other thigns to get:
	#Kaltmiete?
	#Nebenkosten
	#Heizkosten
	#Kaution

	#Baujahr
	#Extra stuff - bath? etc. 

	#UMGEBUNGSINFOS!!! THAT'S AN IMPORTANT ONE. 

	#Stadtteil rating

def get_page(page,browser=None):
	base_url = 'https://www.immowelt.de'
	link = lambda x: 'https://www.immowelt.de/liste/heidelberg/wohnungen?cp=%d'%x
	if browser is None:
		browser = Firefox(executable_path='/Users/houdt/Downloads/geckodriver')#executable_path='/Users/houdt/Downloads/geckodriver')#webdriver.Firefox()
	browser.get(link(page))
	time.sleep(2) #time to load

	no_of_pagedowns = 10
	for _ in range(no_of_pagedowns):
		elem = browser.find_element_by_tag_name("body")
		elem.send_keys(Keys.PAGE_DOWN)
		time.sleep(0.2)

	html = browser.page_source
	soup = BeautifulSoup(html,'html.parser')

	listings = soup.find_all('div',class_="listitem clear relative js-listitem ")
	hrefs = []
	for l in listings:
		hrefs.append(base_url+l.findChild('a')['href'])
	return hrefs

def get_listings():
	link = lambda x: 'https://www.immowelt.de/liste/heidelberg/wohnungen?cp=%d'%x
	page = 1

	browser = Firefox(executable_path='/Users/houdt/Downloads/geckodriver')

	all_listings = []
	for page in range(1,7):
		all_listings += get_page(page,browser)

	browser.quit()

	IPython.embed()
	data = [get_house_info(listing) for listing in all_listings] #pd Series
	data = pd.concat(data)
	data.to_csv('housing_heidelberg')
	print('All done!')

if __name__ == "__main__":
	get_listings()
#	get_house_info('https://www.immowelt.de/expose/2v8pj4m')


