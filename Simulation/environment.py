
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


import csv
import pprint
import random
from typing import List
from PMOntologic.Opportunity import Opportunity
from PMOntologic.Risk import Risk
from Simulation.WorkerAgent import WorkerAgent, WorkerPerception, WorkerAction
from Simulation.PMAgent import PMAgent, PMAction, PMperception
#from PMOntologic.PMO import Project


class WorkCenter(Environment): 
    """
    Clase para modelar el medio donde se desarrollaran nuestros agentes trabajadores y el Project Manager
    """
    def __init__(self, workers, PM , project):
        self.project_manager : PMAgent = PM  
        self.pm_action = PMAction()                                           # Accion devuelta por el PM para ejecutar
        self.workers : List[WorkerAgent] = workers                            # Lista de agentes trabajadores
        self.workers_actions : List[(WorkerAgent,WorkerAction)] = [(worker, WorkerAction()) for worker in self.workers]          # Acciones devueltas por los trabajadores 
        self.cooperations = []                                                # ((trabajador1, trabajador2), tarea) que deben cooperar en una tarea
        self.time = -10                                                         # Tiempo actual de la simulacion
        self.resources_priority = []                                          # Recursos que son prioridad a optimizar
        self.project = project                                                # Projecto a desarrollar por los agentes
        self.resources = {resource.id : resource.total for resource in self.project.resources.values()}      # Recursos actuales
        self.asking_report = { agente.id : False for agente in self.workers}
        self.reports = []                                                     # [(worker_id, task_id, progress)]
        self.problems = []                                                    # Ids de las tareas que presentaron problemas
        self.solved_problems = []                                             # [worker_id] trabajadores que resolvieron un problema durante la ultima jornada
        self.manager_available = True
        self.priority = None
        self.lazzy_agents = []
        self.workers_log = []                                                    # Log para guardar los datos de los trabajadores
        self.pm_log = []                                                         # Log para guardar los datos del PM
        self.w_log_fields = [
            'time', 'worker_id', 'new_state', 'work', 'get_task', 'report_progress', 'cooperate', 'escalate_problem', 'report_problem', 'rest'
        ]
        self.pm_log_fields = [
            'time', 'pm_assignments', 'pm_ask_reports', 'pm_reassign', 'pm_work_on', 'pm_cooperations', 'pm_evaluate_performance', 'pm_motivate', 'pm_priority', 'pm_optimize', 'pm_take_chance','problems_count', 'escalate_problem_count', 'cooperation_prob','trust_in_agents', 'completed_tasks', 'fail_tasks'
        ]
        self.problems_count = 0
        self.escalate_problem_count = 0

        self._see_functions = {
            WorkerAgent : self.worker_see_function,
            PMAgent : self.pm_see_function
        }
        
    def get_team_motivation(self):
        return sum(worker.motivation for worker in self.workers) // len(self.workers) 
        
    def end(self):
        for worker in self.workers:
            if worker.current_task != None or len(worker.task_queue) > 0 :
                return False
        return len(self.project_manager.ordered_tasks) == 0  and len(self.problems) == 0
    
    def log_data(self):
        """
        Función para registrar el estado actual de los agentes en el log
        """
        # Guardamos los datos del Project Manager (usamos len() para los arrays)
        pm_assignments = len(self.pm_action.assignments)
        pm_ask_reports = len(self.pm_action.ask_reports)
        pm_reassign = len(self.pm_action.reassign)
        pm_work_on = self.pm_action.work_on
        pm_cooperations = len(self.pm_action.cooperations)
        pm_evaluate_performance = self.pm_action.evaluate_performance
        pm_motivate = len(self.pm_action.motivate)
        pm_priority = self.pm_action.priority
        pm_optimize = len(self.pm_action.optimize)
        pm_take_chance = self.pm_action.take_chance

        self.pm_log.append({
            'time': self.time,
            'pm_assignments': pm_assignments,
            'pm_ask_reports': pm_ask_reports,
            'pm_reassign': pm_reassign,
            'pm_work_on': pm_work_on,
            'pm_cooperations': pm_cooperations,
            'pm_evaluate_performance': pm_evaluate_performance,
            'pm_motivate': pm_motivate,
            'pm_priority': pm_priority,
            'pm_optimize': pm_optimize,
            'pm_take_chance': pm_take_chance,
            'problems_count': self.problems_count,
            'escalate_problem_count': self.escalate_problem_count,
            'cooperation_prob' : self.project_manager.beliefs['cooperation_prob'],
            'trust_in_agents': [(worker, t[1]) for worker,t in self.project_manager.beliefs['workers'].items()],
            'completed_tasks' : sum([1 for task in self.project.tasks.values() if task.status == 1]),
            'fail_tasks' : sum([1 for task in self.project.tasks.values() if task.status == -1])
        })

        for worker, action in self.workers_actions:
            # Guardamos los atributos de WorkerAction en el log
            self.workers_log.append({
                'time': self.time,
                'worker_id': worker.id,
                'new_state': action.new_state,
                'work': action.work,
                'get_task': action.get_task,
                'report_progress': action.report_progress,
                'cooperate': action.cooperate,
                'escalate_problem': action.escalate_problem,
                'report_problem': action.report_problem,
                'rest': action.rest
            })

    def save_log_to_csv(self):
        """
        Función para guardar los logs archivos CSV sin sobrescribir los datos anteriores.
        """
        filename1 = 'Results/workers_log.csv'
        filename2 = 'Results/pm_log.csv'

        # Guardar el log de los trabajadores
        with open(filename1, mode='a', newline='') as file:  
            writer = csv.DictWriter(file, fieldnames=self.w_log_fields)

            # Escribe el encabezado solo si el archivo está vacío
            if file.tell() == 0:
                writer.writeheader()

            for data in self.workers_log:
                writer.writerow(data)

        # Guardar el log del project manager
        with open(filename2, mode='a', newline='') as file: 
            writer = csv.DictWriter(file, fieldnames=self.pm_log_fields)

            # Escribe el encabezado solo si el archivo está vacío
            if file.tell() == 0:
                writer.writeheader()

            for data in self.pm_log:
                writer.writerow(data)


    def next_step(self):
        self.time += 10    
        #print(self)
        self.cooperations.clear()

        P = self.see(self.project_manager)
        #print(P)
  
        action = self.project_manager.act(P, verbose=False)
        #print(action)
      
        pm_action = action
        self.pm_transform(pm_action)
        self.pm_action = pm_action

        self.reports.clear()
        self.solved_problems.clear()
        self.lazzy_agents.clear()

        workers_actions = []
        for worker in self.workers: 
            P = self.see(worker)
            action = worker.act(P, verbose=False)
            workers_actions.append((worker, action))

        self.worker_transform(workers_actions=workers_actions)
        self.workers_actions = workers_actions

        # Loggear los datos después de ejecutar el siguiente paso
        self.log_data()
 

    def pm_transform(self, pm_action : PMAction):
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

        # Reasignamos las tareas reportadas con problemas            
        for agent,task_id in pm_action.reassign:
            task = self.project.tasks[task_id]
            for worker in self.workers:
                if worker.id == agent :
                    worker.task_queue.insert(0,task)
                    self.problems.remove(task_id)
                    break

        # Activamos o no la disponibilidad del PM
        if pm_action.work_on != None :
            self.manager_available = False
            self.project.tasks[pm_action.work_on].difficulty -= 0.1 * self.project.tasks[pm_action.work_on].difficulty
            self.project.tasks[pm_action.work_on].duration -= 0.2 * self.project.tasks[pm_action.work_on].duration
        else :
            self.manager_available = True

        # Actualizamos la lista de los agentes que deben cooperar
        for cooperation in pm_action.cooperations:
            self.cooperations.append(cooperation)
            self.problems.remove(cooperation[1])

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
                    self.resources[benefit] *= random.uniform(1.01, 1.3)
            else :
                for impact in pm_action.take_chance.impact :
                    self.resources[impact] *= random.uniform(0.75, 0.99)



    # Modificamos el medio segun las acciones que hicieron los trabajadores
    def worker_transform(self, workers_actions):
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
                #print('los agentes van a coooooooooooooooooooooooooooooooooooooooooooooooooooooooooooperar')
                task = self.project.tasks[task_id] 
                task.difficulty = task.difficulty // 2
                task.problems_probability *= 0.5
                task.reward = task.reward // 2
                task.duration = task.duration // 2
                for resource in task.resources:
                    resource.total = resource.total // 2
                for worker in self.workers:
                    if worker.id == agents[0] or worker.id == agents[1]:
                        worker.task_queue.insert(0, task)
            else :
                self.problems.append(task_id)
        
        for agent,action in workers_actions :
            # Si el agente va a reportar progreso
            if action.report_progress :
                self.reports.append((agent.id, agent.current_task.id, agent.beliefs['task_progress']))
                self.asking_report[agent.id] = False
                # Si termino la tarea, disminuimos los recursos actuales
                if agent.current_task.duration <= agent.beliefs['task_progress']:
                    self.project.tasks[agent.current_task.id].status = 1
                    for resource in agent.current_task.resources :
                        self.resources[resource.id] -= resource.total
                    agent.current_task = None

            # Si el agente esta escalando un problema
            if action.escalate_problem :
                if agent.current_task.id not in self.problems:
                    self.problems.append(agent.current_task.id)   
                    self.escalate_problem_count += 1
                if agent.problem_solving >= agent.current_task.difficulty * 1.1:
                    self.lazzy_agents.append(agent.id)
                agent.current_task = None

            # Si el agente toma la proxima tarea
            if action.get_task:
                agent.beliefs['task_progress'] = 0
                agent.current_task = agent.task_queue.pop(0)
                for task in agent.current_task.dependencies:
                    if self.project.tasks[task.id].status == -1 :
                        self.project.tasks[agent.current_task.id].status = -1
                        break
                    if self.project.tasks[task.id].status == 0:
                        agent.task_queue.append(agent.current_task)
                        agent.current_task = agent.task_queue.pop(0)
                if agent.current_task.start > self.time and len(agent.task_queue) > 0:
                    #print(f'Aun no se puede comenzar esta tarea {agent.current_task.id}')
                    agent.task_queue.append(agent.current_task)
                    agent.current_task = agent.task_queue.pop(0)
                if agent.current_task.deadline < self.time + agent.current_task.duration:
                    #print('deadline excedido, tarea fallida')
                    self.project.tasks[agent.current_task.id].status = -1
                    agent.current_task = None

                
            # Si el agente reporta un problema que ya solucionó
            if action.report_problem :
                self.solved_problems.append(agent.id)     

            # Si el agente descansa se le sube la energia 
            if action.rest :
                agent.current_energy += 10       
            


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
                if action.work and agent.current_task != None and random.random() < agent.current_task.problems_probability:
                    problem_detected = True
                    self.problems_count += 1
                    worker.motivation *= 0.9
                    agent.current_task.problems_probability *= 0.5
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

                return WorkerPerception(task_available=task_available, task_progress=task_progress, cooperation_needed=cooperation_needed, problem_detected=problem_detected, problem_severity=problem_severity,manager_available=manager_available, progress_report=progress_report, team_motivation=team_motivation, resource_priority=self.resources_priority, priority=self.priority)
        return WorkerPerception()
                
            

    def pm_see_function(self, agent : PMAgent) -> PMperception:
        # Funcion perceptual de PM
        worker_states = [(agent.id, action.new_state) for agent,action in self.workers_actions]
        resources = [(resource, count) for resource, count in self.resources.items()]
        risks = self.evaluate_risks(agent)
        opportunities = self.evaluate_opportunities(agent)
        team_motivation = self.get_team_motivation()
        return PMperception(actual_time=self.time, reports=self.reports, workers_state=worker_states, resources=resources, problems=self.problems, solved_problems=self.solved_problems, risks=risks, opportunities=opportunities, team_motivation=team_motivation, lazzy_agents=self.lazzy_agents) 
    

    def evaluate_risks(self, PM : PMAgent) -> List[Risk]:
        risks = []
        for risk in self.project.risks:
            flag = True
            for condition in risk.events_or_conditions:
                if not condition(PM,self.time) : 
                    flag = False
                    break
            if flag :
                risks.append(risk)
        return risks
    
    def evaluate_opportunities(self, PM : PMAgent) -> List[Opportunity]:
        opportunities = []
        for opportunity in self.project.opportunities:
            flag = True
            for condition in opportunity.events_or_conditions:
                if not condition(PM,self.time) : 
                    flag = False
                    break
            if flag :
                opportunities.append(opportunity)
        return opportunities



    def __str__(self):
        return (f"\n WorkCenter:\n"
                f"Time: {self.time}\n"
                f"Resources: {self.resources}\n"
                f"Reports: {self.reports}\n"
                f"Problems: {self.problems}\n"
                f"Solved Problems: {self.solved_problems}\n"
                f"Manager Available: {self.manager_available}\n"
                f"Priority: {self.priority}\n"
                f"Asking_Report: {[worker for worker, value in self.asking_report.items() if value]}\n"
                f"Cooperations:{[(workers, task) for workers,task in self.cooperations]}\n"
                f"Problems count :{self.problems_count}\n")
    
                #f"Workers Actions : {[ (worker,action) for worker,action in self.workers_actions]}")
    