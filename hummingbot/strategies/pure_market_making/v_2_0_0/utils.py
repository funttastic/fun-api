import time
import functools




def retry(exception_to_check, tries=3, delay=10, backoff=2, logger=None):
	"""
	Retry decorator with exponential backoff.
	"""


	def deco_retry(f):


		@functools.wraps(f)
		def f_retry(*args, **kwargs):
			mtries, mdelay = tries, delay
			while mtries > 1:
				try:
					return f(*args, **kwargs)
				except exception_to_check as e:
					msg = f"{str(e)}, Retrying in {mdelay} seconds..."
					if logger:
						logger.warning(msg)
					else:
						print(msg)
					time.sleep(mdelay)
					mtries -= 1
					mdelay *= backoff
			return f(*args, **kwargs)


		return f_retry


	return deco_retry

