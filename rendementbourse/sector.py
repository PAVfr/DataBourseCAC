
from options import Options

import re


class Sector:
	sectors: list[dict] = []

	@classmethod
	def Consommation_de_base(cls):
		return cls._request("https://rendementbourse.com/action/consommation-base", "Consommation de base")

	@classmethod
	def Consommation_discretionnaire(cls):
		return cls._request("https://rendementbourse.com/action/consommation-discretionnaire", "Consommation discrétionnaire")

	@classmethod
	def Energie(cls):
		return cls._request("https://rendementbourse.com/action/energie", "Energie")

	@classmethod
	def Finance(cls):
		return cls._request("https://rendementbourse.com/action/finance", "Finance")

	@classmethod
	def Immobilier(cls):
		return cls._request("https://rendementbourse.com/action/immobilier", "Immobilier")

	@classmethod
	def Industrie(cls):
		return cls._request("https://rendementbourse.com/action/industrie", "Industrie")

	@classmethod
	def Materiaux(cls):
		return cls._request("https://rendementbourse.com/action/materiaux", "Matériaux")

	@classmethod
	def Sante(cls):
		return cls._request("https://rendementbourse.com/action/sante", "Santé")

	@classmethod
	def Services_aux_collectivites(cls):
		return cls._request("https://rendementbourse.com/action/collectivites", "Services aux collectivités")

	@classmethod
	def Technologies(cls):
		return cls._request("https://rendementbourse.com/action/technologies", "Technologies")

	@classmethod
	def Telecommunications(cls):
		return cls._request("https://rendementbourse.com/action/communication", "Télécommunications")

	@classmethod
	def all_sector(cls) -> dict[list]:
		lines = []
		# Réccupère la liste des méthodes à exécuter
		for method in [v for v in dir(Sector) if not v.startswith("_") and re.match(r"[A-Z]\w", v)]:
			# Execute les methodes
			for response in getattr(cls, method)():
				lines.append(response)
		cls.sectors = lines
		return lines

	@classmethod
	def _request(cls, url: str, sector: str, params=None):
		lines = []
		for line in Options.requestGet(url=url, params=params).select_one("#quotesList > tbody").find_all("a"):
			# Si le ticker est bien un ".PA"
			code = line.text.strip().splitlines()[0]
			if code.rsplit(".")[-1] in ["PA", "BR"]:
				lines.append({
					"SECTOR": sector,
					"CODE": code,
					"TICKER": code.split(".", maxsplit=1)[0],
					"NAME": line.text.strip().splitlines()[-1].strip(),
					"HREF": line.get("href")
					})
		return lines


if __name__ == '__main__':
	Sector.all_sector()
	for v in ["ORA", "TFI", "STLAP"]:
		r = Sector.find(v)
		print(r)
