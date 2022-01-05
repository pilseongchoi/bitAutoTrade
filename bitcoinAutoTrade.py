import time
import pyupbit
import datetime
import requests

access = "oPxp9q8TTiLX6oKLw9XE7LcPOfJmQ5xybjX5ojZs"          # 본인 값으로 변경
secret = "ALKsz4UxTvGUfP8A4IgelYxCOnRxyjb8Tcu75mxx"          # 본인 값으로 변경
myToken = "xoxb-2254769221553-2242120269186-T2xiWO1onhax1k0DjMalBCKb"

def post_message(token, channel, text):
    """슬랙 메시지 전송"""
    response = requests.post("https://slack.com/api/chat.postMessage",
        headers={"Authorization": "Bearer "+token},
        data={"channel": channel,"text": text}
    )

def get_target_price(ticker, k):
    """변동성 돌파 전략으로 매수 목표가 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=2)
    target_price = df.iloc[0]['close'] + (df.iloc[0]['high'] - df.iloc[0]['low']) * k
    return target_price

def get_start_time(ticker):
    """시작 시간 조회"""
    df = pyupbit.get_ohlcv(ticker, interval="day", count=1)
    start_time = df.index[0]
    return start_time

def get_balance(ticker):
    """잔고 조회"""
    balances = upbit.get_balances()
    for b in balances:
        if b['currency'] == ticker:
            if b['balance'] is not None:
                return float(b['balance'])
            else:
                return 0
    return 0

def get_current_price(ticker):
    """현재가 조회"""
    return pyupbit.get_orderbook(ticker=ticker)["orderbook_units"][0]["ask_price"]

# 로그인
upbit = pyupbit.Upbit(access, secret)
print("autotrade start")
# 시작 메세지 슬랙 전송
post_message(myToken,"#stock", "autotrade start")

portfolio = pyupbit.get_tickers(fiat="KRW")

# 자동매매 시작
while True:
    try:
        now = datetime.datetime.now()
        start_time = get_start_time("KRW-BTC")
        end_time = start_time + datetime.timedelta(days=1)

        for i in portfolio:    
            if start_time < now < end_time - datetime.timedelta(seconds=300):                 
                target_price = get_target_price(i, 0.7)
                current_price = get_current_price(i)
                df = pyupbit.get_ohlcv(i, count=1)
                high_price = df.iloc[0][2]    
                
                if target_price < current_price:
                    krw = get_balance("KRW")                 
                    
                    if current_price == high_price and krw > 5000:
                        buy_result = upbit.buy_market_order(i, krw*0.9995)
                        post_message(myToken,"#stock", " buy : " +str(buy_result))
                        
                        portfolio.remove(i)      
            else:
                portfolio = pyupbit.get_tickers(fiat="KRW")
                        
            time.sleep(1)
            
    except Exception as e:
        print(e)
        post_message(myToken,"#stock", e)
        time.sleep(1)