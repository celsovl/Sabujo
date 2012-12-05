import crawler.config as config
import mysql.connector as mysqldb
import hashlib

class _Scope:
	def __enter__(self):
		self.cnx = mysqldb.connect(**config.DBCONNECTION)
		_Scope.scopes.append(self)

	def __exit__(self, type_ex, ex, traceback):
		if not ex:
			self.cnx.commit()
		else:
			self.cnx.rollback()

		self.cnx.close()
		_Scope.scopes.pop()

		# reraise errors
		return False

_Scope.scopes = []

def scope():
	return _Scope()
	
def _curscope():
	if len(_Scope.scopes) == 0:
		raise Exception('there is no scope available.')

	return _Scope.scopes[-1].cnx

def save_domain(name):
	query =	('INSERT INTO domain (id, name) VALUES (DEFAULT, %s) '
					'ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id)')
	cursor = _curscope().cursor()
	cursor.execute(query, (name,))
	cursor.close()
	return cursor.lastrowid

def save_url(domainId, path, mime=None, type_url=None):
	query =	('INSERT INTO url (id, domainId, path, sha1Path, mime, type) '
						'VALUES (NULL, %s, %s, %s, %s, %s) '
					'ON DUPLICATE KEY UPDATE id = LAST_INSERT_ID(id), mime=VALUES(mime), '
					'type=VALUES(type)')

	encoded_path = bytes(path, 'utf-8')
	sha1_path = hashlib.sha1(encoded_path).digest()
	cursor = _curscope().cursor()
	cursor.execute(query, (domainId, path, sha1_path, mime, type_url))
	cursor.close()
	return cursor.lastrowid

def associate(reference_id, referenced_id, text=None):
	query =	('INSERT IGNORE INTO urlToUrl (referenceId, referencedId, text) '
						'VALUES (%s, %s, %s) ')

	cursor = _curscope().cursor()
	cursor.execute(query, (reference_id, referenced_id, text))
	cursor.close()


def save_header(url_id, text=''):
	query =	('INSERT INTO urlHeader (urlId, text) '
						'VALUES (%s, %s) ')

	cursor = _curscope().cursor()
	cursor.execute(query, (url_id, text))
	cursor.close()

def save_document(url_id, title=None, description=None, text='', text_html=''):
	query =	('INSERT INTO urlDocument (urlId, title, description, text, textHtml) '
						'VALUES (%s, %s, %s, %s, %s) '
						'ON DUPLICATE KEY UPDATE title=VALUES(title), description=VALUES(description), '
						'text=VALUES(text), textHtml=VALUES(textHtml)')

	cursor = _curscope().cursor()
	cursor.execute(query, (url_id, title, description, text, text_html))
	cursor.close()

def querydomain(q):
	domains = []
	query = ("SELECT trim(name) FROM domain WHERE name like %s LIMIT 8")
	cursor = _curscope().cursor()
	cursor.execute(query, ('%' + q + '%',))
	for (d,) in cursor:
		domains.append(d)
	cursor.close()
	return domains
	
def correct_name(name):
	query = ('SELECT trim(name) FROM domain WHERE name = %s')
	cursor = _curscope().cursor()
	cursor.execute(query, (name,))
	name = None
	for (d,) in cursor:
		name = d
	cursor.close()
	return name

def get_link_to(name):
	domains = []
	query = ('SELECT DISTINCT trim(d.name) '
						'FROM domain d JOIN url ud ON d.id = ud.domainId '
						'JOIN urlToUrl uu ON ud.id = uu.referencedId '
						'JOIN url udq ON udq.id = uu.referenceId '
						'JOIN domain dq ON dq.id = udq.domainId '
						'WHERE dq.name = %s AND d.name <> %s')
	cursor = _curscope().cursor()
	cursor.execute(query, (name, name))
	for (d,) in cursor:
		domains.append(d)
	cursor.close()
	return domains


def get_linked_by(name):
	domains = []
	query = ('SELECT DISTINCT (d.name) '
						'FROM domain d JOIN url ud ON d.id = ud.domainId '
						'JOIN urlToUrl uu ON ud.id = uu.referenceId '
						'JOIN url udq ON udq.id = uu.referencedId '
						'JOIN domain dq ON dq.id = udq.domainId '
						'WHERE dq.name = %s AND d.name <> %s')
	cursor = _curscope().cursor()
	cursor.execute(query, (name, name))
	for (d,) in cursor:
		domains.append(d)
	cursor.close()
	return domains

def get_count_local_links(name):
	query = ('SELECT COUNT(*) '
					'FROM urlToUrl uu JOIN url u ON u.id = uu.referenceId '
					'JOIN domain d ON d.id = u.domainId '
					'JOIN url u2 ON u2.id = uu.referencedId '
					'WHERE u.domainId = u2.domainId AND d.name = %s')
	cursor = _curscope().cursor()
	cursor.execute(query, (name,))
	count = 0
	for (c,) in cursor:
		count = c 
	cursor.close()
	return count
	
def get_count_foreign_links(name):
	query = ('SELECT COUNT(*) '
					'FROM urlToUrl uu JOIN url u ON u.id = uu.referenceId '
					'JOIN domain d ON d.id = u.domainId '
					'JOIN url u2 ON u2.id = uu.referencedId '
					'WHERE u.domainId <> u2.domainId AND d.name = %s')
	cursor = _curscope().cursor()
	cursor.execute(query, (name,))
	count = 0
	for (c,) in cursor:
		count = c 
	cursor.close()
	return count
	
