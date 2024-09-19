
class Agent():
    pass

class Rule():
    def __init__(self, id, weight, description=''):
        self.id = id
        self.weight = weight
        self.description = description

    def evaluate(self, agent: Agent):
        pass
    