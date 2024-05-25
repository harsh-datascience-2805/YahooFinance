import requests
import pandas as pd
from io import BytesIO

class NSE():
    def __init__(self, timeout=10) -> None:
        self.base_url = 'https://www.nseindia.com'
        #self.__session = requests.sessions.Session()
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36 Edg/97.0.1072.76",
             "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.9",
             "Accept-Language": "en-US,en;q=0.9"
             }
        self.timeout = timeout
        self.cookies = []


    def __getCookies(self, renew=False):
        if len(self.cookies) > 0 and renew == False:
            return self.cookies
        
        r = requests.get(self.base_url, timeout=self.timeout, headers=self.headers)
        self.cookies = dict(r.cookies)
        return self.__getCookies()
    
    def getHistoricalData(self, symbol, series, from_date, to_date):

        try:
            url = "/api/historical/cm/equity?symbol={0}&series=[%22{1}%22]&from={2}&to={3}&csv=true".format(symbol.replace('&', '%26'), series, from_date.strftime('%d-%m-%Y'), to_date.strftime('%d-%m-%Y'))
            response = requests.get(self.base_url + url, headers=self.headers, timeout=self.timeout, cookies=self.__getCookies())
            
            if response.status_code != 200:
                response = requests.get(self.base_url + url, headers=self.headers, timeout=self.timeout, cookies=self.__getCookies(True))

            df = pd.read_csv(BytesIO(response.content), sep=',', thousands=',')
            response.raise_for_status()  # Raises stored HTTPError, if one occurred.
            df = df.rename(columns={'Date ': 'date', 'series ': 'series', 'OPEN ': 'open', 'HIGH': 'high', 'LOW ': 'low', 
                                    'PREV. CLOSE ': 'prev_close', 'ltp ': 'ltp', 'close ': 'close', '52W H ': 'hi_52_wk', 
                                    '52W L ': 'lo_52_wk', 'VOLUME ': 'trdqty', 'VALUE ': 'value', 'No of trades ': 'trades'})
            df.date = pd.to_datetime(df.date, format='%d-%b-%Y').dt.strftime('%Y-%m-%d')
            return df
        
        except requests.exceptions.HTTPError as errh:
            print("Http Error:", errh)
        except requests.exceptions.ConnectionError as errc:
            print("Error Connecting:", errc)
        except requests.exceptions.Timeout as errt:
            print("Timeout Error:", errt)
        except requests.exceptions.RequestException as err:
            print("Something went wrong", err)
        #except:
            #print('Exepction in getHistoricalData')
        pass
        return None
        

if __name__ == "__main__":
    from datetime import date
    from nse import NSE
    api = NSE()
    df = api.getHistoricalData('SBIN', 'EQ', date(2023, 1, 1), date(2023, 5, 21))
    print(df)