
ELO_DEFAULT = 1000
K = 35

def expectedScore(p1,p2):

    return 1 / (1 + 10**((p2-p1)/400)), 1 / (1 + 10**((p1-p2)/400))

def getNewRating(p1,p2,p1_es,p2_es,win,time):
    #k scalar for p1 
    k1 = 1/(p1/2400)

    #k scalar for p2
    k2 = 1/(p2/2400)

    #k scalar based on time
    k = 150/time * 20

    return (p1 + (k*k1) * (int(win) - p1_es)), (p2 + (k*k2) * (abs(int(win)-1) - p2_es))

def winProbability(p1,p2):
    return 1/(1+10**((p2-p1)/400))