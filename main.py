
import pandas
import datetime
import time

from file_json import EasyFileJson
from bourseDirect import BourseDirect
from rendementbourse import RendementBourse
from euronextParis import EuroNextParis
from stockevents import StockEvents


class UpdateFiles:
	def __init__(self):
		self.file_enterprise = EasyFileJson(f"enterprise.json").load()
		self.file_dividend = EasyFileJson(f"dividend.json").load()

	def updateEnterprise(self):
		RendementBourse.Sector.all_sector()
		# Variables
		data_paris = EuroNextParis().data
		# BourseDirect
		for indice, lines in {
			"CAC_40": BourseDirect.CAC_40(),
			"CAC_NEXT_20": BourseDirect.CAC_NEXT_20(),
			"CAC_MID_60": BourseDirect.CAC_MID_60(),
			"CAC_SMALL": BourseDirect.CAC_SMALL()
			}.items():

			for line in lines:
				TICKER = data_paris.get(line.isin).get("TICKER")
				if not line.isin.startswith("FR"):
					continue
				self.file_enterprise.data[line.isin] = {
					"ISIN": line.isin,
					"TICKER": TICKER,
					"NAME": line.name,
					"INDEX": indice,
					"SECTOR": RendementBourse.find(value=TICKER).get("SECTOR"),
					"HREF_RDMBOURSE": RendementBourse.find(value=TICKER).get("HREF")
				}
		# Supprime les cotations supprimées
		self.file_enterprise.data = {k: v for k, v in self.file_enterprise.data.items() if k in data_paris.keys()}
		# Sauvegarde les fichiers
		self.file_enterprise.save(sort_keys=True)
		pandas.read_json(self.file_enterprise.path).to_csv(f"{self.file_enterprise.path.rsplit('.', maxsplit=1)[0]}.csv", header=False)

	def updateDividend(self):
		# Variable & Lambda
		fdate = lambda txt: datetime.datetime.strptime(txt, "%Y-%m-%d").date()
		findISIN = lambda ticker: {"_": v.get("ISIN") for v in self.file_enterprise.data.values() if v.get("TICKER") in [ticker]}.get("_")
		findHREF = lambda ticker: {"_": v.get("HREF_RDMBOURSE") for v in self.file_enterprise.data.values() if v.get("TICKER") in [ticker]}.get("_")

		for ticker in [v.get("TICKER") for v in self.file_enterprise.data.values()]:
			ISIN = findISIN(ticker=ticker)
			print(ticker)

			# for line in StockEvents.dividend.dividend_history(ticker=ticker):
			for line in RendementBourse.Dividend.dividend(href=findHREF(ticker=ticker)):
				time.sleep(0.02)
				# Variable
				ex_dividend = line.get('EX_DIVIDEND')
				value = line.get('VALUE')

				# Ignore Future Dividende
				if datetime.date.today() < fdate(txt=ex_dividend):
					continue
				# Ajoute les données si la date de dividende n'existe pas déjà et l'affiche
				if self.file_dividend.data.get(ISIN) is None:
					self.file_dividend.data[ISIN] = {}
				if self.file_dividend.data[ISIN].get(ex_dividend) is None:
					data = {
						"ISIN": ISIN,
						"EX_DIVIDEND": ex_dividend,
						"VALUE": value,
						"CHECKED": False
						}
					self.file_dividend.data[ISIN][ex_dividend] = data
					print(f"\t\t{data}")
			# Sauvegarde les fichiers
			self.file_dividend.save(sort_keys=True)
			# Convertie le json et créé le csv
			data = {}
			values = []
			for k, v in self.file_dividend.data.items():
				for m, x in v.items():
					values.append(x)
			for line in values:
				for k, v in line.items():
					if data.get(k) is None:
						data[k] = []
					data[k].append(v)
			pandas.DataFrame(data).to_csv(f"{self.file_dividend.path.rsplit('.', maxsplit=1)[0]}.csv", index=False)


if __name__ == '__main__':
	u = UpdateFiles()
	u.updateEnterprise()
	u.updateDividend()
