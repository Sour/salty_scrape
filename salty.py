import requests, time, pickle
from lxml import html
from lib.salty_elo import expectedScore, getNewRating, winProbability
from character import Character

urlJSON = "http://www.saltybet.com/state.json"
urlWEB = "http://www.saltybet.com/"
urlLOGIN = 'http://www.saltybet.com/authenticate?signin=1'
urlBET = 'http://www.saltybet.com/ajax_place_bet.php'

login_payload = {}

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

def getJSON():
    try:
        data = requests.get(urlJSON).json()
    except requests.exceptions.RequestException as e:
        print(e);
        data = requests.get(urlJSON).json()
    
    return data

def saveBettingData(betting_data):
    with open('betting_data_v2.pickle','wb') as f:
        pickle.dump(betting_data, f)
        f.close()

def openBettingData():
    with open('betting_data_v2.pickle', 'rb') as f:
        betting_data = pickle.load(f)
        f.close()
        return betting_data

def waitForMatchEnd(s):
    print("\nWaiting for bet start")
    data = getJSON()
    while data['status'] == 'locked':
        data = getJSON()
        time.sleep(2)
    time.sleep(3)
    data['time'] = time.time()
    return data

def waitForMatchStart():
    print("\nWaiting for match start")
    data = getJSON()
    while data['status'] != 'locked':
        data = getJSON()
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

def findCommonMatches(p1, p2,betting_data):
    p1_con = 0
    p2_con = 0

    for char1 in p1.won:
        if char1 in p2.lost:
            p1_con += 1
        for char2 in betting_data[char1].won:
            if char2 in p2.lost:
                p1_con += 1


    for char1 in p2.won:
        if char1 in p1.lost:
            p2_con += 1
        for char2 in betting_data[char1].won:
            if char2 in p1.lost:
                p2_con += 1

    if p1_con > p2_con:
        return 1
    if p2_con > p1_con:
        return -1
    
    return 0

def bet(p1,p2,betting_data):
    
    
    p1_games_played = p1.loss + p1.win
    p2_games_played = p2.loss + p2.win
    p1_confidence = 0
    p2_confidence = 0

    pCommon = findCommonMatches(p1,p2,betting_data)

    if pCommon == 1:
        p1_confidence += 100

    if pCommon == -1:
        p2_confidence += 100

    #1000 confidence if match has occured before.
    if p2 in p1.won and p1 not in p2.won:
        print("p1 -> 1000")
        p1_confidence += 1000

    if p1 in p2.won and p2 not in p1.won:
        print("p2 -> 1000")
        p2_confidence += 1000

    if p1_games_played > 0:
        p1_pct = p1.win / p1_games_played
    else:
        p1_pct = 0.5

    if p2_games_played > 0:
        p2_pct = p2.win / p2_games_played
    else:
        p2_pct = 0.5

    if p1.avg_win != 0:
        p1_a_win = abs( (300 - p1.avg_win) / 300 )
    else:
        p1_a_win = 0.5

    if p2.avg_win != 0:
        p2_a_win = abs( (300 - p2.avg_win) / 300 )
    else:
        p2_a_win = 0.5
        
    if p1.avg_loss != 0:
        p1_a_loss = p1.loss / 300
    else:
        p1_a_loss = 0.5

    if p2.avg_loss != 0:
        p2_a_loss = p2.loss / 300
    else:
        p2_a_loss = 0.5

    p1_confidence += p1_pct * 700
    p1_confidence += p1_a_win * 150
    p1_confidence += p1_a_loss * 150

    p2_confidence += p2_pct * 700
    p2_confidence += p2_a_win * 150
    p2_confidence += p2_a_loss * 150 

    print("p1 Confidence: ", p1_confidence,"p2 Confidence: ", p2_confidence)
    
    if p1_confidence >= p2_confidence:
        bet_payload['selectedplayer'] = 'player1'
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
data = getJSON()
p1 = data['p1name']
p2 = data['p2name']

if p1 not in betting_data:
    betting_data[p1] = Character()
if p2 not in betting_data:
    betting_data[p2] = Character()

while(True):
    
    data = getJSON()
    results = s.get(urlWEB)
    
    p1 = data['p1name']
    p2 = data['p2name']
    
    if p1 not in betting_data:
        betting_data[p1] = Character()
    if p2 not in betting_data:
        betting_data[p2] = Character()

    print(p1)
    betting_data[p1]._print()
    print(p2)
    betting_data[p2]._print()

    p1_es,p2_es = expectedScore(betting_data[p1].elo,betting_data[p2].elo)
    balance = int(getBalance(results).replace(',',''))
    balance = balance / 30
    if betting_data[p1].elo >= betting_data[p2].elo:
        bet_payload['selectedplayer'] = 'player1'
        bet_payload['wager'] = int(balance * winProbability(betting_data[p1].elo,betting_data[p2].elo) - (0.30*balance))
    else:
        bet_payload['selectedplayer'] = 'player2'
        bet_payload['wager'] = int(balance * winProbability(betting_data[p2].elo,betting_data[p1].elo) - (0.30*balance))

    if isTourny(data):
        bet_payload['wager'] = int(getBalance(results).replace(',',''))
        print("in a tourny")

    if isExhib(data):
        bet_payload['wager'] = 0
        print("Exhib match")

    print("\nSent POST: ",bet_payload)
    
    r_bet = s.post(urlBET,bet_payload, headers)
    
    print("POST Response:", r_bet.status_code, r_bet.reason,"\n")

    time_start = waitForMatchStart()
    
    data = waitForMatchEnd(s)

    time_end = data['time']

    results = s.get(urlWEB)

    games += 1

    if data['status'] == '1':   
        betting_data[p1].elo,betting_data[p2].elo = getNewRating(betting_data[p1].elo,betting_data[p2].elo,p1_es,p2_es, 1,time_end-time_start)
        betting_data[p1]._won(p2,time_end-time_start)
        betting_data[p2]._lost(p1,time_end-time_start)
        print(p1,"won!")
        if bet_payload['selectedplayer'] == 'player1':
            wins += 1
            
               
    if data['status'] == '2':
        betting_data[p1].elo,betting_data[p2].elo = getNewRating(betting_data[p1].elo,betting_data[p2].elo,p1_es,p2_es, 0,time_end-time_start)
        betting_data[p2]._won(p1,time_end-time_start)
        betting_data[p1]._lost(p2,time_end-time_start)
        print(p2,"won!")
        if bet_payload['selectedplayer'] == 'player2':
            wins += 1

    print(p1)
    betting_data[p1]._print()
    print(p2)
    betting_data[p2]._print()
    
    print("wins:",wins," games:",games, "PCT: ", wins/games)

    saveBettingData(betting_data)
    print("---------------------------------------------------------")