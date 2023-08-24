import json
import os
from dotmap import DotMap

import urllib3

from core.properties import properties

if __name__ == '__main__':
	app = DotMap({
		'instance_path': os.path.dirname(os.path.realpath(__file__)),
		'root_path': os.getcwd(),
	})

	properties.load(app)

	base_url = properties.get('flask.base_url')

	url = base_url

	payload = {
		'block_template': {
			'max_number_of_attempts': 48,
		}
	}

	response = urllib3.PoolManager().request(
		'POST',
		url,
		body=json.dumps(payload).encode('utf-8'),
		headers={
			'Content-Type': 'application/json',
		}
	)

	print(response.data.decode('utf-8'))
