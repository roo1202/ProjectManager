
from PMOntologic.Risk import Risk
# Class representing an Opportunity in the project
class Opportunity(Risk):
    def __init__(self, probability=0.1, impact=[], events_or_conditions=[], benefits=[]):
        super(self, probability, impact, events_or_conditions).__init__
        self.benefits = benefits
