import requests
import pandas as pd
import requests
import pandas as pd
from dateutil import parser

class OptionChain:
    def __init__(self, symbol='NIFTY', series='indices', timeout=5) -> None:
        self.__url ="https://www.nseindia.com/api/option-chain-{0}?symbol={1}".format(series, symbol.replace('&', '%26'))
        self.__session = requests.sessions.Session()
        self.__session.headers = {
            "User-Agent": "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:89.0) Gecko/20100101 Firefox/89.0", "Accept": "*/*", "Accept-Language": "en-US,en;q=0.5"
        }
        self.__timeout = timeout
        self.__session.get("https://www.nseindia.com/option-chain", timeout=self.__timeout)
    
    def fetch_data(self, expiry_date=None, starting_strike_price=None, number_of_rows=2):
        try:
            data = self.__session.get(url=self.__url, timeout=self.__timeout)
            data = data.json()
            df = pd.json_normalize(data['records']['data'])

            if expiry_date is not None:
                df = df[df['expiryDate'] == expiry_date]

            if starting_strike_price is not None:
                df = df[df['strikePrice'] >= starting_strike_price][:number_of_rows]

            return df

        except Exception as ex:
            print('Error: {}'.format(ex))
            self.__session.get("https://www.nseindia.com/api/option-chain", timeout=self.__timeout)
            return None

def convert_date_format(date_string):
    # Try to automatically infer the format of the input date
    date_object = parser.parse(date_string)
    
    # Convert the date object to the desired format
    formatted_date = date_object.strftime('%d-%b-%Y')
    
    return formatted_date        

if __name__ == "__main__":
    symbol = input("Enter symbol: ")
    expiry_date = input("Enter expiry date: ")
    series = input("Is it equity? (Y/N): ")
    expiry_date = convert_date_format(expiry_date)
    if series.upper() == "Y":
        objeq = OptionChain(series='equities', symbol=symbol)
        df = objeq.fetch_data(expiry_date=expiry_date)
    else:
        objid = OptionChain(symbol=symbol)
        df = objid.fetch_data(expiry_date=expiry_date)

    print(df)
    print("Symbol:", symbol)
    print("Expiry Date:", expiry_date)

# Find corresponding CE.lastPrice and PE.lastPrice for max CE.openInterest and PE.openInterest
max_ce_oi = df['CE.openInterest'].max()
max_pe_oi = df['PE.openInterest'].max()

ce_strike_price = df.loc[df['CE.openInterest'] == max_ce_oi, 'CE.strikePrice'].values[0]
pe_strike_price = df.loc[df['PE.openInterest'] == max_pe_oi, 'PE.strikePrice'].values[0]

ce_last_price = df.loc[df['CE.openInterest'] == max_ce_oi, 'CE.lastPrice'].values[0]
pe_last_price = df.loc[df['PE.openInterest'] == max_pe_oi, 'PE.lastPrice'].values[0]

# Print support and resistance level
print("Support Level: {:.2f}".format(ce_strike_price + (ce_last_price + pe_last_price)))
print("Resistance Level: {:.2f}".format(pe_strike_price - (pe_last_price + ce_last_price)))

# Calculate PCR ratio
pcr_ratio = df['PE.openInterest'].sum() / df['CE.openInterest'].sum()
print("PCR Ratio: {:.2f}".format(pcr_ratio))

if pcr_ratio > 1.8:
    print("Market sentiment is extream bearish (over bought), posibility of correction don't place buy orders.")
elif pcr_ratio > 1.5 and pcr_ratio < 1.8:
    print("Market sentiment is very bearish.")
elif pcr_ratio > 1.2 and pcr_ratio < 1.5:
        print("Market sentiment is bearish.")
elif pcr_ratio > 0.8 and pcr_ratio < 1.2:
        print("Market sentiment is neutral.")
elif pcr_ratio > 0.5 and pcr_ratio < 0.8:
        print("Market sentiment is bearish.")
elif pcr_ratio > 0.2 and pcr_ratio < 0.5:
        print("Market sentiment is very bearish.")
else:
    print("Market sentiment is extream bearish (over sold), posibility of correction don't place sell orders.")
