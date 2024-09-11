
import random
from PMOntologic.Risk import Risk
from Simulation.PMAgent import PMAgent
# Class representing an Opportunity in the project
class Opportunity(Risk):
    def __init__(self, probability=0.1, impact=[], events_or_conditions=[], benefits=[]):
        super(self, probability, impact, events_or_conditions).__init__
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
        return PM.beliefs['resources']['budget'] > PM.project.resources['budget'] * 0.8 and time > 0.25 * PM.beliefs['project_average_time']

    # Evento: Cumplimiento temprano de tareas
    def early_completion(self, PM: PMAgent, time: int) -> bool:
        completed_tasks = sum(status == 1 for status in PM.beliefs['tasks'].values())
        return completed_tasks >= len(PM.beliefs['tasks']) * 0.75 and time < PM.beliefs['project_average_time'] * 0.75

    # Evento: Alto nivel de cooperación
    def high_cooperation(self, PM: PMAgent) -> bool:
        cooperative_workers = sum(1 for _, (state, _) in PM.beliefs['workers'].items() if state == 1)
        return cooperative_workers > len(PM.beliefs['workers']) * 0.5

    # Evento: Cumplimiento de hitos importantes
    def milestone_completion(self, PM: PMAgent) -> bool:
        return PM.beliefs['milestones']['milestones'][1] < PM.milestones_count and random.random() < 0.8  # Alta probabilidad si se supera un hito

    # Evento: Gestión eficiente del riesgo
    def risk_management_success(self, PM: PMAgent, time: int) -> bool:
        return len(PM.beliefs['problems']) < len(PM.beliefs['tasks']) * 0.1 and time < PM.beliefs['project_average_time'] * 0.75

    # Evento: Oportunidad de innovación
    def innovation_opportunity(self, PM: PMAgent, time: int) -> bool:
        return random.random() < 0.2 and PM.beliefs['team'] > 70 and time < PM.beliefs['project_average_time'] * 0.5


def singleton(cls):
    instances = {}

    def get_instance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return get_instance

########################## Clases de Oportunidades ############################

# Oportunidad: Alta Productividad
@singleton
class HighProductivityOpportunity(Opportunity):
    def __init__(self):
        probability = 0.2
        impact = ['time', 'rewards']
        events_or_conditions = [self.high_productivity]
        benefits = ['budget', 'time']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Alta Motivación del Equipo
@singleton
class HighMotivationOpportunity(Opportunity):
    def __init__(self):
        probability = 0.3
        impact = ['boost morale', 'increase cooperation']
        events_or_conditions = [self.high_motivation]
        benefits = ['Higher worker efficiency', 'Faster task completion']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Optimización de Recursos
@singleton
class OptimizedResourcesOpportunity(Opportunity):
    def __init__(self):
        probability = 0.25
        impact = ['lower resource usage', 'reduced costs']
        events_or_conditions = [self.optimized_resources]
        benefits = ['Extra budget for future phases', 'Improved project ROI']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Reducción de Costos
@singleton
class CostSavingOpportunity(Opportunity):
    def __init__(self):
        probability = 0.15
        impact = ['budget savings', 'increased project margin']
        events_or_conditions = [self.cost_saving]
        benefits = ['Reallocation of saved budget', 'Opportunity for additional investments']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Cumplimiento Temprano de Tareas
@singleton
class EarlyCompletionOpportunity(Opportunity):
    def __init__(self):
        probability = 0.3
        impact = ['time savings', 'better client satisfaction']
        events_or_conditions = [self.early_completion]
        benefits = ['Opportunity for early project delivery', 'Potential bonuses for early completion']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Alta Cooperación del Equipo
@singleton
class HighCooperationOpportunity(Opportunity):
    def __init__(self):
        probability = 0.2
        impact = ['teamwork enhancement', 'faster problem-solving']
        events_or_conditions = [self.high_cooperation]
        benefits = ['Improved task efficiency', 'Better use of shared resources']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Cumplimiento de Hitos
@singleton
class MilestoneCompletionOpportunity(Opportunity):
    def __init__(self):
        probability = 0.4
        impact = ['project visibility', 'increased stakeholder confidence']
        events_or_conditions = [self.milestone_completion]
        benefits = ['Increased project funding', 'Positive publicity']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Gestión Eficiente del Riesgo
@singleton
class RiskManagementSuccessOpportunity(Opportunity):
    def __init__(self):
        probability = 0.25
        impact = ['lower risk exposure', 'higher team confidence']
        events_or_conditions = [self.risk_management_success]
        benefits = ['Improved project stability', 'Increased risk tolerance for innovation']
        super().__init__(probability, impact, events_or_conditions, benefits)

# Oportunidad: Innovación
@singleton
class InnovationOpportunity(Opportunity):
    def __init__(self):
        probability = 0.2
        impact = ['potential for new solutions', 'increased competitiveness']
        events_or_conditions = [self.innovation_opportunity]
        benefits = ['New technology implementation', 'Enhanced project deliverables']
        super().__init__(probability, impact, events_or_conditions, benefits)
