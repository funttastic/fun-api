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
		self._tick_task: Optional[asyncio.Task] = None

	def start(self):
		if not self._initialized:
			self._can_run = True

			self._tick_task = asyncio.create_task(self._tick())

			self._initialized = True

	async def _tick(self):
		while self._can_run:
			await self._has_new_events.wait()
			print(f"{self.now()} clock: start")

			pending_events: Dict[float, asyncio.Event] = dict({})

			for timestamp, event in self._events.items():
				if self.now() > timestamp:
					event.set()
					print(f"{self.now()} clock: event {timestamp} dispatched")
				else:
					pending_events[timestamp] = event

			self._events = pending_events

			if not self._events:
				self._has_new_events.clear()

			await asyncio.sleep(1)

	def register(self, timestamp: float):
		if not self._events.get(timestamp):
			self._events[timestamp] = asyncio.Event()
			self._has_new_events.set()

		return timestamp, self._events[timestamp]

	@staticmethod
	def now() -> float:
		return time.time()


class Worker:
	def __init__(self, name, waiting_time):
		self.name = name
		self.waiting_time = waiting_time
		self.timestamp: Optional[int] = None
		self.event: Optional[asyncio.Event] = None

	async def start(self):
		self.timestamp, self.event = clock.register(clock.now() + self.waiting_time)

		while True:
			print(f"""{clock.now()} {self.name}: loop wait""")
			await self.event.wait()
			print(f"""{clock.now()} {self.name}: loop start""")
			await asyncio.sleep(1)  # Doing async stuff
			self.timestamp, self.event = clock.register(clock.now() + self.waiting_time)
			print(f"""{clock.now()} {self.name}: loop end""")
			print(f"""{clock.now()} {self.name}: loop sleeping""")
			await asyncio.sleep(self.waiting_time)
			print(f"""{clock.now()} {self.name}: loop awoke""")


clock = Clock.instance()


async def main():
	clock.start()

	worker1 = Worker("worker1", 3)
	worker2 = Worker("worker2", 30)

	task1 = asyncio.create_task(worker1.start())
	task2 = asyncio.create_task(worker2.start())

	await asyncio.gather(task1, task2)

if __name__ == "__main__":
	asyncio.run(main())
