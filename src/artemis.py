import time
from binance.client import Client
from datetime import datetime
from datetime import timedelta
from artemis_config import API_KEY, API_SECRET_KEY, gainpercentage, losspercentage, walletpercentage
client = Client(API_KEY, API_SECRET_KEY)

def long():
  client.futures_cancel_all_open_orders(symbol="BTCUSDT")
  balance=float(client.futures_account_balance()[1]["balance"])*walletpercentage/100
  price1=float(client.futures_mark_price(symbol= "BTCUSDT")["markPrice"])
  order = client.futures_create_order(symbol="BTCUSDT", side="BUY", type="MARKET", quantity=float(str(balance*leverage/price1)[0:5]))
  price2=float(client.futures_mark_price(symbol= "BTCUSDT")["markPrice"])
  price=(price1+price2)/2
  TAKEPROFIT = client.futures_create_order(symbol="BTCUSDT", side="SELL", type="TAKE_PROFIT_MARKET", stopPrice=int(price+(price-price*(1-0.01*gainpercentage))/leverage), closePosition=True)
  STOP = client.futures_create_order(symbol="BTCUSDT", side="SELL", type="STOP_MARKET", stopPrice=int(price-(price-price*(1-0.01*losspercentage))/leverage), closePosition=True)
  return str(datetime.now())[0:19] + " - Long position opened"

def short():
  client.futures_cancel_all_open_orders(symbol="BTCUSDT")
  balance=float(client.futures_account_balance()[1]["balance"])*walletpercentage/100
  price1=float(client.futures_mark_price(symbol= "BTCUSDT")["markPrice"])
  order = client.futures_create_order(symbol="BTCUSDT", side="SELL", type="MARKET", quantity=float(str(balance*leverage/price1)[0:5]))
  price2=float(client.futures_mark_price(symbol= "BTCUSDT")["markPrice"])
  price=(price1+price2)/2
  STOP = client.futures_create_order(symbol="BTCUSDT", side="BUY", type="STOP_MARKET", stopPrice=int(price+(price-price*(1-0.01*losspercentage))/leverage), closePosition=True)
  TAKEPROFIT = client.futures_create_order(symbol="BTCUSDT", side="BUY", type="TAKE_PROFIT_MARKET", stopPrice=int(price-(price-price*(1-0.01*gainpercentage))/leverage), closePosition=True)
  return str(datetime.now())[0:19] + " - Short position opened"

def ordermonitor():
  print("Monitoring the position")
  start = time.time()
  while True:
    order=client.futures_get_open_orders(symbol="BTCUSDT")
    if len(order) == 1:
      if order[0]["type"] == "STOP_MARKET":
        print("Take profit triggered. Position closed")
        elapsed = (time.time() - start)
        print("Duration: " + str(timedelta(seconds=elapsed))[2:4] + " minutes and " + str(timedelta(seconds=elapsed))[5:7] + " seconds")
        trades=register_trades(True)
        return "Winrate: " + str(round(100*trades[0]/(trades[0]+trades[1]), 2)) + "%"
      elif order[0]["type"] == "TAKE_PROFIT_MARKET":
        print("Stop loss triggered. Position closed")
        elapsed = (time.time() - start)
        print("Duration: " + str(timedelta(seconds=elapsed))[2:4] + " minutes and " + str(timedelta(seconds=elapsed))[5:7] + " seconds")
        trades=register_trades(False)
        return "Winrate: " + str(round(100*trades[0]/(trades[0]+trades[1]), 2)) + "%"
    elif len(order) == 0:
      return "Position closed manually"
    else:
      time.sleep(10)

def register_trades(win):
    text = open("winrate.txt", "r")
    list_of_lines = text.readlines()
    wins = int(list_of_lines[0][0:-1])
    losses = int(list_of_lines[1])
    if win == True:
        wins+=1
        list_of_lines[0] = str(wins) + "\n"
    if win == False:
        losses+=1
        list_of_lines[1] = str(losses)
    text = open("winrate.txt", "w")
    text.writelines(list_of_lines)
    text.close()
    return (wins, losses)

def welcome_msg():
    print("""       =========================================\n
        ARTEMIS v0.0.1 - Binance Futures script\n
       =========================================\n\n
        You can find more help at: https://github.com/almeidath/artemis\n
        Make sure you are using the latest version\n\n\n""")

if __name__=="__main__":
  welcome_msg()
  leverage=int(input("Type the leverage you are using on BTCUSDT Perpetual: "))
  print()
  while True:
    start = int(input("Type 1 for long, 2 for short or just press enter to exit: "))
    if start == 1:
      print(long())
      print(ordermonitor())
    elif start == 2:
      print(short())
      print(ordermonitor())
    else:
      exit()
    print()
