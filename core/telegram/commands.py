from enum import Enum
from typing import Any

from dotmap import DotMap

from core.properties import properties
# noinspection PyUnresolvedReferences
from telegram import Update
from telegram.ext import ContextTypes, MessageHandler, filters, CommandHandler

from core import controller
from core.telegram.telegram import telegram
from core.utils import dump


def validate(update: Update, _context: ContextTypes.DEFAULT_TYPE) -> bool:
	authorized_users = properties.get_or_default('telegram.admin.users', [])

	user_name = str(update.effective_user.name)
	if len(authorized_users) > 0 and user_name not in authorized_users:
		return False

	chat_id = str(update.message.chat_id)
	if chat_id != telegram.chat_id:
		return False

	return True


def sanitize(_update: Update, context: ContextTypes.DEFAULT_TYPE) -> DotMap[str, Any]:
	output = DotMap({})

	# (empty)
	# <supervisor_id>
	# <strategy_id>:<strategy_version>:<supervisor_id>
	# <supervisor_id> <worker_id>
	# <strategy_id>:<strategy_version>:<supervisor_id> <worker_id>
	if len(context.args):
		supervisor = context.args[0].split(':')

		if len(supervisor) > 1:
			output.strategy = supervisor[0]

			if len(supervisor) > 1:
				output.version = supervisor[1]

			if len(supervisor) > 2:
				output.id = supervisor[2]
		else:
			output.id = context.args[0]

		if len(context.args) > 1:
			output.worker_id = context.args[1]

	output._dynamic = False

	return output


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not validate(update, context):
		return

	options = sanitize(update, context)

	response = await controller.strategy_start(options)
	telegram.send(dump(response))


async def status(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not validate(update, context):
		return

	options = sanitize(update, context)

	response = await controller.strategy_status(options)
	telegram.send(dump(response))


async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
	if not validate(update, context):
		return

	options = sanitize(update, context)

	response = await controller.strategy_stop(options)
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
