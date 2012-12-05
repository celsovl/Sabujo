from bottle import *
import crawler.db as db

@route('/')
@route('/index')
def index():
	return static_file('index.html', root='.')


@get('/url/<urlId>')
def get_url(urlId):
	return template('url.html', urlId=urlId)


@get('/domain/<name>')
def get_domain(name):
	return template('domain.html', name=name)


@get('/favicon.ico')
def favicon():
	return static_file('favicon.ico', root='.')


@get('/<folder:re:img|js|css>/<filename:re:.*>')
def static(folder, filename):
	return static_file(filename, root='./' + folder)


@get('/services/typeaheaddomain/<query>')
def typeaheaddomain(query):
	with db.scope():
		result = db.querydomain(query)
		return { 'options': result }

	return {}


@get('/services/topheaders/<domain>')
def get_top_headers(domain):
	with db.scope():
		result = db.get_top_headers(domain)
		if result:
			return { 'success': result }

	return {}


@get('/services/url/document/<urlId>')
def get_text(urlId):
	with db.scope():
		document = db.get_url_document(urlId)
		if document:
			return { 'success': document }

	return {}


@get('/services/url/images/<urlId>')
def get_url_images(urlId):
	with db.scope():
		images = db. get_images(urlId)
		return { 'success': images }


@get('/services/domain/images/<name>')
def get_domain_images(name):
	with db.scope():
		images = db. get_domain_images(name)
		return { 'success': images }


@get('/services/domain/pages/<domain>')
def get_domain_pages(domain):
	with db.scope():
		links = db.get_pages(domain)
		if links:
			return { 'success': links }

	return {}


@get('/imgdb/<urlId>')
def get_image(urlId):
	response.content_type = 'image/jpeg'
	with db.scope():
		blob = db.get_image(urlId)
		if blob:
			return blob

	abort(404, 'Imagem inexistente.')
		

@get('/services/domain/links/<domain>')
def get_domain_links(domain):
	with db.scope():
		links = db.get_links(domain)
		if links:
			return { 'success': links }

	return {}


@get('/services/websiteinfo/<domain>')
def getwebsiteinfo(domain):
	with db.scope():
		domain = db.correct_name(domain)
		if domain:
			linksTo = db.get_link_to(domain)
			linkedBy = db.get_linked_by(domain)

			x = {
				'domain': domain,
				'linksTo': {},
				'linkedBy': {},
				'details': {
					'links': db.get_count_local_links(domain),
					'foreignLinks': db.get_count_foreign_links(domain),
					'images': db.get_count_images(domain),
					'mainCategories': ['Geral']
				}
			}

			for link in linksTo:
				x['linksTo'][link] = db.get_count_local_links(link)

			for link in linkedBy:
				x['linkedBy'][link] = db.get_count_foreign_links(link)

			return x


run(host='0.0.0.0', port=8000, debug=True, reloader=True)
