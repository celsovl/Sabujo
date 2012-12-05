import unittest as ut
import crawler.db as db

class DbTest(ut.TestCase):
	def test_add_domain(self):
		with db.scope():
			self.assertIsInstance(db.save_domain('google.com'), int)

	def test_add_url(self):
		with db.scope():
			domain_id = db.save_domain('google.com')
			url_id = db.save_url(domain_id, '/google+/index.aspx?user=main#2')
			self.assertIsInstance(url_id, int)

if __name__ == '__main__':
	ut.main()
