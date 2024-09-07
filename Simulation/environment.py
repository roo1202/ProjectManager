
class Environment():
    '''
    Clase abstracta para modelar los Medio Ambientes.
    Un medio ambiente necesita una funcion de transformacion (`transform`) del Medio, y 
    las funciones perceptuales (`see`) segun los tipos de agentes que pueden convivir en el
    '''

    def __init__(self) -> None:
        self._see_functions = {}

    def see(self, agent):
        '''
        Evaluacion de la funcion perceptual para un agente especifico. Dado el agente (`agent`),
        y el tipo de agente (`type(agent)`), genera el conjunto de percepciones que
        ese agente capta, segun la funcion perceptual de su tipo.

        `agent`: Instancia del agente

        `return`: Conjunto de percepciones captadas
        '''
        f = self._see_functions[type(agent)]
        return f(agent)

    def get_see_function(self, type_agent):
        '''
        Funcion perceptual para un agente especifico dado el tipo del agente (`type_agent`)

        `type_agent`: Tipo de agente

        `return`: Funcion perceptual
        '''
        return self._see_functions[type_agent]

    def transform(self, actions):
        '''
        Funcion de transformacion del Medio, que dado un conjunto de acciones, 
        cambia el estado del sistema
        '''
        raise NotImplementedError()

    def next_step(self):
        '''
        Ejecuta un paso de la simulacion dentro del Medio
        '''
        raise NotImplementedError()

    def outputs(self):
        '''
        Devuelve las observaciones realizadas hasta el momento de las variables observables.
        '''
        raise NotImplementedError()


import random
from typing import List
from PMOntologic.Opportunity import Opportunity
from PMOntologic.Risk import Risk
from Simulation.WorkerAgent import WorkerAgent, WorkerPerception, WorkerAction
from Simulation.PMAgent import PMAgent, PMAction, PMperception
from PMOntologic.PMO import Project


