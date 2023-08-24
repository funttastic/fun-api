import asyncio
import time
from typing import Dict, Optional

from singleton.singleton import ThreadSafeSingleton

from core.properties import properties


@ThreadSafeSingleton
class Clock(object):

	def __init__(self):
		self._initialized = False
		self._can_run = False
		self._delay = properties.get_or_default('clock.delay', 1)
		self._has_new_events = asyncio.Event()
		self._events: Dict[float, asyncio.Event] = dict({})
		self._tick_task: Optional[asyncio.Task] = None

	def start(self):
		if not self._initialized:
			self._can_run = True

			self._tick_task = asyncio.create_task(self._tick())

			self._initialized = True

	async def _tick(self):
		while self._can_run:
			await self._has_new_events.wait()

			pending_events: Dict[float, asyncio.Event] = dict({})

			for timestamp, event in self._events.items():
				if self.now() > timestamp:
					event.set()
				else:
					pending_events[timestamp] = event

			self._events = pending_events

			if not self._events:
				self._has_new_events.clear()

			await asyncio.sleep(self._delay)

	def get(self, timestamp: float):
		return self._events.get(timestamp, None)

	def register(self, timestamp: float):
		if not self._events.get(timestamp):
			self._events[timestamp] = asyncio.Event()
			self._has_new_events.set()

		return timestamp, self._events[timestamp]

	def deregister(self, timestamp: float):
		del self._events[timestamp]

		if not self._events:
			self._has_new_events.clear()

	async def stop(self):
		self._can_run = False
		self._initialized = False
		try:
			self._tick_task.cancel()
			await self._tick_task
		except asyncio.exceptions.CancelledError:
			pass

	@staticmethod
	def now() -> float:
		return time.time()

	def clear(self):
		self._events.clear()
		self._has_new_events.clear()


clock = Clock.instance()
