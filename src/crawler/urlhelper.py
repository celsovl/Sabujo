import crawler.config as config
import logging
import urllib.error
import urllib.parse
import urllib.robotparser as robotparser

logger = logging.getLogger(__name__)
logger.addHandler(logging.FileHandler('log.txt', encoding='utf-8'))

robots_cache = {}

def fullurl(url, link):
	parsedurl = urllib.parse.urlparse(url)
	parsedlink = urllib.parse.urlparse(link)
	correctedurl = urllib.parse.ParseResult(
		parsedlink.scheme or 'http',
		parsedlink.netloc or parsedurl.netloc,
		parsedlink.path,
		parsedlink.params,
		parsedlink.query,
		parsedlink.fragment)

	return correctedurl.geturl()

def robots_url(url):
	return urllib.parse.urljoin(url, '/robots.txt')

def can_fetch(url):
	rurl = robots_url(url)

	if not rurl in robots_cache:
		rp = robotparser.RobotFileParser()
		rp.set_url(rurl)

		try:
			rp.read()
			robots_cache[rurl] = rp
		except Exception:
			robots_cache[rurl] = None

	logger.debug('%s\t%s', url, rurl)

	rp = robots_cache[rurl]
	if rp:
		return rp.can_fetch(config.USERAGENT, url)

	return True


class Url:
	def __init__(self, url):
		self.parsed = url

	def _getdomain(self):
		return self.parsed.netloc

	def _getpath(self):
		p = ['', '']
		p.extend(self.parsed[2:])
		return urllib.parse.urlunparse(p) or '/'

	path = property(_getpath)
	domain = property(_getdomain)

	def __getattr__(self, attr):
		if attr in self.parsed:
			return self.parsed.__getattr__(attr)

		raise AttributeError(attr)

	@staticmethod
	def parse(url, base=None):
		base = base or url
		joined = urllib.parse.urljoin(base, url)
		parsed = urllib.parse.urlparse(joined)

		return Url(parsed)
