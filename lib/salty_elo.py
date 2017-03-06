
ELO_DEFAULT = 1000
K = 35

def expectedScore(player1, player2):
    p1ExpectedScore = 1 / (1 + 10 ** ((player2 - player1) / 400))
    p2ExpectedScore = 1 / (1 + 10 ** ((player1 - player2) / 400))

    return p1ExpectedScore

def getNewRating(player1, p1ExpectedScore, win, time):  
    player1K = 1 / (p1 / 2400)
    k = (150 / time) * 20

    newPlayer1Elo = (player1 + (k*player1K) * (int(win) - p1ExpectedScore))

    return newPlayer1Elo

def winProbability(player1, player2):   
    return (1 / (1 + 10 ** ((player2 - player1) / 400)))