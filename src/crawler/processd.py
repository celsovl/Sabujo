from crawler.process import ProcessQueue
from crawler.tasks import TaskQueue
import bs4
import crawler
import crawler.db as db
import crawler.images as images
import crawler.urlhelper as urlhelper
import io
import json
import logging
import re
import urllib.parse

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(logging.FileHandler('log.txt', encoding='utf-8'))

allowed_mimes = [
	'image/bmp',
	'image/x-windows-bmp',
	'image/gif',
	'image/x-icon',
	'image/jpeg',
	'image/pjpeg',
	'image/png',
	'text/html',
	'text/plain'
	#'text/xml'
]

class CaseInsensitiveDict(dict):
	def __setitem__(self, key, value):
		super(CaseInsensitiveDict, self).__setitem__(key.lower(), value)

	def __getitem__(self, key):
		return super(CaseInsensitiveDict, self).__getitem__(key.lower())

	def get(self, key, default=None):
		return super(CaseInsensitiveDict, self).get(key.lower(), default)

	@staticmethod
	def fromdict(d):
		tmp = CaseInsensitiveDict()
		for k, v in d.items():
			tmp[k] = v

		return tmp
		
def get_text(el):
	if not el:
		return None

	buf = io.StringIO()
	for s in el.strings:
		if not isinstance(s, bs4.element.Comment):
			buf.write(s)

	return buf.getvalue()

def process_html(url, request, response, data, **kwarg):
	data = str(data, 'utf-8', 'ignore')
	try:
		soup = bs4.BeautifulSoup(data)
	except:
		return

	# remove os scripts, eles só atrapalham
	for script in soup.find_all('script'):
		script.decompose()

	link_url = kwarg['link_url']
	this_domain_id = kwarg['domain_id']
	this_url_id = kwarg['url_id']

	# salva e cria referência para todos os links desta página
	imgs = soup.find_all('img', src=True)
	links = soup.find_all('a', href=True)
	with db.scope():
		for img in imgs:
			img_url = urlhelper.Url.parse(img.get('src'), url)
			img_title = img.get('title')

			domain_id = db.save_domain(img_url.domain)
			url_id = db.save_url(domain_id, img_url.path, None, 2)
			db.associate(this_url_id, url_id, img_title)

		for link in links:
			m = re.match('\s*(\w+):', link.get('href'))
			if m and m.group(1) not in ('http', 'https'):
				continue

			link_text = get_text(link).strip()
			link_url = urlhelper.Url.parse(link.get('href'), url)

			domain_id = db.save_domain(link_url.domain)
			url_id = db.save_url(domain_id, link_url.path, None, None)
			db.associate(this_url_id, url_id, link_text)

		hs = soup.find_all('h1')
		hs += soup.find_all('h2')
		hs += soup.find_all('h3')
		hs += soup.find_all('h4')
		hs += soup.find_all('h5')
		hs += soup.find_all('h6')

		for hx in hs:
			if not hx.a or len(hx.get_text()) > 0 and len(hx.a.get_text())/len(hx.get_text()) < 0.3:
				header_text = get_text(hx).strip()
				db.save_header(this_url_id, header_text)

		output = io.StringIO()
		outputHtml = io.StringIO()
		text_elements = crawler.readtext(soup)

		for el in text_elements:
			if isinstance(el, bs4.NavigableString):
				outputHtml.write(str(el) + '\n')
				output.write(el)
			elif not el.a or len(el.get_text()) > 0 and len(el.a.get_text())/len(el.get_text()) < 0.3:
				outputHtml.write(str(el) + '\n')
				output.write(get_text(el))

		og_title = soup.find('meta', attrs= { 'property':'og:title' })
		if og_title:
			title = og_title.get('content')
		else:
			twitter_title = soup.find('meta', attrs= { 'name':'twitter:title' })
			if twitter_title:
				title = twitter_title.get('content')
			else:
				main_title = soup.find('meta', attrs= { 'name': 'title' })
				if main_title:
					title = main_title.get('content')
				else:
					title = get_text(soup.title)

		og_description = soup.find('meta', attrs= { 'property':'og:description' })
		if og_description:
			description = og_description.get('content')
		else:
			twitter_description = soup.find('meta', attrs= { 'name':'twitter:description' })
			if twitter_description:
				description = twitter_description.get('content')
			else:
				main_description = soup.find('meta', attrs= { 'name':'description' })
				if main_description:
					description = main_description.get('content')
				else:
					description = None

		try:
			print('HTML:', this_url_id, url)
		except:
			pass

		db.save_document(
			this_url_id,
			title,
			description,
			re.sub(' +', ' ', output.getvalue()),
			outputHtml.getvalue())


def process_img(url, request, response, data, **kwarg):
	this_url_id = kwarg['url_id']

	try:
		print('IMAGE:', this_url_id, url)
	except:
		pass

	blob = images.resize(140, 140, data)
	if blob:
		with db.scope():
			db.save_image(this_url_id, blob)

def process_plain(url, request, response, data, **kwarg):
	pass

def process(url, request, response, data):
	request = CaseInsensitiveDict.fromdict(json.loads(request))
	response = CaseInsensitiveDict.fromdict(json.loads(response))

	# verifica se é um content-type válido
	m = re.match('^\s*([\w-]+/[\w-]+)', response.get('Content-Type', 'text/html'))
	if not m or m.group(1) not in allowed_mimes:
		return

	# descobre o tipo de dado na resposta e qual função
	# irá tratá-la
	if m.group(1) == 'text/html':
		func = process_html
		link_type = 1
	elif m.group(1).startswith('image/'):
		func = process_img
		link_type = 2
	elif m.group(1) == 'text/plain':
		func = process_plain
		link_type = 3

	# salva o link sem as informações para fazer as referências necessárias
	link_url = urlhelper.Url.parse(url)
	with db.scope():
		this_domain_id = db.save_domain(link_url.domain)
		this_url_id = db.save_url(this_domain_id, link_url.path,
			m.group(1), link_type)

	kwarg = {
		'link_url': link_url,
		'domain_id': this_domain_id,
		'url_id': this_url_id
	}

	# chama a função específica para tratar esta url
	func(url, request, response, data, **kwarg)


def start():
	queue = ProcessQueue()
	queue.bind(process)

	queue.run()

if __name__ == '__main__':
	start()
