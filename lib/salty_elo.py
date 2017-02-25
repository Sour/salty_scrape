
ELO_DEFAULT = 1000
K = 35

def expectedScore(p1,p2):

    return 1 / (1 + 10**((p2-p1)/400)), 1 / (1 + 10**((p1-p2)/400))

def getNewRating(p1,p2,p1_es,p2_es,win,time):
    
    k = 150/time * 25
    print("k:",k)
    return (p1 + K * (int(win) - p1_es)), (p2 + K * (abs(int(win)-1) - p2_es))

def winProbability(p1,p2):
    return 1/(1+10**((p2-p1)/400))