import pickle
from character import Character
def saveBettingData(betting_data):
    with open('betting_data_v2.pickle','wb') as file:
        pickle.dump(betting_data, file)
        file.close()

def loadBettingData():
    with open('betting_data_v2.pickle', 'rb') as file:
        betting_data = pickle.load(file)
        file.close()
        return betting_data

def loadLoginCredentials():
    with open('leechy.key', 'r') as file:
        data = file.read().split(',')
        login_payload = {data[0]:data[1],data[2]:data[3],data[4]:data[5]}
        file.close()

    return login_payload