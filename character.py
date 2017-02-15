

class Character():
    def __init__(self):
        self.win = 0
        self.loss = 0
        self.won = []
        self.lost = []
        self.avg_win = 0
        self.avg_loss = 0

    def _lost(self, character, time):
        self.loss += 1
        self.lost.append(character)
        if self.win != 0:
            self.avg_loss = (((self.loss - 1) * self.avg_loss) + time) / self.loss
        else:
            self.avg_loss = time
        
    def _won(self, character, time):
        self.win += 1
        self.won.append(character)
        if self.win != 0:
            self.avg_win = (((self.win - 1) * self.avg_win) + time) / self.win
        else:
            self.avg_win = time

    def print(self):
        print("wins:",self.win)
        print("losses:",self.loss)
        print("beat:",self.won)
        print("lost:",self.lost)
        print("avg win time:",self.avg_win)
        print("avg loss time:",self.avg_loss)
        print("\n")

    
    
    
