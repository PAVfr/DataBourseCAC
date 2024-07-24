
import re

from options import Options


class Dividend:
	@classmethod
	def dividend(cls, url: str) -> list[dict]:
		values = []
		try:
			response = Options.requestGet(url)
			selector_isin = "#app > main > div.mb-4.py-3 > div > div.col-lg-5.col-xl-4 > div:nth-child(4) > div:nth-child(2) > section:nth-child(11) > div > div > p"
			ISIN = response.select_one(selector_isin).text.replace("  ", "").splitlines()[-1].replace(".", "").rsplit(maxsplit=1)[-1]

			index_ex_div = 1
			index_value = 2
			table = response.find("table", id="allDivs")
			tr = [v.text.replace("\n", ";").replace("  ", "").replace("\xa0€", "") for v in table.find_all("tr")[1:]]
			for line in [[x for x in v.split(";") if x] for v in tr]:
				if re.match(r"\d+,\d+", line[index_value]):
					EX_DIVIDEND = line[index_ex_div]
					values.append({
						"ISIN": ISIN,
						"EX_DIVIDEND": EX_DIVIDEND,
						"VALUE": line[index_value]
						})
		except AttributeError:
			pass
		return values


if __name__ == '__main__':
	div = Dividend()
	# r = div.dividend(url="https://rendementbourse.com/bnp-bnp-paribas/dividendes")
	r = div.dividend(url="https://rendementbourse.com/ovh-ovh-group-sas/dividendes")
	print(r)
