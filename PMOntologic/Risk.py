# Class representing a Risk in the project

import random
from Simulation.PMAgent import PMAgent


class Risk:
    def __init__(self, impact, events_or_conditions , probability=0.1):
        self.probability = probability
        self.impact = impact
        self.events_or_conditions = events_or_conditions

    def risk_level(self):
        return self.probability * self.impact

    def __str__(self):
        return f"Risk(Probability: {self.probability}, Impact: {self.impact}, Events/Conditions: {self.events_or_conditions})"
    
    ###################### Eventos negativos #####################

    # Evento: Retraso en la ejecución
    def execution_delay(self, PM: PMAgent, time: int) -> bool:
        completed_tasks = sum(status == 1 for status in PM.beliefs['tasks'].values())
        total_tasks = len(PM.beliefs['tasks'])
        return completed_tasks < total_tasks / 2 and time > 0.75 * PM.beliefs['project_average_time']

    # Evento: Gasto acelerado
    def accelerated_spending(self, PM: PMAgent, time: int) -> bool:
        return (PM.beliefs['resources']['budget'] < PM.project.resources['budget'].total / 2 and 
                time < 0.5 * PM.beliefs['project_average_time'])

    # Evento: Incremento en el costo
    def cost_increase(self, PM: PMAgent, time: int) -> bool:
        return time > 0.5 * PM.beliefs['project_average_time'] and random.random() < 0.3

    # Evento: Dependencias no cumplidas
    def unfulfilled_dependences(self, PM: PMAgent , time : int) -> bool:
        for task in PM.project.tasks.values():
            if task.status == 0:  # Si la tarea no ha comenzado
                for dependency in task.dependencies:
                    if PM.beliefs['tasks'][dependency.id] == -1:  # Si alguna dependencia fallo
                        return True
        return False

    # Evento: Falta de personal
    def lack_of_staff(self, PM: PMAgent, time : int) -> bool:
        required_workers = len(PM.project.tasks)
        actual_workers = len(PM.beliefs['workers'])
        return actual_workers < required_workers * 0.1  # Si hay menos trabajadores que el 10% de las tareas

    # Evento: Baja productividad
    def low_productivity(self, PM: PMAgent, time: int) -> bool:
        incomplete_tasks_reward = sum(task.reward for task in PM.project.tasks.values() if task.status == 0)
        return incomplete_tasks_reward < PM.beliefs['max_reward'] * 0.25 and time > PM.beliefs['project_average_time'] * 0.5

    # Evento: Baja experiencia del equipo
    def low_experience(self, PM: PMAgent, time: int) -> bool:
        return len(PM.beliefs['problems']) > len(PM.beliefs['tasks']) / max(len(PM.beliefs['workers']), 1)

    # Evento: Baja motivación
    def low_motivation(self, PM: PMAgent, time: int) -> bool:
        return PM.beliefs['team'] < PM.min_motivation_team

    # Evento: Baja prioridad
    def low_priority(self, PM: PMAgent, time: int) -> bool:
        total_priority = sum(task.priority for task in PM.project.tasks.values())
        completed_priority = sum(task.priority for task in PM.project.tasks.values() if task.status == 1)
        return completed_priority < total_priority * 0.3 and time > PM.beliefs['project_average_time'] * 0.5

######################## Clases de riesgos #########################

# Riesgo : Retraso de Ejecucion
class ExecutionDelayRisk(Risk):
    def __init__(self):
        probability = 0.3  # 30% de probabilidad de que ocurra
        impact = ['time', 'budget']
        events_or_conditions = [self.execution_delay]
        super().__init__(impact, events_or_conditions, probability)

# Riesgo : Gasto Acelerado
class AcceleratedSpendingRisk(Risk):
    def __init__(self):
        probability = 0.2  # 20% de probabilidad
        impact = ['budget']
        events_or_conditions = [self.accelerated_spending]
        super().__init__(impact, events_or_conditions, probability)
        
# Riesgo : Incremento en el Costo
class CostIncreaseRisk(Risk):
    def __init__(self):
        probability = 0.3  # 30% de probabilidad
        impact = ['budget']
        events_or_conditions = [self.cost_increase]
        super().__init__(impact, events_or_conditions, probability)

# Riesgo : Dependencias No Cumplidas
class UnfulfilledDependencesRisk(Risk):
    def __init__(self):
        probability = 0.25  # 25% de probabilidad
        impact = ['number_of_tasks', 'Workstations']
        events_or_conditions = [self.unfulfilled_dependences]
        super().__init__(impact, events_or_conditions, probability)

# Riesgo : Falta de Personal
class LackOfStaffRisk(Risk):
    def __init__(self):
        probability = 0.4  # 40% de probabilidad
        impact = ['time', 'reward']
        events_or_conditions = [self.lack_of_staff]
        super().__init__(impact, events_or_conditions, probability)

# Riesgo : Baja Productividad
class LowProductivityRisk(Risk):
    def __init__(self):
        probability = 0.35  # 35% de probabilidad
        impact = ['number_of_tasks', 'reward']
        events_or_conditions = [self.low_productivity]
        super().__init__(impact, events_or_conditions, probability)

# Riesgo : Baja Motivación
class LowMotivationRisk(Risk):
    def __init__(self):
        probability = 0.25  # 25% de probabilidad
        impact = ['number_of_tasks', 'Network']
        events_or_conditions = [self.low_motivation]
        super().__init__(impact, events_or_conditions, probability)

# Riesgo : Baja Prioridad
class LowPriorityRisk(Risk):
    def __init__(self):
        probability = 0.3  # 30% de probabilidad
        impact = ['Developers', 'Testers']
        events_or_conditions = [self.low_priority]
        super().__init__(impact, events_or_conditions, probability)
