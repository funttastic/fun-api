import sqlite3
import os

from properties import properties


class Database(object):
	def __init__(self):
		self.connection = None
		self.connect()

	def close(self):
		if self.connection:
			self.connection.close()
			self.connection = None

	def connect(self):
		if self.connection is None:
			database_path = os.path.join(properties.get('app_root_path'), properties.get('database.relative_path'))

			self.connection = sqlite3.connect(database_path)

	def plain_row_factory(self):
		self.connection.row_factory = lambda cursor, row: row[0]

	def normal_row_factory(self):
		self.connection.row_factory = None

	def execute(self, query):
		return self.connection.cursor().execute(query)

	def commit(self):
		self.connection.commit()

	def rollback(self):
		self.connection.rollback()
