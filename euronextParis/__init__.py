
import requests
import json
import pandas as pd


class EuroNextParis:
	def __init__(self):
		self.data = {}
		separator = ";"
		url = "https://live.euronext.com/en/pd_es/data/stocks/download?mics=dm_all_stock&issueType=101&market=18&region=1&tradingLocation=11&country=14%2C220%2C250%2C234%2C243%2C244%2C49%2C58%2C73%2C76%2C79%2C96%2C113%2C124%2C133%2C145%2C172%2C178%2C179%2C198&initialLetter=&fe_type=txt&fe_decimal_separator=%2C&fe_date_format=d%2Fm%2FY"
		response = requests.get(url).text.replace("\ufeff", "").replace('"', "").replace(separator + "'", separator)
		headers = response.splitlines()[0].replace("Symbol", "TICKER").upper().split(separator)

		for row in response.splitlines()[4:]:
			values = row.split(separator)
			self.data[values[1]] = {headers[a]: values[a] for a in range(0, len(values))}
