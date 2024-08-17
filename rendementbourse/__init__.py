
import fnmatch

from .sector import Sector
from .dividend import Dividend


class RendementBourse:
	Sector = Sector
	Dividend = Dividend

	@classmethod
	def find(cls, value: str) -> dict:
		"""
		:param value: find value get keys TICKER, HREF
		"""
		for line in cls.Sector.sectors:
			values = [v for k, v in line.items()]
			res = bool(list(filter(lambda x: fnmatch.fnmatch(value, x), values)))
			if res:
				return line
		return {}
