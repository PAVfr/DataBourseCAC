
import pandas
import datetime

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
		# Variables
		secteurs = {k: [c.ticker for c in v] for k, v in RendementBourse.sector.all_sector().items()}
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
				self.file_enterprise.data[line.isin] = {
					"ISIN": line.isin,
					"TICKER": TICKER,
					"NAME": line.name,
					"INDEX": indice,
					"SECTOR": {"_": k for k, v in secteurs.items() if TICKER in v}.get("_"),
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

		for ticker in [v.get("TICKER") for v in self.file_enterprise.data.values()]:
			ISIN = findISIN(ticker=ticker)
			print(ticker)
			for line in StockEvents.dividend.dividend_history(ticker=ticker):
				# Variable
				ex_dividend = line.get('date_ex_dividend')
				date_payement = line.get("date_payement")
				value = float(line.get('value').replace(",", "."))

				# Ignore Future Dividende
				if datetime.date.today() < fdate(txt=ex_dividend):
					continue

				if self.file_dividend.data.get(ISIN) is None:
					self.file_dividend.data[ISIN] = {}
				self.file_dividend.data[ISIN][ex_dividend] = {
					"ISIN": ISIN,
					"EX_DIVIDEND": ex_dividend,
					"DATE_PAYEMENT": date_payement,
					"VALUE": float(value)
					}
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
