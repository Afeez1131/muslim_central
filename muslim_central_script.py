import requests
import urllib3
import shutil
from selenium import webdriver
from bs4 import BeautifulSoup
import os, sys, re, time
import errno
from tqdm import trange, tqdm

def make_folder(title, name):
	folder_name = str(title).strip('\n') + name 
	try:
		os.mkdir(folder_name)
	except OSError as e:
		if e.errno == errno.EEXIST:
			print('Directory not created.')
	else:
		raise e
	return folder_name

def get_javascript(url):
	'''
	turn the source code into beautiful soup object and return the beautiful soup object
	'''
	driver = webdriver.PhantomJS()
	driver.get(url)
	soup = BeautifulSoup(driver.page_source, features='lxml')
	return soup 

def find_para(soup_content):
	'''
	Get the argument of the beautiful soup object, then  get the title, name and url_list from it, and return title, name, url_list, folder_name
	'''
	url_list = []
	title = soup_content.find('h1', class_='page-title').text
	name = (soup_content.find('div', class_='taxonomy-description')).find('a').text
	url_class = soup_content.find(class_='clusterize-content')

	folder_name = make_folder(title, name)

	for html_url in url_class:
		if 'clusterize-bottom-space' not in str(html_url):
			# regex = r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+.mp3'
			url = re.findall(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+.mp3', str(html_url))
			url_list.append(url[0])
		else:
			continue

	return title, name, url_list, folder_name
# title, name, url_list, folder_name = (find_para(get_javascript('https://muslimcentral.com/series/bilal-ismail-yassarnal-quran/')))
def download(url_list, folder_name):
	'''
	get the url list and loop through them, using the folder, name joined together with the file_name gotten from the url_list object and then download each file.
	'''
	http = urllib3.PoolManager()
	for url in url_list:
		# print(url)
		for ch in url.split('/'):
			if ch.endswith('.mp3'):
				mp3_name = ch
		
				file_path = os.path.join(folder_name, mp3_name)

				response = requests.get(url, stream=True)
				size = int(response.headers.get('content-length'))
				block_size = 1024
				print('\nDownloading:', mp3_name)
				progress_bar = tqdm(total=size, unit='iB', unit_scale=True)

				with http.request('GET', url, preload_content=False) as r, open(file_path, 'wb') as out_file:
					for data in response.iter_content(block_size):
						progress_bar.update(len(data))
						shutil.copyfileobj(r, out_file)
					progress_bar.close()

# print(download(url_list, folder_name))
def main():
	if len(sys.argv) > 1 :
	      url = sys.argv[1]
	else :
		url = input('Enter URL > ')
	soup = get_javascript(url)
	title, name, url_list, folder_name = find_para(soup)
	download(url_list, folder_name)

if __name__== '__main__':
	main()