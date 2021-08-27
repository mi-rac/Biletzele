class Team:
    def __init__(self, color):
        self.color = color
        self.score = 0
        self.turn = 0
        self.players = []


class Game:
    def __init__(self):
        self.all_chosen = 0
        self.num_words = 5
        self.stage = 'lobby'
        self.turn = 0
        self.teams = [Team('red'), Team('blue')]
        self.words = []
        self.guessed = []
        self.turn = 0
        self.players = {}

guest = Game()
guest.players['bula'] = 'red'
guest.players['strula'] = 'blue'
guest.teams[0].players = ['bula']
guest.teams[1].players = ['strula']
guest.words = ['ala', 'bala', 'portocala', 'ai', 'venit', 'si', 'mi', 'sugi', 'banana', 'mea']
