import crawler.config as config
import mysql.connector
import time
import hashlib

class ProcessQueue:
	def __init__(self):
		self.funcs = []
		self.queue = []

	@staticmethod
	def push(url, request, response, data):
		query = ('INSERT IGNORE INTO processQueue (id, url, sha1Url, request, response, data, processed) '
						'VALUES (NULL, %s, %s, %s, %s, %s, false)')

		if not (isinstance(request, str) and isinstance(response, str)):
			raise Exception('request and response must be str')

		if isinstance(data, str):
			data = data.encode('utf-8')

		cnx = mysql.connector.connect(**config.DBCONNECTION)

		sha1_url = hashlib.sha1(url.encode('utf-8')).digest()
		cursor = cnx.cursor()

		try:
			print('SAVING', url)
		except:
			pass

		cursor.execute(query, (url, sha1_url, request, response, data))


		try:
			print('COMMITING', url)
		except:
			pass

		cnx.commit()
		cursor.close()
		cnx.close()

		try:
			print('SAVED', url)
		except:
			pass

	def bind(self, func):
		if not callable(func):
			raise Exception('func must be callable')

		if not func in self.funcs:
			self.funcs.append(func)

	def _invoke(self, process):
		process_id, url, request, response, data = process 
		for func in self.funcs:
			func(url, request, response, data)

		self._done(process_id)

	def _done(self, process_id):
		query = 'UPDATE processQueue SET processed = %s WHERE id = %s'
		cnx = mysql.connector.connect(**config.DBCONNECTION)

		cursor = cnx.cursor()
		cursor.execute(query, (True, process_id))

		cnx.commit()
		cursor.close()
		cnx.close()
		
		
	def run(self, times=None):
		while times == None or times > 0:
			self._fetch()

			for process in self.queue:
				self._invoke(process)

			self.queue = []

			if times:
				times -= 1
			else:		# breathe
				time.sleep(1)

	def _fetch(self, batch_size=20):
		query = ('SELECT id, url, request, response, data FROM processQueue '
							'WHERE processed = false ORDER BY id LIMIT %s')

		cnx = mysql.connector.connect(**config.DBCONNECTION)

		cursor = cnx.cursor()
		cursor.execute(query, (batch_size,))

		for process_id, url, request, response, data in cursor:
			self.queue.append((process_id, url, request, response, data))

		cursor.close()
		cnx.close()
