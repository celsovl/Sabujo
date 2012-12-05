import unittest as ut
from crawler.tasks import TaskQueue

class TasksTest(ut.TestCase):
	def test_push(self):
		TaskQueue.push('http://www.google.com/')
		TaskQueue.push('http://www.globo.com/')
		TaskQueue.push('http://www.uol.com.br/')

	def test_all(self):
		TaskQueue.push('http://www.google.com/')
		TaskQueue.push('http://www.globo.com/')

		task_queue = TaskQueue()

		def p(url):
			pass

		task_queue.bind(p)
		task_queue.run(2)

if __name__ == '__main__':
	ut.main()
