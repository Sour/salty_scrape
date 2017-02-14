

class Character():
    def __init__(self):
        self.win = 0
        self.loss = 0
        self.won = []
        self.lost = []
        self.avg_win = 0
        self.avg_loss = 0

    def lost(self, character, time):
        self.loss += 1
        self.lost.append(character)
        self.avg_loss = (self.avg_loss + time) / 2

        
    def won(self, character, time):
        self.win += 1
        self.won.append(character)
        self.avg_win = (self.avg_loss + time) / 2

    

    
