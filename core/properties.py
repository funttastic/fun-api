import os

import yaml
import base64
from singleton.singleton import ThreadSafeSingleton

from core.constants import constants
from core.utils import deep_merge
from core.extensions import DotMap
from functools import reduce


@ThreadSafeSingleton
class Properties(object):
	def __init__(self):
		self.properties = DotMap({}, _dynamic=False)

	def load(self, app):
		self.load_from_app(app)
		self.load_from_constants()
		self.load_from_configuration_files()
		self.load_from_database()
		self.load_from_environment_variables()

	def load_from_app(self, app):
		self.properties['app'] = app
		self.properties['root_path'] = app.root_path
		self.properties['app_root_path'] = app.root_path
		self.properties['app_instance_path'] = app.root_path

	def load_from_constants(self):
		self.properties = deep_merge(self.properties, constants)

	def load_from_configuration_files(self):
		root_path = self.properties['app_root_path']

		configuration = {}

		with open(os.path.join(root_path, constants.configuration.relative_folder, constants.configuration.main), 'r') as stream:
			target = yaml.safe_load(stream) or {}
			configuration = deep_merge(configuration, target)

		with open(os.path.join(root_path, constants.configuration.relative_folder, constants.configuration.common), 'r') as stream:
			target = yaml.safe_load(stream) or {}
			configuration = deep_merge(configuration, target)

		if os.environ.get('ENVIRONMENT'):
			configuration['environment'] = os.environ['ENVIRONMENT']

		with open(os.path.join(root_path, constants.configuration.relative_folder, constants.configuration.environment[configuration['environment']]), 'r') as stream:
			target = yaml.safe_load(stream) or {}
			configuration = deep_merge(configuration, target)

		self.properties = DotMap(deep_merge(self.properties, configuration), _dynamic=False)

	def load_from_database(self):
		pass

	def load_from_environment_variables(self):
		pass

	def get_or_default_as(self, key, type, default=None):
		# TODO Finish implementation
		raise NotImplemented()

	def get(self, key):
		output = self.get_or_default(key, None)

		if output is None:
			raise ValueError(f'Property with key "{key}" not found.')

		return output

	def get_or_default(self, key, default=None):
		# if key.startswith('public.'):
		# 	try:
		# 		request_parameters = deep_merge(request.args, request.get_json())
		# 	except RuntimeError:
		# 		request_parameters = DotMap({}, _dynamic=False)
		#
		# 	output = request_parameters.safe_deep_get(key)
		# 	if output is not None: return output

		output = self.properties.safe_deep_get(key)
		if output is not None: return output

		modified_key = key.replace('.', '_')
		output = os.environ.get(modified_key, None)
		if output is not None: return output

		modified_key = modified_key.upper()
		output = os.environ.get(modified_key, None)
		if output is not None: return output

		if isinstance(output, DotMap): return default

		return default

	def set(self, key, value):
		file_path = f"{self.properties.root_path}/{self.properties.configuration.relative_folder}/{self.properties.server.environment}.yml"

		with open(file_path, 'r') as f:
			file_object = DotMap(yaml.safe_load(f))

		value_to_base64 = base64.b64encode(value).decode('utf-8')

		splitted_keys = key.split(".")

		propertie = reduce(lambda d, k: d[k], splitted_keys[:-1], file_object)

		propertie[splitted_keys[-1]] = value_to_base64

		with open(file_path, 'w') as f:
			yaml.dump(file_object.toDict(), f, Dumper=yaml.SafeDumper, sort_keys=False)


properties = Properties.instance()
