import csv, pickle
from character import Character

def openBettingData():
    with open('betting_data.pickle', 'rb') as f:
        return pickle.load(f)

def saveBettingData():
    with open('betting_data_bak.pickle','wb') as f:
        pickle.dump(betting_data, f)



betting_data = openBettingData()
with open('records.csv', newline='') as f:
    r = csv.reader(f,delimiter=',')
    for row in r:
        p1 = row[0]
        p2 = row[1]
        winner = row[2]
        time = row[8]

        if p1 not in betting_data:
            betting_data[p1] = Character()
        if p2 not in betting_data:
            betting_data[p2] = Character()
    
        if winner == '0':   
            betting_data[p1]._won(p2,int(time))
            betting_data[p2]._lost(p1,int(time))
               
        if winner == '1':
            betting_data[p2]._won(p1,int(time))
            betting_data[p1]._lost(p2,int(time))


saveBettingData()
