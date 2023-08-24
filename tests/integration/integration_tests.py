import json
import os

import urllib3
from dotmap import DotMap

from core.properties import properties

def test_01():
	app = DotMap({
		'instance_path':os.path.dirname(os.path.realpath(__file__)),
		'root_path':os.getcwd(),
	})

	properties.load(app)

	base_url = properties.get('flask.base_url')

	# TODO Check how to properly test Flask APIs.
	url = base_url

	payload = {}

	response = urllib3.PoolManager().request(
		'POST',
		url,
		body=json.dumps(payload).encode('utf-8'),
		headers={
			'Content-Type': 'application/json',
		}
	)

	print(response.data.decode('utf-8'))


if __name__ == '__main__':
	test_01()
