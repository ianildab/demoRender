from flask import Flask
import hashlib

app = Flask(__name__)
app_secret = "DIJNYWXSFG"
redirect_uri = "https://trade.fyers.in/api-login/redirect-uri/index.html"
fyers_id = "XD18596"
pin = "7751"
client_id = "X4LLCSVYTL-100"
app_id = "X4LLCSVYTL"
TOTP_KEY = "NRLLLUV5QNJ4M2QCG3CEJHYVR62OURPE"  # TOTP secret is generated when we enable 2Factor TOTP from myaccount portal

APP_ID_TYPE = "2"  # Keep default as 2, It denotes web login
APP_TYPE = "100"
APP_ID_HASH = '0a65c9c558660b48ff9a8314661848de9c78973787fef825da490df2eb56ad15'

# API endpoints
BASE_URL = "https://api-t2.fyers.in/vagator/v2"
BASE_URL_2 = "https://api.fyers.in/api/v2"
URL_SEND_LOGIN_OTP = BASE_URL + "/send_login_otp"
URL_VERIFY_TOTP = BASE_URL + "/verify_otp"
URL_VERIFY_PIN = BASE_URL + "/verify_pin"
URL_TOKEN = BASE_URL_2 + "/token"
URL_VALIDATE_AUTH_CODE = BASE_URL_2 + "/validate-authcode"

SUCCESS = 1
ERROR = -1
@app.route('/')
def getTime():
    return datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

def maAlgorithm():
    #Identify ATM Strike 
    SPOT_SYMBOL='NSE:NIFTYBANK-INDEX'
    SYMBOL={'symbols':SPOT_SYMBOL}
    LAST_PRICE=fyers.quotes(SYMBOL)['d'][0]['v']['lp']
    ATM_STRIKE=100*round(LAST_PRICE/100)
    print('#ATM_STRIKE :'+str(ATM_STRIKE) + ' #Time : ' +getTime())
    #Required Variables
    EXCHANGE = "NSE"
    QUANTITY = int(15)
    TIMEFRAME = "5"
    #FROM_DATE = "2023-07-01"
    TODAY = datetime.datetime.now().strftime('%Y-%m-%d') #"2022-03-14"
    BANKNIFTY = 'BANKNIFTY'
    #DATE_STRIKE = str('23920')
    DATE_STRIKE = str('23SEP')
    CE = 'CE'
    PE = 'PE'
    #BANKNIFTY23JUN43700CE - Monthly expiry format
    # 23622 - weekly expiry format
    CE_STRIKE = BANKNIFTY+DATE_STRIKE+str(ATM_STRIKE)+CE
    PE_STRIKE = BANKNIFTY+DATE_STRIKE+str(ATM_STRIKE)+PE
    #print(CE_STRIKE + PE_STRIKE)

    script_list = [CE_STRIKE,PE_STRIKE]

    exchange = "NSE"
    quantity = int(100)
    timeframe = "5"
    from_date = "2023-09-01"
    today = datetime.datetime.now().strftime('%Y-%m-%d') #"2022-03-14"
    buy_traded_stock = []
    sell_traded_stock = []
    for script in script_list:
        data = {"symbol":f"{exchange}:{script}","resolution": timeframe,"date_format":"1","range_from": from_date,"range_to": today,"cont_flag":"0"}
        try:
            #hist_data = fyers.history(data)
            nx = fyers.history(data)
        except Exception as e:
            raise e
        #data = {"symbol":f"{exchange}:{script}","resolution":"5","date_format":"1","range_from":"2023-06-16","range_to":"2023-06-16","cont_flag":"1"}
        #nx = fyers.history(data)

        cols = ['datetime','open','high','low','close','volume']
        df = pd.DataFrame.from_dict(nx['candles'])
        #print(df)
        df.columns = cols
        df['datetime'] = pd.to_datetime(df['datetime'],unit = "s")
        df['datetime'] = df['datetime'].dt.tz_localize('utc').dt.tz_convert('Asia/Kolkata')
        df['datetime'] = df['datetime'].dt.tz_localize(None)
        df = df.set_index('datetime')
        
        df['VWAP'] = ta.vwap(df.high,df.low,df.close,df.volume)
        df['CCI'] = ta.cci(df.high,df.low,df.close,20,0.015,'false',0)
        df['RSI'] = ta.rsi(df.close,14,100,'false',1,0)
        df.dropna(inplace=True)
        if not df.empty:
            #print(df)
            if ((df.close[-1] > df.VWAP.values[-1]) and (df.close[-2] < df.VWAP.values[-2]) and (df.CCI.values[-1] > 100) and (df.RSI.values[-1] > 45)) :
            #if ((df.CCI.values[-1] > 0) and (df.RSI.values[-1] > 0)) :
                print(script + ' '+str(datetime.datetime.now()))
                message = 'VWAP and CCI>100 and RSI>45 : '+script
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message}"
                #requests.get(url).json()
                
                tsl_point = 20
                order_id = {
                  "symbol":f"{EXCHANGE}:{script}",
                  "qty":90,
                  "type":2,
                  "side":1,
                  "productType":"MARGIN",
                  "limitPrice":0,
                  "stopPrice":0,
                  "validity":"DAY",
                  "disclosedQty":0,
                  "offlineOrder":"False",
                  "stopLoss":0,
                  "takeProfit":0
                }
                order_executed_id = fyers.place_order(order_id)
                
                SPOT_SYMBOL=f'NSE:{script}'
                SYMBOL={'symbols':SPOT_SYMBOL}
                LAST_PRICE=fyers.quotes(SYMBOL)['d'][0]['v']['lp']
                print('In maAlgorithm : order_executed:')
                
                trailing_stop_loss_live(script, LAST_PRICE,tsl_point,True)
                
                notify2.init("Test")
                notice = notify2.Notification(script, message)
                notice.show()
                
                message1 = 'Order done for : '+script
                url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message1}"
                requests.get(url).json()
                
                
