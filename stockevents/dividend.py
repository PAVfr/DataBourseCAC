
from options import Options

import re
import time
import datetime


class Dividend:
	URL = "https://stockevents.app"

	@classmethod
	def dividend_history(cls, ticker: str):
		print(ticker)

		values = []
		soup = Options.requestGet(f"{cls.URL}/fr/stock/{ticker}.PA")
		lines = [element for element in soup.find_all("a", href=True) if element.get("href").startswith("/fr/event/dividends/") and element.get("target") is None]

		for line in lines:
			data = {
				"TICKER": ticker,
				"HREF": line.get("href"),
				"VALUE": line.find_all("span")[-1].text.replace(".", ",").replace("€", ""),
				}
			data.update(cls.getInfos(href=line.get("href")))
			values.insert(0, data)
			time.sleep(0.1)

			break

		return values

	@classmethod
	def getInfos(cls, href: str):
		"""
		date_ex_dividend = date à partir de laquelle elle est cotée sans le droit au dividende à venir
		date_payement = date de payement du dividende
		"""
		soup = Options.requestGet(f"{cls.URL}{href}")

		# Ex Dividende
		date_ex_dividend = None
		for line in soup.find_all("div", attrs={"class": "flex flex-1 flex-col text-left"}):
			titre = line.find("p", attrs={"class": "font-manrope font-bold text-lg leading-snug"}).text
			date = line.find("p", attrs={"class": "font-manrope text-base text-gray-500 leading-snug"}).text.split("•")[-1]
			if titre == "Date d'Ex-dividende":
				date_ex_dividend = cls._format_date(date)
				break
		if date_ex_dividend is None:
			raise Exception(f"{cls.URL}{href}")

		# Date Paiement
		try:
			date_paye = soup.select_one("""#app > div > div.max-w-5xl.mx-auto.py-12.min-h-screen.px-2 > div > 
				div.col-span-3.md\:col-span-2 > div.relative > div.flex > div.flex.flex-col.text-left > 
				p""").text.split("•")[-1]
			date_paye = cls._format_date(date_paye)
		except ValueError:
			date_paye = "N/A"

		return {
			"EX_DIVIDEND": date_ex_dividend,
			"PAYEMENT": date_paye
			}

	@classmethod
	def _format_date(cls, txt: str):
		txt = txt.strip()
		txt = txt.replace(",", "")
		# MOIS
		data = {
			"janvier": "01",
			"février": "02",
			"mars": "03",
			"avril": "04",
			"mai": "05",
			"juin": "06",
			"juillet": "07",
			"août": "08",
			"septembre": "09",
			"octobre": "10",
			"novembre": "11",
			"décembre": "12"
			}
		mois = txt.split(" ", maxsplit=1)[0]
		for k, v in data.items():
			mois = mois.replace(k, v)
		# Date
		jour = txt.split(" ")[1]
		annee = txt.split(" ")[-1]
		return datetime.datetime.strptime(f"{jour}/{mois}/{annee}", "%d/%m/%y").strftime("%Y-%m-%d")


if __name__ == '__main__':
	href = "/fr/event/dividends/33417389"
	div = Dividend.dividend_history(ticker="ORA")
	# div = Dividend.getInfos(href=href)
	print(div)
