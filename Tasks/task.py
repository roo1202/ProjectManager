import numpy as np
from PMOntologic.Resource import Resource
from typing import List

# Class representing a Task in the project
class Task:
    def __init__(self, id, priority, duration, reward, start=0, deadline=1000000, difficulty=0, problems_probability=0.0):
        self.id = id
        self.start = start
        self.deadline = deadline
        self.priority = priority
        self.status = 0
        self.resources: List[Resource] = []
        self.dependencies:List[Task] = []
        self.duration = duration
        self.reward = reward
        self.difficulty = difficulty
        self.problems_probability = problems_probability

    def is_overdue(self):
        # Placeholder for actual date comparison logic
        # This method would check if the current date is past the deadline
        return False

    def __repr__(self):
        return f"Task(Name: {self.id} Status: {self.status} Duration: {self.duration}"
    
    def __eq__(self, other):
        if isinstance(other, Task):
            return (self.id == other.id)
        return False

    def __hash__(self):
        return hash((self.id))