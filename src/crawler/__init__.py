import bs4
import urllib.request
import urllib.error
import urllib.parse
import crawler.config as config
import http.client
import re

"""
-detectDomain
parseRobotsTxt
isDownloadAllowed
-downloadPage
-detectEncoding
-readTitle
-readLinks
	detectLocalLinks
	detectForeignLinks
readImages
readflash
readvideos
extractText
classifyText
updateClassificationStatistics
"""

		




def detectdomain(httpresponse):
	responseurl = urllib.parse.urlparse(httpresponse.geturl())
	return responseurl.netloc

def readtext(soup):
	ptags = soup.find_all('p')

	if not ptags:
		return ()
		
	plen = []
	mean = 0
	for ptag in ptags:
		l = len(str(ptag.get_text()))
		plen.append(l)
		mean += l

	mean = mean/len(ptags)

	for i in range(len(ptags)-1, 0, -1):
		if plen[i] < 0.8 * mean:
			del ptags[i]

	parentcount = {}
	for ptag in ptags:
		if not ptag.parent in parentcount:
			parentcount[ptag.parent] = 0
		parentcount[ptag.parent] += 1

	maxk = None
	maxv = 0
	for k in parentcount:
		v = parentcount[k]
		if v > maxv:
			maxv = v
			maxk = k

	if maxk:
		return maxk.children

	return () 

def readlinkshref(soup):
	hrefs = []
	tags = soup.find_all('a', href=True)
	
	for tag in tags:
		hrefs.append(tag.get('href'))

	return hrefs

def readimagessrc(soup):
	srcs = []
	imgs = soup.find_all('img', src=True)
	for img in imgs:
		srcs.append(img.get('src'))

	return srcs

def readlinks(soup, domain):
	links = []
	tags = soup.find_all('a', href=True)
	
	for tag in tags:
		link = Link.parse(tag, domain)
		links.append(link)

	return links 

def readtitle(soup):
	return soup.title.string.strip()

def handlecharset(httpmsg, data):
	assert(type(httpmsg) == http.client.HTTPMessage)

	charset = httpmsg.get_content_charset()
	if charset:
		try:
			return data.decode(charset)
		except Exception:
			pass

	pattern = '<meta.*charset\s*=\s*[\'"]?\s*([\w-]+)\s*[\'"]?'
	result = re.search(pattern, str(data), re.IGNORECASE)
	if result:
		charset = result.group(1).lower()
		try:
			return data.decode(charset)
		except Exception:
			pass

	return data.decode('iso-8859-1', 'ignore')

def download(url):
	headers = {
		'User-Agent': config.USERAGENT
	}

	if re.match('^\w+://', url):
		if url.startswith('http://') or url.startswith('https://'):
			parsedurl = urllib.parse.urlparse(url, 'http')
		else:
			return None, None
	else:
		parsedurl = urllib.parse.urlparse('http://' + url)

	request = urllib.request.Request(
			parsedurl.geturl(),
			headers=headers)

	try:
		return request, urllib.request.urlopen(request, timeout=5)
	except Exception as ex:
		try:
			print('falhou ' + parsedurl.geturl())
		except:
			print('falhou')
		return None, None

def load(url):
	request, response = download(url)

	if response == None:
		return None, None, None, None

	if not 200 <= response.status < 400:
		return None, None, None, None

	try:
		data = response.read()
	except:
		return None, None, None, None

	if response.info().get_content_type().startswith('text/'):
		data = handlecharset(response.info(), data)
		return request, response, data, bs4.BeautifulSoup(data)
	else:
		return request, response, data, None
