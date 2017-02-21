import requests, time, pickle
from lxml import html
from character import Character

urlJSON = "http://www.saltybet.com/state.json"
urlWEB = "http://www.saltybet.com/"
urlLOGIN = 'http://www.saltybet.com/authenticate?signin=1'
urlBET = 'http://www.saltybet.com/ajax_place_bet.php'

login_payload = {}

bet_payload = {
    'selectedplayer': 'player1',
    'wager': '300',
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
        f.close()

def openBettingData():
    with open('betting_data.pickle', 'rb') as f:
        betting_data = pickle.load(f)
        f.close()
        return betting_data

def waitForMatchEnd(s):
    print("\nWaiting for bet start")
    data = requests.get(urlJSON).json()
    while data['status'] == 'locked':
        data = requests.get(urlJSON).json()
        time.sleep(2)
    time.sleep(3)
    data['time'] = time.time()
    return data

def waitForMatchStart():
    print("\nWaiting for match start")
    data = requests.get(urlJSON).json()
    while data['status'] != 'locked':
        data = requests.get(urlJSON).json()
        time.sleep(2)
    return time.time()

def getBalance(r):
    tree = html.fromstring(r.content)
    return tree.xpath('//span[@class="dollar"]/text()')[0]

def isTourny(data):

    tourny1 = 'bracket!'
    tourny2 = 'after the tournament!'
    if tourny1 in data['remaining']:
        return True
    if tourny2 in data['remaining']:
        return True
    return False

def isExhib(data):
    exhib1 = 'exhibition matches left!'
    exhib2 = 'after the next exhibition match!'
    if exhib1 in data['remaining']:
        return True
    if exhib2 in data['remaining']:
        return True
    return False

def bet(p1,p2):
    p1_games_played = p1.loss + p1.win
    p2_games_played = p2.loss + p2.win
    p1_confidence = 0
    p2_confidence = 0
    d_avg_loss = 100
    d_avg_win = 200
    if p1_games_played > 0 and p2_games_played > 0:
        #1000 confidence if match has occured before.
        if p2 in p1.won and p1 not in p2.won:
            print("p1 -> 1000")
            p1_confidence += 1000
        elif p1 in p2.won and p2 not in p1.won:
            print("p2 -> 1000")
            p2_confidence += 1000
        
        if p1.win != 0 and p1.loss != 0:
            p1_confidence += (p1.avg_loss / p1.avg_win) * 200

        elif p1.win == 0:
            p1_confidence += (p1.avg_loss / d_avg_win) * 200
            
        elif p1.loss == 0:
            p1_confidence += (d_avg_loss / p1.avg_win) * 200

        if p2.win != 0 and p2.loss != 0:
            p2_confidence += (p2.avg_loss / p2.avg_win) * 200
            
        elif p2.win == 0:
            p2_confidence += (p2.avg_loss / d_avg_win) * 200
            
        elif p2.loss == 0:
            p2_confidence += (d_avg_loss / p2.avg_win) * 200

        p1_confidence += (p1.win / p1_games_played) * 500
        p2_confidence += (p2.win / p2_games_played) * 500

    elif p1_games_played > 0 and p2_games_played == 0:

        if p1.win != 0 and p1.loss != 0:
            p1_confidence += (p1.avg_loss / p1.avg_win) * 200

        if p1.win != 0 and p1.loss != 0:
            p1_confidence += (p1.avg_loss / p1.avg_win) * 200

        elif p1.win == 0:
            p1_confidence += (p1.avg_loss / d_avg_win) * 200
            
        elif p1.loss == 0:
            p1_confidence += (d_avg_loss / p1.avg_win) * 200
        p2_confidence = 500
        

    elif p2_games_played > 0 and p1_games_played == 0:
        if p2.win != 0 and p2.loss != 0:
            p2_confidence += (p2.avg_loss / p2.avg_win) * 200

        if p2.win != 0 and p2.loss != 0:
            p2_confidence += (p2.avg_loss / p2.avg_win) * 200
            
        elif p2.win == 0:
            p2_confidence += (p2.avg_loss / d_avg_win) * 200
            
        elif p2.loss == 0:
            p2_confidence += (d_avg_loss / p2.avg_win) * 200
        p1_confidence = 500

    else:
         p1_confidence = 500
         p2_confidence = 500

    print("p1 Confidence: ", p1_confidence)
    print("p2 Confidence: ", p2_confidence)
    
    if p1_confidence >= p2_confidence:
        bet_payload['selectedplayer'] = 'player1'
        bet_payload['wager'] = 1000

    else:
        bet_payload['selectedplayer'] = 'player2'
        bet_payload['wager'] = 1000

with open('leechy.key', 'r') as f:
    data = f.read().split(',')
    login_payload = {data[0]:data[1],data[2]:data[3],data[4]:data[5]}


wins = 0
games = 0

betting_data = openBettingData()

s = requests.session()
results = s.get(urlLOGIN)

#login
results = s.post(urlLOGIN, login_payload, dict(referer = urlLOGIN))



data = waitForMatchEnd(s)
data = requests.get(urlJSON).json()
p1 = data['p1name']
p2 = data['p2name']

if p1 not in betting_data:
    betting_data[p1] = Character()
if p2 not in betting_data:
    betting_data[p2] = Character()

while(True):
    
    data = requests.get(urlJSON).json()
    results = s.get(urlWEB)
    
    p1 = data['p1name']
    p2 = data['p2name']
    
    if p1 not in betting_data:
        betting_data[p1] = Character()
    if p2 not in betting_data:
        betting_data[p2] = Character()

    bet(betting_data[p1], betting_data[p2])

    if isTourny(data):
        bet_payload['wager'] = int(getBalance(results).replace(',',''))
        print("in a tourny")

    if isExhib(data):
        bet_payload['wager'] = 0
        print("Exhib match")

    print(p1,"\n")
    betting_data[p1]._print()
    print(p2,"\n")
    betting_data[p2]._print()
    
    print("\nSent POST: ",bet_payload)
    
    r_bet = s.post(urlBET,bet_payload, headers)
    
    print("POST Response:", r_bet.status_code, r_bet.reason,"\n")

    time_start = waitForMatchStart()
    
    data = waitForMatchEnd(s)

    time_end = data['time']

    results = s.get(urlWEB)

    games += 1
    if data['status'] == '1':   
        betting_data[p1]._won(p2,time_end-time_start)
        betting_data[p2]._lost(p1,time_end-time_start)
        print(p1," won!")
        if bet_payload['selectedplayer'] == 'player1':
            wins += 1
            
               
    if data['status'] == '2':
        betting_data[p2]._won(p1,time_end-time_start)
        betting_data[p1]._lost(p2,time_end-time_start)
        print(p2," won!")
        if bet_payload['selectedplayer'] == 'player2':
            wins += 1

    print("wins:",wins," games:",games)

    print("\n",p1,"\n")
    betting_data[p1]._print()
    print(p2,"\n")
    betting_data[p2]._print()

    
    saveBettingData()
    print("---------------------------------------------------------")