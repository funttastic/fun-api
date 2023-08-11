import asyncio
import time
from typing import Optional


def now():
	return time.time()


class Worker:
	def __init__(self, name, waiting_time):
		self.name = name
		self.waiting_time = waiting_time
		self.timestamp: Optional[int] = None
		self.event: Optional[asyncio.Event] = asyncio.Event()

	async def start(self):
		while True:
			print(f"""{now()} {self.name}: loop wait""")
			await self.event.wait()
			print(f"""{now()} {self.name}: loop start""")
			await asyncio.sleep(1)  # Doing async stuff
			print(f"""{now()} {self.name}: loop end""")
			print(f"""{now()} {self.name}: loop sleeping""")
			await asyncio.sleep(self.waiting_time)
			print(f"""{now()} {self.name}: loop awoke""")


async def main():
	worker1 = Worker("worker1", 3)
	worker2 = Worker("worker2", 30)

	task1 = asyncio.create_task(worker1.start())
	task2 = asyncio.create_task(worker2.start())

	worker1.event.set()
	worker2.event.set()

	await asyncio.gather(task1, task2)

if __name__ == "__main__":
	asyncio.run(main())
