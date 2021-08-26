class Game:
    def __init__(self):
        self.all_chosen = 0
        self.num_words = 5
        self.stage = 'lobby'
        self.turn = 0
        self.teams = [{'points': 0, 'turn':0, 'players':[]}, {'points': 0, 'turn':0, 'players':[]}]
        self.words = []
        self.turn = 0
        self.players = {}
