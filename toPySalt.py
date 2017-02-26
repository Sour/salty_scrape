import csv, pickle, time
from character import Character

def saveBettingData(betting_data):
    with open('betting_data_v2.pickle','wb') as f:
        pickle.dump(betting_data, f)
        f.close()

def openBettingData():
    with open('betting_data.pickle', 'rb') as f:
        betting_data = pickle.load(f)
        f.close()
        return betting_data

def expectedScore(p1,p2):
    
    return 1 / (1 + 10**((p2-p1)/400)), 1 / (1 + 10**((p1-p2)/400))

def getNewRating(p1,p2,p1_es,p2_es,win,time):
    #k scalar for p1 
    k1 = 1/(p1/2400)

    #k scalar for p2
    k2 = 1/(p2/2400)

    #k scalar based on time
    if int(time) != 0:
        k = 150/(int(time)+1) * 20
    else:
        k = 20

    return (p1 + (k*k1) * (abs(int(win)-1) - p1_es)), (p2 + (k*k2) * (int(win) - p2_es))

def winProbability(p1,p2):
    return 1/(1+10**((p2-p1)/400))


betting_data = {}
with open('records.csv', newline='') as f:
    r = csv.reader(f,delimiter=',')
    for row in r:
        p1 = row[0]
        p2 = row[1]
        winner = row[2]
        rtime = row[8]

        if p1 not in betting_data:
            betting_data[p1] = Character()
        if p2 not in betting_data:
            betting_data[p2] = Character()
    
        if winner == '0':   
            betting_data[p1]._won(p2,int(rtime))
            betting_data[p2]._lost(p1,int(rtime))
               
        if winner == '1':
            betting_data[p2]._won(p1,int(rtime))
            betting_data[p1]._lost(p2,int(rtime))

        p1_es,p2_es = expectedScore(betting_data[p1].elo,betting_data[p2].elo)
        betting_data[p1].elo,betting_data[p2].elo = getNewRating(betting_data[p1].elo,betting_data[p2].elo,p1_es,p2_es, winner, rtime)
        
    
saveBettingData(betting_data)

print(len(betting_data))