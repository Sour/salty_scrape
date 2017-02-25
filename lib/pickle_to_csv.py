import csv, pickle
from character import Character


def openBettingData():
    with open('betting_data.pickle', 'rb') as f:
        betting_data = pickle.load(f)
        f.close()
        return betting_data


data = openBettingData()

with open('training_data.csv','w') as f:
    writer = csv.writer(f,delimiter=',')
    for char in data:
        writer.writerow([data[char].win, data[char].loss, data[char].avg_win, data[char].avg_loss]);