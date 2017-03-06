import requests
import time

from lxml import html
from lib.salty_elo import winProbability
from lib.salty_file_io import loadLoginCredentials
from character import Character

urlJSON = "http://www.saltybet.com/state.json"
urlWEB = "http://www.saltybet.com/"
urlLOGIN = 'http://www.saltybet.com/authenticate?signin=1'
urlBET = 'http://www.saltybet.com/ajax_place_bet.php'

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
    except:
        print("emptyJSON retry")
        data = requests.get(urlJSON).json()
    
    return data

def getSiteHTML(session):
    return session.get(urlWEB)

def getBalance(session):
    results = getSiteHTML(session)
    tree = html.fromstring(results.content)
    balance = tree.xpath('//span[@class="dollar"]/text()')[0]
    balance = int(balance.replace(',', ''))
    return balance

def getBetTotals():
    data = getJSON()
    p1_total = data['p1total']
    p2_total = data['p2total']

    return p1_total, p2_total

def getMatchType():
    data = getJSON()
    tourny1 = 'bracket!'
    tourny2 = 'after the tournament!'
    exhib1 = 'exhibition matches left!'
    exhib2 = 'after the next exhibition match!'

    if tourny1 in data['remaining']:
        return 'tournament'
    if tourny2 in data['remaining']:
        return 'tournament'
    if exhib1 in data['remaining']:
        return 'exhibition'
    if exhib2 in data['remaining']:
        return 'exhibition'

    return 'matchmaking'

def openSaltySession():
    session = requests.session()
    results = session.get(urlLOGIN)
    login_payload = loadLoginCredentials()
    #POST login payload
    results = session.post(urlLOGIN, login_payload, dict(referer = urlLOGIN))

    return session

def waitForMatchEnd():
    print("\nWaiting for bet start")
    data = getJSON()
    while data['status'] == 'locked':
        data = getJSON()
        time.sleep(2)
    time.sleep(3)
    return time.time()

def waitForMatchStart():
    print("\nWaiting for match start")
    data = getJSON()
    while data['status'] != 'locked':
        data = getJSON()
        time.sleep(2)
    return time.time()

def bet(session, betting_data):
    data = getJSON()

    player1 = data['p1name']
    player2 = data['p2name']

    balance = getBalance(session)
    #40th of total balance will be later modified by win%
    bet_amount = balance / 50

    #add players to db if they do not exist yet
    if player1 not in betting_data:
        betting_data[player1] = Character()
    if player2 not in betting_data:
        betting_data[player2] = Character()

    player1Elo = betting_data[player1].elo
    player2Elo = betting_data[player2].elo

    print("bet:", bet_amount, "elo",player1Elo,player2Elo)

    if player1Elo >= player2Elo:
        bet_payload['selectedplayer'] = 'player1'
        bet_amount = int((bet_amount * winProbability(player1Elo, player2Elo)) - (0.30 * bet_amount))
       
        if (player1Elo == 0) or (player2Elo == 0):
            bet_amount = (bet_amount * 0.5) - (0.30 * bet_amount)

        bet_payload['wager'] = bet_amount
    else:
        bet_payload['selectedplayer'] = 'player2'
        bet_amount = int((bet_amount * winProbability(player2Elo, player1Elo)) - (0.30 * bet_amount))
        
        if (player1Elo == 0) or (player2Elo == 0):
            bet_amount = (bet_amount * 0.5) - (0.30 * bet_amount)
    
        bet_payload['wager'] = bet_amount

    matchType = getMatchType()
    #all in bets in tournaments and small bets on exhibition matches | temp?
    if matchType == 'tournament':
        bet_payload['wager'] = balance
    if matchType == 'exhibition':
        bet_payload['wager'] = 1000

    return bet_payload

def checkWinner(timeStart, timeEnd, betting_data):
    data = getJSON()
    player1 = data['p1name']
    player2 = data['p2name']

    if data['status'] == '1':   
        betting_data[player1]._won(player2, timeEnd - timeStart)
        betting_data[player2]._lost(player1, timeEnd - timeStart)
            
    if data['status'] == '2':
        betting_data[player2]._won(player1, timeEnd - timeStart)
        betting_data[player1]._lost(player2, timeEnd - timeStart)
    
    return betting_data

def postBet(session, bet_payload):
    print("POST:", bet_payload)
    postReturn = session.post(urlBET, bet_payload, headers)
    print("POST Response:", postReturn.status_code, postReturn.reason)
