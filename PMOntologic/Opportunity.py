
import random
from PMOntologic.Risk import Risk
from Simulation.PMAgent import PMAgent
# Class representing an Opportunity in the project
class Opportunity(Risk):
    def __init__(self, probability=0.1, impact=[], events_or_conditions=[], benefits=[]):
        super().__init__(impact, events_or_conditions, probability)
        self.benefits = benefits


    ######################### Eventos positivos ############################

    # Evento: Alta productividad
    def high_productivity(self, PM: PMAgent, time: int) -> bool:
        completed_tasks_reward = sum(task.reward for task in PM.project.tasks.values() if task.status == 1)
        return completed_tasks_reward >= PM.beliefs['max_reward'] * 0.75 and time < PM.beliefs['project_average_time'] * 0.75

    # Evento: Equipo altamente motivado
    def high_motivation(self, PM: PMAgent, time: int) -> bool:
        return PM.beliefs['team'] > 80 and time < PM.beliefs['project_average_time'] * 0.75

    # Evento: Optimización de recursos
    def optimized_resources(self, PM: PMAgent, time: int) -> bool:
        total_resources = sum(PM.beliefs['resources'].values())
        required_resources = sum(resource.total for resource in PM.project.resources.values())
        return total_resources >= required_resources * 0.8 and time < PM.beliefs['project_average_time'] * 0.5

    # Evento: Reducción de costos
    def cost_saving(self, PM: PMAgent, time: int) -> bool:
        return PM.beliefs['resources']['budget'] > PM.project.resources['budget'].total * 0.8 and time > 0.25 * PM.beliefs['project_average_time']

    # Evento: Cumplimiento temprano de tareas
    def early_completion(self, PM: PMAgent, time: int) -> bool:
        completed_tasks = sum(status == 1 for status in PM.beliefs['tasks'].values())
        return completed_tasks >= len(PM.beliefs['tasks']) * 0.75 and time < PM.beliefs['project_average_time'] * 0.75

    # Evento: Alto nivel de cooperación
    def high_cooperation(self, PM: PMAgent, time: int) -> bool:
        cooperative_workers = sum(1 for _, (state, _) in PM.beliefs['workers'].items() if state == 1)
        return cooperative_workers > len(PM.beliefs['workers']) * 0.5

    # Evento: Cumplimiento de hitos importantes
    def milestone_completion(self, PM: PMAgent, time: int) -> bool:
        return PM.beliefs['milestones']['milestones'][0][1] < PM.milestones_count and random.random() < 0.8  # Alta probabilidad si se supera un hito

    # Evento: Gestión eficiente del riesgo
    def risk_management_success(self, PM: PMAgent, time: int) -> bool:
        return len(PM.beliefs['problems']) < len(PM.beliefs['tasks']) * 0.1 and time < PM.beliefs['project_average_time'] * 0.75

    # Evento: Oportunidad de innovación
    def innovation_opportunity(self, PM: PMAgent, time: int) -> bool:
        return random.random() < 0.2 and PM.beliefs['team'] > 70 and time < PM.beliefs['project_average_time'] * 0.5



########################## Clases de Oportunidades ############################

# Oportunidad: Alta Productividad
class HighProductivityOpportunity(Opportunity):
    def __init__(self):
        probability = 0.2
        impact = ['time', 'rewards']
        events_or_conditions = [self.high_productivity]
        benefits = ['budget', 'time']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Alta Motivación del Equipo
class HighMotivationOpportunity(Opportunity):
    def __init__(self):
        probability = 0.3
        impact = ['Resource1', 'Resource2']
        events_or_conditions = [self.high_motivation]
        benefits = ['Resource3', 'Resource1']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Optimización de Recursos
class OptimizedResourcesOpportunity(Opportunity):
    def __init__(self):
        probability = 0.25
        impact = ['Resource5', 'Resource6']
        events_or_conditions = [self.optimized_resources]
        benefits = ['Resource9', 'Resource1']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Reducción de Costos
class CostSavingOpportunity(Opportunity):
    def __init__(self):
        probability = 0.15
        impact = ['Resource2', 'Resource4']
        events_or_conditions = [self.cost_saving]
        benefits = ['Resource6', 'Resource8']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Cumplimiento Temprano de Tareas
class EarlyCompletionOpportunity(Opportunity):
    def __init__(self):
        probability = 0.3
        impact = ['Resource1', 'Resource3']
        events_or_conditions = [self.early_completion]
        benefits = ['Resource1', 'Resource8']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Alta Cooperación del Equipo
class HighCooperationOpportunity(Opportunity):
    def __init__(self):
        probability = 0.2
        impact = ['Resource7', 'Resource5']
        events_or_conditions = [self.high_cooperation]
        benefits = ['Resource7', 'Resource3']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Cumplimiento de Hitos
class MilestoneCompletionOpportunity(Opportunity):
    def __init__(self):
        probability = 0.4
        impact = ['Resource8', 'Resource2']
        events_or_conditions = [self.milestone_completion]
        benefits = ['Resource1', 'Resource3']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Gestión Eficiente del Riesgo
class RiskManagementSuccessOpportunity(Opportunity):
    def __init__(self):
        probability = 0.25
        impact = ['Resource3', 'Resource4']
        events_or_conditions = [self.risk_management_success]
        benefits = ['Resource2', 'Resource6']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Innovación
class InnovationOpportunity(Opportunity):
    def __init__(self):
        probability = 0.2
        impact = ['Resource2', 'Resource7']
        events_or_conditions = [self.innovation_opportunity]
        benefits = ['Resource1', 'Resource2']
        super().__init__(probability, impact, events_or_conditions, benefits)