def get_count_images(name):
	return 0


def get_url_document(urlId):
	query = ('SELECT ud.title, ud.description, ud.text, ud.textHtml, u.path, d.name '
						'FROM urlDocument ud JOIN url u ON u.id = ud.urlId '
						'JOIN domain d ON d.id = u.domainId WHERE u.id = %s')
	cursor = _curscope().cursor()
	cursor.execute(query, (urlId,))
	result = None
	for title, desc, text, text_html, path, domain in cursor:
		result = {
			'title': title,
			'description': desc,
			'text': text,
			'textHtml': text_html,
			'path': path,
			'domain': domain
		}

	cursor.close()
	return result

def get_top_headers(name):
	query = ("SELECT COUNT(*) AS 'num', h.urlId, h.text "
					"FROM urlHeader h JOIN url u ON u.id = h.urlId "
					"JOIN domain d ON d.id = u.domainId "
					"WHERE d.name = %s AND h.text <> '' "
					"GROUP BY h.text "
					"ORDER BY num, CASE WHEN LENGTH(h.text) > 30 THEN 1 ELSE 2 END "
					"LIMIT 30")
	
	cursor = _curscope().cursor()
	cursor.execute(query, (name,))
	result = []
	for c, url_id, header in cursor:
		result.append({
			'urlId': url_id,
			'header': header 
		})

	cursor.close()
	return result


def get_urls(name):
	query = ("SELECT COUNT(*) AS 'num', h.urlId, h.text "
					"FROM urlHeader h JOIN url u ON u.id = h.urlId "
					"JOIN domain d ON d.id = u.domainId "
					"WHERE d.name = %s AND h.text <> '' "
					"GROUP BY h.text "
					"ORDER BY num, CASE WHEN LENGTH(h.text) > 30 THEN 1 ELSE 2 END "
					"LIMIT 30")
	
	cursor = _curscope().cursor()
	cursor.execute(query, (name,))
	result = []
	for c, url_id, header in cursor:
		result.append({
			'urlId': url_id,
			'header': header 
		})

	cursor.close()
	return result


def get_pages(name):
	query = ("SELECT u.id, ud.title, ud.description FROM urlDocument ud "
					"JOIN url u ON u.id = ud.urlId JOIN domain d ON d.id = u.domainId "
					"WHERE d.name = %s AND ud.title <> '' AND ud.title IS NOT NULL")
	cursor = _curscope().cursor()
	cursor.execute(query, (name,))
	result = []
	for url_id, title, description in cursor:
		result.append({
			'urlId': url_id,
			'title': title,
			'description': description
		})

	cursor.close()
	return result


def get_links(name):
	query = ("SELECT COUNT(*) AS 'num', uu.text, u2.path, d2.name FROM urlToUrl uu JOIN url u ON uu.referenceId = u.id "
					"JOIN domain d ON u.domainId = d.id "
					"JOIN url u2 ON uu.referencedId = u2.id "
					"JOIN domain d2 ON u2.domainId = d2.id "
					"WHERE d.name = %s AND TRIM(uu.text) <> '' AND uu.text IS NOT NULL "
					"GROUP BY uu.text, u2.path, d2.name "
					"ORDER BY num, CASE WHEN LENGTH(uu.text) > 30 THEN 1 ELSE 2 END")

	cursor = _curscope().cursor()
	cursor.execute(query, (name,))
	result = []
	for c, text, path, domain in cursor:
		result.append({
			'text': text,
			'path': path,
			'domain': domain
		})

	cursor.close()
	return result


def save_image(url_id, blob):
	query = ("INSERT IGNORE INTO urlImage (urlId, image) values (%s, %s)")
	cursor = _curscope().cursor()
	cursor.execute(query, (url_id, blob))
	cursor.close()


def get_image(url_id):
	query = ("SELECT image FROM urlImage WHERE urlId = %s")
	cursor = _curscope().cursor()
	cursor.execute(query, (url_id,))
	blob = None
	for (b,) in cursor:
		blob = b

	cursor.close()
	return blob


def get_images(url_id):
	query = ("SELECT DISTINCT d.name, u.path, uu.referencedId "
					"FROM domain d JOIN url u ON d.id = u.domainId "
					"JOIN urlImage ui ON u.id = ui.urlId "
					"JOIN urlToUrl uu ON u.id = uu.referencedId "
					"JOIN url u2 ON uu.referenceId = u2.id "
					"WHERE u2.id = %s AND u.type = 2")
	cursor = _curscope().cursor()
	cursor.execute(query, (url_id,))
	images = [{
		'domain': domain,
		'path': path,
		'urlId': urlid
		} for domain, path, urlid in cursor]
	cursor.close()
	return images


def get_domain_images(name):
	query = ("SELECT DISTINCT d.name, u.path, uu.referencedId "
					"FROM domain d JOIN url u ON d.id = u.domainId "
					"JOIN urlImage ui ON u.id = ui.urlId "
					"JOIN urlToUrl uu ON u.id = uu.referencedId "
					"JOIN url u2 ON uu.referenceId = u2.id "
					"JOIN domain d2 ON u2.domainId = d2.id "
					"WHERE d2.name = %s AND u.type = 2")
	cursor = _curscope().cursor()
	cursor.execute(query, (name,))
	images = [{
		'domain': domain,
		'path': path,
		'urlId': urlid
		} for domain, path, urlid in cursor]
	cursor.close()
	return images


