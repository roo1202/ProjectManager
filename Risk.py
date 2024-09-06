# Class representing a Risk in the project

class Risk:
    def __init__(self, impact, events_or_conditions , probability=0.1):
        self.probability = probability
        self.impact = impact
        self.events_or_conditions = events_or_conditions

    def risk_level(self):
        return self.probability * self.impact

    def __str__(self):
        return f"Risk(Probability: {self.probability}, Impact: {self.impact}, Events/Conditions: {self.events_or_conditions})"
    
