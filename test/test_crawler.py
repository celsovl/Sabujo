import bs4
import unittest as ut
import crawler
import sys

class CrawlerTest(ut.TestCase):
	def setUp(self):
		self.url = 'www.google.com'

	def test_download(self):
		response = crawler.download(self.url)
		self.assertTrue(self.url in response.geturl())

	def test_detectencoding(self):
		response = crawler.download(self.url)
		data = response.read()
		charset = crawler.detectcharset(response.info(), data)
		self.assertEqual(charset, 'iso-8859-1')
		data.decode(charset)

	def test_detectencoding2(self):
		url = 'g1.globo.com'
		response = crawler.download(url)
		data = response.read()
		charset = crawler.detectcharset(response.info(), data)
		self.assertEqual(charset, 'utf-8')
		data.decode(charset)

	def test_loadbs(self):
		soup = crawler.loadbs(self.url)
		self.assertEqual(type(soup), bs4.BeautifulSoup)

	def test_loadbs2(self):
		urls = ('uol.com.br', 'ig.com.br', 'g1.globo.com', 'apinfo.com')
		for url in urls:
			soup = crawler.loadbs(url)
			self.assertEqual(type(soup), bs4.BeautifulSoup)

	def test_readtitle(self):
		url = 'uol.com.br'
		#import pdb; pdb.set_trace()
		soup = crawler.loadbs(url)
		self.assertEqual('UOL - O melhor conteúdo', crawler.readtitle(soup))

	def test_readlinks(self):
		url = 'http://www1.folha.uol.com.br/esporte/1187452-empate-entre-portuguesa-e-gremio-rebaixa-o-palmeiras-a-serie-b.shtml'
		soup = crawler.loadbs(url)
		crawler.readlinks(soup, url)

	def test_readtext(self):
		url = 'http://globoesporte.globo.com/futebol/brasileirao-serie-a/noticia/2012/11/gremio-reage-empata-com-lusa-e-confirma-rebaixamento-do-palmeiras.html'
		soup = crawler.loadbs(url)
		crawler.readtext(soup)

	def test_detectdomain(self):
		url = 'folha.com.br'
		response = crawler.download(url)
		self.assertEqual('www.folha.uol.com.br', crawler.detectdomain(response))

if __name__ == '__main__':
	if len(sys.argv) > 2:
		ut.main(sys.argv[2])
	else:
		ut.main()
