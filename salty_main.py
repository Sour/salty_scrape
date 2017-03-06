import lib
from lib.salty_scrape import openSaltySession, waitForMatchEnd, waitForMatchStart, bet, postBet, checkWinner
from lib.salty_file_io import saveBettingData, loadBettingData, loadLoginCredentials


def main(session):  
    betting_data = loadBettingData()

    #main loop
    while(True):
        bet_payload = bet(session, betting_data)
        postBet(session, bet_payload)

        timeStart = waitForMatchStart()
        timeEnd = waitForMatchEnd()

        betting_data = checkWinner(timeStart, timeEnd, betting_data)
        saveBettingData(betting_data)

if __name__ == "__main__":
    waitForMatchEnd()
    session = openSaltySession()
    main(session)