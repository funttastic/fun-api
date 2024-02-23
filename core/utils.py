from datetime import datetime
from functools import reduce
from typing import Any

import jsonpickle
from dateutil.relativedelta import relativedelta
from deepmerge import always_merger
from dotmap import DotMap


def human_readable(delta):
	attributes = ['years', 'months', 'days', 'hours', 'minutes', 'seconds', 'microseconds']

	return ', '.join([
		(f'{getattr(delta, attribute)} {attribute}' if getattr(delta, attribute) > 0 else attribute[:-1])\
		for attribute in attributes if getattr(delta, attribute)
	])


def elapsed_time(start_time, end_time):
	start = datetime.fromtimestamp(start_time)
	end = datetime.fromtimestamp(end_time)
	delta = relativedelta(end, start)

	return human_readable(delta)


def safe_deep_get(self, keys, default=None):
	return reduce(
		lambda dictionary, key:
			dictionary.get(key, default) if isinstance(dictionary, dict)
			else default, keys.split("."), self
	)


def safe_deep_set(self, keys, value):
	keys = keys.split(".")

	last_key = keys.pop()

	current_dict = self

	for key in keys:
		if key not in current_dict or not isinstance(current_dict[key], dict):
			current_dict[key] = {}
		current_dict = current_dict[key]

	current_dict[last_key] = value


def deep_merge(base, next):
	return always_merger.merge(base, next)


def dump(target: Any):
	try:
		if isinstance(target, str):
			return target

		if isinstance(target, DotMap):
			target = target.toDict()

		return jsonpickle.encode(target, unpicklable=True, indent=2)
	except (Exception,):
		return target


def escape_html(text: str) -> str:
	return text.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&apos;")
