
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
		self.file_enterprise = EasyFileJson(f"enterprise.json")
		self.file_dividend = EasyFileJson(f"dividend.json")
		RendementBourse.Sector.all_sector()

	def updateEnterprise(self):
		index = {i: [v.isin for v in values] for i, values in {
			"CAC_40": BourseDirect.CAC_40(),
			"CAC_NEXT_20": BourseDirect.CAC_NEXT_20(),
			"CAC_MID_60": BourseDirect.CAC_MID_60(),
			"CAC_SMALL": BourseDirect.CAC_SMALL()}.items()}

		data = {}
		for isin, value in EuroNextParis().data.items():
			data[isin] = {
				"ISIN": value.get("ISIN"),
				"TICKER": value.get("TICKER"),
				"NAME": value.get("NAME"),
				"SECTOR": RendementBourse.find(value=value.get("TICKER")).get("SECTOR"),
				"INDEX": {"_": k for k, v in index.items() if isin in v}.get("_")
				}
		# JSON
		self.file_enterprise.data = data
		self.file_enterprise.save(sort_keys=False)
		# CSV
		data = {}
		values = []
		for m, x in self.file_enterprise.data.items():
			values.append(x)
		for line in values:
			for k, v in line.items():
				if data.get(k) is None:
					data[k] = []
				data[k].append(v)
		pandas.DataFrame(data).to_csv(f"{self.file_enterprise.path.rsplit('.', maxsplit=1)[0]}.csv", index=False)

	def updateDividend(self, forced_check: bool = False):
		self.file_enterprise.load()
		self.file_dividend.load()
		# Variable & Lambda
		fdate = lambda txt: datetime.datetime.strptime(txt, "%Y-%m-%d").date()
		findISIN = lambda ticker: {"_": v.get("ISIN") for v in self.file_enterprise.data.values() if v.get("TICKER") in [ticker]}.get("_")
		findHREF = lambda ticker: RendementBourse.find(value=ticker).get("HREF")
		forced_check = True if len(self.file_dividend.data.keys()) == 0 else forced_check

		for ticker in [v.get("TICKER") for v in self.file_enterprise.data.values()]:
			ISIN = findISIN(ticker=ticker)

			if ISIN not in self.file_dividend.data.keys() and forced_check in [None, False]:
				continue

			print(ticker)

			# Recherche les dividendes sur RendementBourse, puis sur StockEvents si inexistant sur le premier.
			lines = RendementBourse.Dividend.dividend(href=findHREF(ticker=ticker))
			if not lines:
				for v in StockEvents.dividend.dividend_history(ticker=ticker):
					lines.append(v)

			for line in lines:
				time.sleep(0.02)
				# Variable
				ex_dividend = line.get('EX_DIVIDEND')
				value = line.get('VALUE')

				# Ignore les dividendes Passé
				last_div = datetime.date(1900, 1, 1)
				if self.file_dividend.data.get(ISIN):
					last_div = fdate(list(self.file_dividend.data[ISIN].keys())[-1]) + datetime.timedelta(days=7)
				if fdate(txt=ex_dividend) < last_div:
					continue
				# Ignore les dividendes Future
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

				# JSON
				self.file_dividend.save(sort_keys=True)
			# CSV
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

	def test(self):
		ticker = "ORA"

		self.file_enterprise.load()
		self.file_dividend.load()
		fdate = lambda txt: datetime.datetime.strptime(txt, "%Y-%m-%d").date()
		findISIN = lambda ticker: {"_": v.get("ISIN") for v in self.file_enterprise.data.values() if v.get("TICKER") in [ticker]}.get("_")
		ISIN = findISIN(ticker=ticker)

		last_div = fdate(self.file_dividend.data[ISIN].popitem()[0]) + datetime.timedelta(days=7)
		print(last_div)
		# 2024-06-05


if __name__ == '__main__':
	u = UpdateFiles()
	# u.updateEnterprise()
	u.updateDividend()
	# u.test()
