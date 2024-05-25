import requests
import pandas as pd

class OptionChain:
    def __init__(self, symbol='NIFTY', timeout=5) -> None:
        self.__url ="https://www.nseindia.com/api/option-chain-indices?symbol={}".format(symbol)
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
        

if __name__ == "__main__":
    obj = OptionChain(symbol='BANKNIFTY')
    df = obj.fetch_data(expiry_date='29-May-2024')
    print(df)