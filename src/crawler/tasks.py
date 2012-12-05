import crawler.config as config
import mysql.connector as mysqldb
import hashlib

class _Scope:
	scopes = []

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


class TaskQueue:
	def __init__(self):
		self.funcs = []
		self.tasks = []

	@staticmethod
	def scope():
		return _Scope()
		
	@staticmethod
	def _curscope():
		if len(_Scope.scopes) == 0:
			raise Exception('there is no scope available.')

		return _Scope.scopes[-1].cnx
		
	@staticmethod
	def push(url):
		query = 'INSERT IGNORE INTO taskQueue (id, url, sha1Url, processed) values (NULL, %s, %s, false)'

		sha1_url = hashlib.sha1(url.encode('utf-8')).digest()
		cursor = TaskQueue._curscope().cursor()
		cursor.execute(query, (url, sha1_url))
		cursor.close()

	def bind(self, func):
		if not callable(func):
			raise Error('func must be callable')

		if not func in self.funcs:
			self.funcs.append(func)

	def _invoke(self, task):
		task_id, url = task
		for func in self.funcs:
			func(url)

		self._done(task_id)

	def _done(self, task_id):
		query = 'UPDATE taskQueue SET processed = true WHERE id = %s'
		cursor = TaskQueue._curscope().cursor()
		cursor.execute(query, (task_id,))
		cursor.close()
		
		
	def run(self, times=None):
		while times == None or times > 0:
			with TaskQueue.scope():
				self._fetch()

				for task in self.tasks:
					self._invoke(task)

			self.tasks = []

			if times:
				times -= 1

	def _fetch(self, batch_size=20):
		query = "SELECT id, url FROM taskQueue WHERE processed = false ORDER BY id LIMIT %s"
		cursor = TaskQueue._curscope().cursor()
		cursor.execute(query, (batch_size,))

		for task_id, url in cursor:
			self.tasks.append((task_id, url))

		cursor.close()
