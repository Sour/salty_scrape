import requests, time, pickle
from lxml import html

urlJSON = "http://www.saltybet.com/state.json"
urlWEB = "http://www.saltybet.com/"
urlLOGIN = 'http://www.saltybet.com/authenticate?signin=1'
urlBET = 'http://www.saltybet.com/ajax_place_bet.php'

login_payload = {
    'email': "mechanicfreak440@gmail.com",
    'pword': 'lolice440',
    'authenticate': 'signin'
    }
bet_payload = {
    'selectedplayer': 'player1',
    'wager': '100',
    }
headers = {
    'Host': 'www.saltybet.com',
    'Connection': 'keep-alive',
    'Content-Length': '32',
    'Accept': '*/*',
    'Origin': 'http://www.saltybet.com',
    'X-Requested-With': 'XMLHttpRequest',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/56.0.2924.87 Safari/537.36',
    'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
    'DNT': '1',
    'Referer': 'http://www.saltybet.com/',
    'Accept-Encoding': 'gzip, deflate',
    'Accept-Language': 'en-US,en;q=0.8,ja;q=0.6',
    'Cookie': '__cfduid=d9298001d3c60b3bc2b5d51465e8b7b241486695449; PHPSESSID=ekpuf9gt5pq9boggvvgakkact6'
    }

def saveBettingData():
    with open('betting_data.pickle','wb') as f:
        pickle.dump(betting_data, f)

def openBettingData():
    with open('betting_data.pickle', 'rb') as f:
        return pickle.load(f)

def waitForMatchEnd(s):
    print("\nWaiting for bet start")
    data = requests.get(urlJSON).json()
    while data['status'] == 'locked':
        data = requests.get(urlJSON).json()
        time.sleep(2)
    time.sleep(3)
    return data

def waitForMatchStart():
    print("\nWaiting for match start")
    data = requests.get(urlJSON).json()
    while data['status'] != 'locked':
        data = requests.get(urlJSON).json()
        time.sleep(2)
    return

def getBalance(r):
    tree = html.fromstring(r.content)
    return tree.xpath('//span[@class="dollar"]/text()')[0]

def bet(p1,p2):
    
    if p1 in betting_data:
        count_p1 = betting_data[p1].count(p2)

    if p2 in betting_data:
        count_p2 = betting_data[p2].count(p2)

    if count_p1 >= count_p2:
        bet_payload['selectedplayer'] = 'player1'
    else:
        bet_payload['selectedplayer'] = 'player2'

betting_data = openBettingData()

s = requests.session()
results = s.get(urlLOGIN)

#login
results = s.post(urlLOGIN, login_payload, dict(referer = urlLOGIN))

data = requests.get(urlJSON).json()
balance = getBalance(results)

p1 = data['p1name']
p2 = data['p2name']

if p1 not in betting_data:
    betting_data[p1] = []
if p2 not in betting_data:
    betting_data[p2] = []

while(True):  
    data = waitForMatchEnd(s)

    results = s.get(urlWEB)
    
    balance = getBalance(results)

    if data['status'] == '1':
        win_pct['win'] = win_pct['win'] + 1
        betting_data[p1].append(p2)
        print(p1," won!")
               
    if data['status'] == '2':
        win_pct['loss'] = win_pct['loss'] + 1
        betting_data[p2].append(p1)
        print(p2," won!")
    
    saveBettingData()
    
    data = requests.get(urlJSON).json()
    
    p1 = data['p1name']
    p2 = data['p2name']
    if p1 not in betting_data:
        betting_data[p1] = []
    if p2 not in betting_data:
        betting_data[p2] = []
        
    bet(p1,p2)
    print(data['p1name'], " vs ", data['p2name'])
    print(p1,": ",betting_data[p1])
    print(p2,": ",betting_data[p2])
    
    print("\nSent POST: ",bet_payload)
    
    r_bet = s.post(urlBET,bet_payload, headers)
    
    print("POST Response:", r_bet.status_code, r_bet.reason,"\n")

    print(betting_data)
    waitForMatchStart()






    
