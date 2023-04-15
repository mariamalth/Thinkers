import random
import time
import requests
import pandas as pd

from pythonosc import udp_client

port = 5005
ip = '127.0.0.1'

def getWeatherData(ranking):
#   payload = {'appid': '[YOUR APP ID]', 'q': city}
#   r = requests.get('https://api.openweathermap.org/data/2.5/weather', params=payload)
#   res = r.json()
  res = pd.read_csv("leaderboard.csv")
  return res['Username'][ranking]

if __name__ == "__main__":
  client = udp_client.SimpleUDPClient(ip, port)
  while(True):
    # taipei = getWeatherData('Taipei')
    # tokyo = getWeatherData('Tokyo')
    # berlin = getWeatherData('Berlin')
    # new_york = getWeatherData('New York')
    first_place = getWeatherData(0)
    second_place = getWeatherData(1)
    third_place = getWeatherData(2)
    client.send_message("/first_place",first_place)
    client.send_message("/second_place",second_place)
    client.send_message("/third_place",third_place)
    # client.send_message("/taipei", taipei['wind']['speed'])
    # client.send_message("/tokyo", tokyo['wind']['speed'])
    # client.send_message("/berlin", berlin['wind']['speed'])
    # client.send_message("/new_york", new_york['wind']['speed'])
    time.sleep(1)