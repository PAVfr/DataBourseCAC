
import json


class EasyFileJson:
	def __init__(self, path: str):
		"""
		:param path: str | list
		:type path: str or list
		"""
		self.name = path.rsplit(".", maxsplit=1)[0]
		self.path = path
		self.encoding = "UTF-8"
		self.data: dict = {}

	def load(self):
		"""Conversion d'un fichier JSON en dictionnaire Python. """
		try:
			with open(self.path, mode="r", encoding=self.encoding) as file:
				self.data = json.loads(file.read())
		except FileNotFoundError:
			self.data = {}
		finally:
			return self

	def loads(self, s: str):
		"""Conversion d'une chaîne JSON (str) en un dictionnaire Python. """
		self.data = json.loads(s)
		return self

	def save(self, sort_keys=False, indent=4, ensure_ascii=None, separators=None):
		"""
		Écrase le dictionnaire Python dans le fichier JSON.
		Créé les dossiers récursifs s'ils n'existent pas.

		:type sort_keys: bool
		:type indent: int
		:type ensure_ascii: bool
		:type separators: tuple
		"""
		with open(self.path, mode="w", encoding=self.encoding) as file:
			json.dump(self.data, file, indent=indent, sort_keys=sort_keys, separators=separators, ensure_ascii=ensure_ascii)
