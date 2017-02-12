import requests, time, pickle
from lxml import html

urlJSON = "http://www.saltybet.com/state.json"
urlWEB = "http://www.saltybet.com/"
urlLOGIN = 'http://www.saltybet.com/authenticate?signin=1'
urlBET = 'http://www.saltybet.com/ajax_place_bet.php'

win_pct = {'win':0,'loss':0};

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

def waitForNewData(s):
    data = requests.get(urlJSON).json()
    while data['status'] != 'open':
        data = requests.get(urlJSON).json()
        time.sleep(2)
        print("Waiting for bet start")
    time.sleep(3)
    return data

def waitForMatchStart():
    data = requests.get(urlJSON).json()
    while data['status'] != 'locked':
        data = requests.get(urlJSON).json()
        time.sleep(2)
        print("Waiting for match start")
    return

def getBalance(r):
    tree = html.fromstring(r.content)
    return tree.xpath('//span[@class="dollar"]/text()')[0]

def bet(data):
    
   # if(p1):
    bet_payload['selectedplayer'] = 'player1'
   # else
       # bet_payload['player2'] = data['p2name']


betting_data = openBettingData()

s = requests.session()

results = s.get(urlLOGIN)
results = s.post(urlLOGIN, login_payload, dict(referer = urlLOGIN))

data = requests.get(urlJSON).json()
balance = getBalance(results)

while(True):
    
    results = s.get(urlWEB)
    

    balance_new = getBalance(results)
    
    print(betting_data)
    
    p1 = data['p1name']
    p2 = data['p2name']
    
    if balance < balance_new:
        win_pct['win'] = win_pct['win'] + 1
        if p1 not in betting_data:
            betting_data[p1] = []
            
        betting_data[p1].append(p2)
    elif balance > balance_new:
        win_pct['loss'] = win_pct['loss'] + 1
        if p2 not in betting_data:
            betting_data[p2] = []
            
        betting_data[p2].append(p1)

    balance = balance_new
    
    data = waitForNewData(s)
    
    r_bet = s.post(urlBET,bet_payload, headers)
    print(r_bet.status_code, r_bet.reason)
    print(getBalance(results))
    print(win_pct)
    print(betting_data)
    waitForMatchStart()
    saveBettingData()


#data = waitForNewData()


#p1 = data['p1name']
#p2 = data['p2name']
#print(p1,p2)






    
