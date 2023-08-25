from enum import Enum
from typing import Any

# noinspection PyUnresolvedReferences
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler

from core import controller
from core.telegram.telegram import telegram
from core.utils import dump


def validate(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> bool:
	chat_id = str(update.message.chat_id)
	if chat_id != telegram.chat_id:
		return False

	return True


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not validate(update, context):
		return

	if not context.args:
		telegram.send("You need to provide the strategy, version and id")
		return

	args = context.args[0].split(':')
	if len(args) != 3:
		telegram.send("You need to provide the strategy, version and id")
		return

	strategy = args[0]
	version = args[1]
	id = args[2]
	response = await controller.strategy_start(strategy, version, id)
	telegram.send(dump(response))


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not validate(update, context):
		return

	if not context.args:
		telegram.send("You need to provide the strategy, version and id")
		return

	args = context.args[0].split(':')
	if len(args) != 3:
		telegram.send("You need to provide the strategy, version and id")
		return

	strategy = args[0]
	version = args[1]
	id = args[2]
	response = await controller.strategy_stop(strategy, version, id)
	telegram.send(dump(response))


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not validate(update, context):
		return

	if not context.args:
		telegram.send("You need to provide the strategy, version and id")
		return

	args = context.args[0].split(':')
	if len(args) != 3:
		telegram.send("You need to provide the strategy, version and id")
		return

	strategy = args[0]
	version = args[1]
	id = args[2]
	response = await controller.strategy_status(strategy, version, id)
	telegram.send(dump(response))


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not validate(update, context):
		return

	telegram.send("Sorry, I didn't understand that command.")


class Command(Enum):
	START = ("start", start, None)
	STOP = ("stop", stop, None)
	STATUS = ("status", status, None)
	UNKNOWN = ("unknown", unknown, MessageHandler(filters.COMMAND, unknown))

	def __init__(self, id: str, command: Any, handler: Any):
		self.id = id
		self.command = command
		if not handler:
			self.handler = CommandHandler(self.id, command)
		else:
			self.handler = handler
