import asyncio
import time
from typing import Dict, Optional

from singleton.singleton import ThreadSafeSingleton


@ThreadSafeSingleton
class Clock(object):

	def __init__(self):
		self._initialized = False
		self._can_run = False
		self._has_new_events = asyncio.Event()
		self._events: Dict[float, asyncio.Event] = dict({})
		self._tick: Optional[asyncio.Task] = None

	def start(self):
		if not self._initialized:
			self._can_run = True

			self._tick = asyncio.create_task(self.tick())

	async def tick(self):
		while self._can_run:
			await self._has_new_events.wait()

			pending_events: Dict[float, asyncio.Event] = dict({})

			for id, event in self._events.items():
				timestamp = float(id)
				if self.now() > timestamp:
					event.set()
				else:
					pending_events[timestamp] = event

			self._events = pending_events

			if not self._events:
				self._has_new_events.clear()

	async def stop(self):
		self._can_run = False
		self._initialized = False
		try:
			self._tick.cancel()
			await self._tick
		except asyncio.exceptions.CancelledError:
			pass

	def register(self, timestamp: float):
		if not self._events.get(timestamp):
			self._events[timestamp] = asyncio.Event()
			self._has_new_events.set()

		return timestamp, self._events[timestamp]

	def deregister(self, timestamp: float):
		del self._events[timestamp]

		if not self._events:
			self._has_new_events.clear()

	def get(self, timestamp: float):
		return self._events.get(timestamp, None)

	def clear(self):
		self._events.clear()
		self._has_new_events.clear()

	@staticmethod
	def now() -> float:
		return time.time()


clock = Clock.instance()