class Work_Center(Environment): 
    """
    Clase para modelar el medio donde se desarrollaran nuestros agentes trabajadores y el Project Manager
    """
    def __init__(self, workers, PM , risks, opportunities):
        self.__see_functions = {
            WorkerAgent : self.worker_see_function,
            PMAgent : self.pm_see_function
        }
        self.project_manager : PMAgent = PM  
        self.pm_action = PMAction()                                           # Accion devuelta por el PM para ejecutar
        self.workers : List[WorkerAgent] = workers                            # Lista de agentes trabajadores
        self.workers_actions : List[(WorkerAgent,WorkerAction)] = []          # Acciones devueltas por los trabajadores 
        self.cooperations = []                                                # ((trabajador1, trabajador2), tarea) que deben cooperar en una tarea
        self.time = 0                                                         # Tiempo actual de la simulacion
        self.resources = {}                                                   # Recursos actuales
        self.resources_priority = []                                          # Recursos que son prioridad a optimizar
        self.project = Project()                                              # Projecto a desarrollar por los agentes
        self.asking_report = { agente.id : False for agente in self.workers}
        self.reports = []                                                     # [(worker_id, task_id, progress)]
        self.problems = []                                                    # Ids de las tareas que presentaron problemas
        self.solved_problems = []                                             # [worker_id] trabajadores que resolvieron un problema durante la ultima jornada
        self.risks = risks
        self.opportunities = opportunities
        self.manager_available = True
        self.priority = None
        
    def get_team_motivation(self):
        return sum(worker.motivation for worker in self.workers) // len(self.workers)
        
        
    def next_step(self):
        self.time += 10    
         
        P = self.see(self.project_manager)
        action = self.project_manager.act(P)
        pm_action = action

        self.reports = []
        self.solved_problems = []

        workers_actions = []
        for worker in self.workers:  
            P = self.see(worker)
            action = worker.act(P)
            workers_actions.append((worker, action))

        self.transform(workers_actions=workers_actions, pm_action=pm_action)
        self.workers_actions = workers_actions
        self.pm_action = pm_action


    def transform(self, workers_actions : List[(WorkerAgent,WorkerAction)], pm_action : PMAction):
        # Modificamos el medio segun las acciones que hizo el Project Manager

        # Asignamos las tareas a los trabajadores
        for agent,task_id in pm_action.assignments:
            task = self.project.tasks[task_id]
            for worker in self.workers:
                if worker.id == agent :
                    worker.task_queue.append(task)

        # Marcamos los agentes que deben reportar progreso
        for agent in pm_action.ask_reports:
            self.asking_report[agent] = True

        # Reasignamos las tareas reportadas con problemas              revisar reasignacion, pq no la puse en asignaciones y ya?
        for agent,task_id in pm_action.reassign:
            task = self.project.tasks[task_id]
            for worker in self.workers:
                if worker.id == agent :
                    worker.task_queue.append(task)

        # Activamos o no la disponibilidad del PM
        if pm_action.work_on != None :
            self.manager_available = False
            self.project.tasks[pm_action.work_on].difficulty -= 1
        else :
            self.manager_available = True

        # Actualizamos la lista de los agentes que deben cooperar
        self.cooperations.extend(cooperation for cooperation in pm_action.cooperations)

        # Motivamos a los agentes
        if len(pm_action.motivate) > 0 :
            for agent in self.workers :
                if agent.id in pm_action.motivate :
                    agent.motivation += 10

        # Actualizamos la prioridad
        if pm_action.priority != None :
            self.priority = pm_action.priority

        # Actualizamos los recursos a optimizar
        self.resources_priority = pm_action.optimize

        # Actualizamos si se tomo alguna oportunidad, y jugamos con la probabilidad de exito
        if pm_action.take_chance != None :
            if random.random() < pm_action.take_chance.probability :
                for benefit in pm_action.take_chance.benefits :
                    self.resources[benefit] += 10
            else :
                for impact in pm_action.take_chance.impact :
                    self.resources[impact] -= 10


        # Modificamos el medio segun las acciones que hicieron los trabajadores

        # Revisamos la disposicion de cooperar de los agentes, y dividimos la tarea
        for agents, task_id in self.cooperations :
            flag1 = False
            flag2 = False
            for agent, action in self.workers_actions:
                if agents[0] == agent.id and action.cooperate :
                    flag1 = True
                if agents[1] == agent.id and action.cooperate :
                    flag2 = True
            if flag1 and flag2:
                task = self.project.tasks[task_id] 
                task.difficulty = task.difficulty // 2
                task.reward = task.reward // 2
                task.duration = task.duration // 2
                for resource in task.resources:
                    resource.total = resource.total // 2
                for worker in self.workers:
                    if worker.id == agents[0] or worker.id == agents[1]:
                        worker.task_queue.append(task)
            else :
                self.problems.append(task_id)
        
        for agent,action in workers_actions :
            # Si el agente va a reportar progreso
            if action.report_progress :
                self.reports.append((agent.id, agent.current_task.id, agent.beliefs['task_progress']))
                # Si termino la tarea, disminuimos los recursos actuales
                if agent.current_task.duration <= agent.beliefs['task_progress']:
                    for resource in agent.current_task.resources :
                        self.resources[resource.id] -= resource.total

            # Si el agente esta escalando un problema
            if action.escalate_problem :
                self.problems.append(agent.current_task.id)

            # Si el agente reporta un problema que ya solucionó
            if action.report_problem :
                self.solved_problems.append(agent.id)     

            # Si el agente descansa se le sube la energia 
            if action.rest :
                agent.current_enegry += 10       
            


    def worker_see_function(self, agent : WorkerAgent) -> WorkerPerception:
        coworkers = {}
        cooperation_needed = False
        # Comprobamos si se necesita la cooperacion del agente
        for workers, _ in self.cooperations:
            if workers[0] == agent.id : 
                cooperation_needed = True
                coworkers[workers[1]] = 0
            if workers[1] == agent.id :
                cooperation_needed = True
                coworkers[workers[0]] = 0
        
        for worker, action in self.workers_actions:
            if worker.id == agent.id :
                # Si el agente como ultima accion estaba trabajando entonces habra un progreso
                if action.work and action.new_state == 1:
                    task_progress = 10
                else :
                    task_progress = 0
                # Revisamos que el agente tenga tareas disponibles
                if len(agent.task_queue) > 0 :
                    task_available = True
                else :
                    task_available = False
                # Si el agente esta trabajando tiene posibilidad de encontrarse un problema
                problem_detected = False
                problem_severity = 0
                if agent.current_task != None and random.random() < agent.current_task.problems_probability:
                    problem_detected = True
                    problem_severity = agent.current_task.difficulty      
                # Revisamos disponibilidad del PM
                manager_available = self.manager_available
                # Revisamos si el PM requiere de reporte 
                if self.asking_report[agent.id] :
                    progress_report = True
                else: 
                    progress_report = False
                # Actualizamos la motivacion del equipo
                team_motivation = self.get_team_motivation()

        return WorkerPerception(task_available=task_available, task_progress=task_progress, cooperation_needed=cooperation_needed, problem_detected=problem_detected, problem_severity=problem_severity,manager_available=manager_available, coworkers=coworkers, progress_report=progress_report, team_motivation=team_motivation, resource_priority=self.resources_priority, priority=self.priority)
                
            

    def pm_see_function(self, agent : PMAgent) -> PMperception:
        # Funcion perceptual de PM
        worker_states = [(agent.id, action.new_state) for agent,action in self.workers_actions]
        resources = [(resource, count) for resource, count in self.resources.items()]
        risks = self.evaluate_risks(agent)
        opportunities = self.evaluate_opportunities(agent)
        team_motivation = self.get_team_motivation()
        return PMperception(actual_time=self.time, reports=self.reports, workers_state=worker_states, resources=resources, problems=self.problems, solved_problems=self.solved_problems, risks=risks, opportunities=opportunities, team_motivation=team_motivation) 
    

    def evaluate_risks(self, PM : PMAgent) -> List[Risk]:
        risks = []
        flag = True
        for risk in self.risks:
            for condition in risk:
                if not condition(PM) : 
                    flag = False
                    break
            if flag :
                risks.append(risk)
        return risks
    
    def evaluate_opportunities(self, PM : PMAgent) -> List[Opportunity]:
        opportunities = []
        flag = True
        for opportunity in self.opportunities:
            for condition in opportunity:
                if not condition(PM) : 
                    flag = False
                    break
            if flag :
                opportunities.append(opportunity)
        return opportunities
            