def trailing_stop_loss_live(script, buy_price,tsl_point,orderExecuted):
    new_tsl_price = buy_price - tsl_point
    print('new_tsl_price : '+str(new_tsl_price))
    print(buy_price)
    print('Buy Price : '+str(buy_price))
    print('order_executed_id : '+order_executed_id['id'])
            
    while orderExecuted:
        SPOT_SYMBOL=f'NSE:{script}'
        SYMBOL={'symbols':SPOT_SYMBOL}
        LAST_PRICE=fyers.quotes(SYMBOL)['d'][0]['v']['lp']
        
        old_ltp = new_tsl_price + tsl_point

        if(LAST_PRICE > old_ltp):
            old_ltp = LAST_PRICE
            new_tsl_price = old_ltp - tsl_point
            print('New Trailing SL : '+str(new_tsl_price))
            message1 = 'New trailing stoploss for : '+script+ ' is '+ str(new_tsl_price)
            url = f"https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={chat_id}&text={message1}"
            requests.get(url).json()


        if(new_tsl_price > LAST_PRICE):
            scrip = SPOT_SYMBOL+'-MARGIN'
            print(fyers.exit_positions({"id":scrip}))
            orderExecuted = False
            print('Trailing Stoploss Hit :')
            
        time.sleep(1)    
        


def main():
    global fyers
    token = 'eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9.eyJpc3MiOiJhcGkuZnllcnMuaW4iLCJpYXQiOjE2OTU3NDk2ODEsImV4cCI6MTY5NTc3NDY0MSwibmJmIjoxNjk1NzQ5NjgxLCJhdWQiOlsieDowIiwieDoxIiwieDoyIiwiZDoxIiwiZDoyIiwieDoxIiwieDowIl0sInN1YiI6ImFjY2Vzc190b2tlbiIsImF0X2hhc2giOiJnQUFBQUFCbEV4WXhwaG83d0hId3N4SWF1ek9CR0hzY2JBUnVKYkRyUkg3dTg2UUhaQ3o2MDNlVXo1UzhPVkp2cDB5dFZXMnV4OWhLYml0czliY2N3LXpfaGU3RC1HRVZaTWZEYU93amhBMy1LenlBdmxxRHpTOD0iLCJkaXNwbGF5X25hbWUiOiJESVBBTEkgQU5JTCBKQURIQVYiLCJvbXMiOiJLMSIsImhzbV9rZXkiOiJkYTgwYjAzZjE3ZWRiMjEzNmE0MTdhZDlhNjc3YjQ1NTk2ODJjZGY3ZWYwOTc1ZDY0NDAwYTdlMSIsImZ5X2lkIjoiWEQxODU5NiIsImFwcFR5cGUiOjEwMCwicG9hX2ZsYWciOiJOIn0.aBNapnC_F2HkwxgdSRVIC1J5PcWhVedSSys7I0JU21E'
    fyers = fyersModel.FyersModel(client_id=client_id, token=token, log_path='/tmp/')
    closingtime = int(15) * 60 + int(10)
    orderplacetime = int(9) * 60 + int(20)
    timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
    print(f"Waiting for 9.30 AM , Time Now:{getTime()}")

    while timenow < orderplacetime:
        time.sleep(0.2)
        timenow = (datetime.datetime.now().hour * 60 + datetime.datetime.now().minute)
    print(f"Ready for trading, Time Now:{getTime()}")
    
    while True: 
        maAlgorithm()
        time.sleep(60)
        
if __name__ == '__main__':
    
    token = get_auth_code()
    fyers = fyersModel.FyersModel(client_id=client_id, token=token, log_path='/tmp/')
    app.run()
