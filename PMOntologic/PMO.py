
from Tasks.task import Task
from PMOntologic.Resource import Resource

# Class representing a Project
class Project:
    def __init__(self, objective, tasks, resources):
        self.objective = objective
        self.progress = 0
        self.tasks = {task.id : task for task in tasks} #{task_id : Task}
        self.risks = []
        self.opportunities = [] 
        self.resources = {resource.id : resource for resource in resources} # {resource_id : Resource}

    def add_task(self, task):
        self.tasks.append(task)
    
    def add_risk(self, risk):
        self.risks.append(risk)
    
    def add_resource(self, resource):
        self.resources.append(resource)

    def __str__(self):
        return f"Project(Objective: {self.objective})"

# Class representing a Role in the project
class Role:
    def __init__(self, group_or_individual, role_type):
        self.group_or_individual = group_or_individual
        self.role_type = role_type

    def __str__(self):
        return f"Role(Type: {self.role_type}, Group/Individual: {self.group_or_individual})"

# Class representing a Milestone in the project
class Milestone:
    def __init__(self, phase_completed):
        self.phase_completed = phase_completed

    def __str__(self):
        return f"Milestone(Phase Completed: {self.phase_completed})"


# Class representing a Constraint in the project
class Constraint:
    def __init__(self, limitation):
        self.limitation = limitation

    def __str__(self):
        return f"Constraint(Limitation: {self.limitation})"
