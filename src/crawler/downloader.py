from crawler.process import ProcessQueue
from crawler.tasks import TaskQueue
import crawler
import crawler.urlhelper as urlhelper
import json
import logging
import re

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
logger.addHandler(logging.FileHandler('log.txt', encoding='utf-8'))

def process(url):
	try:
		print('DOWNLOADING', url)
	except:
		pass

	if not urlhelper.can_fetch(url):
		logger.info('disallowed ' + url)
		return

	request, response, data, soup = crawler.load(url)

	if request == None:
		return

	if response.geturl().endswith('.pdf'):
		return

	drequest = { k: v for k, v in request.header_items() }
	dresponse = { k: v for k, v in response.getheaders() }
	dresponse.update({
		'status': response.status,
		'reason': response.reason
	})



	ProcessQueue.push(
		response.geturl(),
		json.dumps(drequest, sort_keys=True),
		json.dumps(dresponse, sort_keys=True),
		data)

	"""
	if soup:
		with TaskQueue.scope():
			for link in crawler.readlinkshref(soup):
				m = re.match('\s*(\w+):', link)
				if m and m.group(1) not in ('http', 'https'):
					continue

				fullurl = urlhelper.fullurl(response.geturl(), link)
				if not urlhelper.can_fetch(fullurl):
					logger.info('disallowed ' + fullurl)
					continue

				try:
					print('PUSHING:', fullurl)
				except:
					pass
				TaskQueue.push(fullurl)

			for img in crawler.readimagessrc(soup):
				fullurl = urlhelper.fullurl(response.geturl(), img)
				if not urlhelper.can_fetch(fullurl) and False:
					logger.info('disallowed ' + fullurl)
					continue

				try:
					print('PUSHING:', fullurl)
				except:
					pass
				TaskQueue.push(fullurl)
	"""

def start():
	task_queue = TaskQueue()
	task_queue.bind(process)

	task_queue.run()

if __name__ == '__main__':
	start()
