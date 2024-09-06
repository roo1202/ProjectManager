import numpy as np
from PMOntologic.Resource import Resource

# Class representing a Task in the project
class Task:
    def __init__(self, id, start, deadline, priority, status, duration, reward, difficulty=0, problems_probability=0.0):
        self.id = id
        self.start = start
        self.deadline = deadline
        self.priority = priority
        self.status = status
        self.resources = [Resource]
        self.dependencies = [Task]
        self.duration = duration
        self.reward = reward
        self.difficulty = difficulty
        self.problems_probability = problems_probability

    def is_overdue(self):
        # Placeholder for actual date comparison logic
        # This method would check if the current date is past the deadline
        return False

    def __repr__(self):
        return f"Task(Name: {self.name})"#, Deadline: {self.deadline}, Priority: {self.priority}, Status: {self.status})"
    
    def tasks_count(self) :
        count = 0
        for sub in self.subTasks:
            count += sub.tasks_count()
        return count + len(self.subTasks)

