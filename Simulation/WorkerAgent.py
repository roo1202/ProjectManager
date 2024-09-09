################################################################
######################### WORKER ###############################
################################################################

import random
from Tasks.task import Task

####################### PERCEPTION #############################

class WorkerPerception():
    def __init__(self, 
                 task_available=False, 
                 task_progress=0, 
                 cooperation_needed=False, 
                 problem_detected=False, 
                 problem_severity=0, 
                 priority=None,
                 resource_priority=[], 
                 manager_available=True, 
                 coworkers = {}, 
                 progress_report = False,
                 team_motivation = 100,
                 ) -> None:
        self.task_available = task_available
        self.task_progress = task_progress
        self.cooperation_needed = cooperation_needed
        self.problem_detected = problem_detected
        self.problem_severity = problem_severity
        self.priority = priority
        self.manager_available = manager_available
        self.coworkers = coworkers
        self.progress_report = progress_report
        self.team_motivation = team_motivation
        self.resource_priority = resource_priority


    def __str__(self):
        return (f"\n WorkerPerception:\n"
                f"Task available: {self.task_available}\n"
                f"Task progress: {self.task_progress}\n"
                f"Cooperation needed: {self.cooperation_needed}\n"
                f"Problem detected: {self.problem_detected}\n"
                f"Problem severuty: {self.problem_severity}\n"
                f"Priority: {self.priority}\n"
                f"Resource priority: {[resource.id for resource in self.resource_priority]}\n"
                f"Manager Available: {self.manager_available}\n"
                f"Progress report: {self.progress_report}\n"
                f"Team motivation: {self.team_motivation}")


########################## ACTION ##############################

class WorkerAction():
    def __init__(self,
                new_state=0,
                work = False,
                get_task = False,
                report_progress = False,
                cooperate = False,
                escalate_problem = False,
                report_problem = False,
                rest = False
                ) -> None:
        self.new_state = new_state
        self.get_task = get_task
        self.report_progress = report_progress
        self.cooperate = cooperate
        self.escalate_problem = escalate_problem
        self.report_problem = report_problem
        self.rest = rest
        self.work = work

    def __str__(self):
        return (f"\n WorkerAction:\n"
                f"  New State: {self.new_state}\n"
                f"  Work: {self.work}\n"
                f"  Get Task: {self.get_task}\n"
                f"  Report Progress: {self.report_progress}\n"
                f"  Cooperate: {self.cooperate}\n"
                f"  Escalate Problem: {self.escalate_problem}\n"
                f"  Report Problem: {self.report_problem}\n"
                f"  Rest: {self.rest}")


####################### AGENT WORKER #################################

class WorkerAgent:
    def __init__(self, 
                 id, 
                 problem_solving,
                 current_task=None, 
                 task_queue=None, 
                 coworkers=None,
                 perception=None,
                 max_energy=100,
                 min_motivation = 10,
                 min_energy = 10,
                 min_friendship = 10,
                 beliefs=None):
        """
        Inicializa un agente trabajador.

        :param id: Identificador único del trabajador.
        :param current_task: Tarea actual que el trabajador está realizando (None si no tiene tarea).
        :param task_queue: Cola de tareas pendientes asignadas al trabajador.
        :param manager: Referencia al Project Manager (otro agente o entidad).
        :param coworkers: Lista de referencias a otros trabajadores (otros agentes).
        :param perception: Objeto que encapsula las percepciones del trabajador.
        """
        self.id = id
        self.current_task = current_task
        self.task_queue = task_queue if task_queue is not None else []
        self.coworkers = coworkers if coworkers is not None else []
        self.perception = perception if perception is not None else WorkerPerception()
        self.min_motivation = min_motivation    # Nivel de motivacion minima para considerarse motivado
        self.min_energy = min_energy            # Nivel de energia minimo para trabajar
        self.current_energy = 0                 # Nivel de energia actual para trabajar
        self.max_energy = max_energy            # Nivel de energia maximo del agente
        self.motivation = 100                     # Nivel de motivacion personal del agente
        self.min_friendship = min_friendship    # Nivel necesario para que el agente coopere con otro
        self.problem_solving = problem_solving  # Capacidad de resolver problemas de un agente

        self.beliefs = beliefs if beliefs is not None else {
            'task_assigned': False,    # si se tiene una tarea asignada actualmente
            'task_progress': 0,        # el progreso que tiene la tarea actual
            'progress_reported': 0,    # -1 pendiente de reportar, 0 no hay que reportar, 1 reportado
            'problem_detected': 0,     # -1 pendiente de resolver, 0 no hay problema, 1 resuelto
            'cooperation_required': 0, # -1 pendiente para cooperar, 0 no necesario cooperacion, 1 cooperando
            'respect' : 0,             # respeto por el ProjectManager
            'team_motivation' : 0,     # nivel de motivacion del equipo
            'motivated': False,        # si el agente se encuentra motivado para trabajar  
            'friendships': {}          # {name : level} nivel de amistad con tus compañeros
        }

        self.desires = {
            'work' : False,                 # deseo de completar la tarea actual
            'avoid_problems': False,        #       de evitar resolver los problemas elevandolos directamente al PM
            'cooperate': False,             #       de cooperar con otros trabajadores
            'keep_energy': False,           #       de mantener la energia sobre cierto nivel
            'report_progress': False        #       de reportar los progresos de las tareas al PM sin que este necesariamente lo requiera
        }

        self.intentions = {
            'get_work':False,
            'do_task': False,
            'escalate_problem': False,
            'solve_problem': False,
            'cooperate': False,
            'report_progress': False,
            'rest': False
        }
    
        
############### BRF - Belief Revision Function #####################

    def brf(self, verbose=False):
        """
        Actualiza las creencias del agente basándose en las percepciones y las creencias actuales.
        """
        # Actualizar la motivacion del equipo y la propia del agente
        self.beliefs['team_motivation'] = self.perception.team_motivation
        self.motivation = (self.motivation + self.perception.team_motivation) // 2
        self.beliefs['motivated'] = self.motivation > self.min_motivation

        # Actualizar si se han asignado tareas al agente
        if self.current_task != None or len(self.task_queue) > 0:
            self.beliefs['task_assigned'] = True

        # Actualizar si el agente esta en alguna tarea para disminuir la energia
        if self.perception.task_progress > 0 :
            self.beliefs['task_progress'] += self.perception.task_progress
            self.current_energy -= self.perception.task_progress

        # Actualizar creencia sobre si el progreso ha sido reportado
        if self.perception.progress_report :
            self.beliefs['progress_reported'] = -1      # Se marca que debes el reporte
        elif self.beliefs['progress_reported'] == 1:    # Ya reporto el progreso
            self.beliefs['progress_reported'] = 0   

        # Actualizar creencia sobre si se ha detectado un problema
        if self.perception.problem_detected:
            self.beliefs['problem_detected'] = -1      # Se marca pendiente de un problema
        elif self.beliefs['problem_detected'] == 1:    # Ya resolvio el problema
            self.beliefs['problem_detected'] = 0   

        # Actualizar creencia sobre si se necesita cooperación
        if not self.perception.cooperation_needed:
            self.beliefs['cooperation_required'] = 0
        else :
            self.beliefs['cooperation_required'] = -1

        # Actualizar relaciones con los compañeros de trabajo
        if len(self.perception.coworkers.items()) > 0 :
            for coworker, value in self.perception.coworkers.items() :
                self.beliefs['friendships'][coworker] += value

        # Actualizar la prioridad de las tareas
        if self.perception.priority != None and self.current_task != None:
            if self.perception.priority == 'time':
                self.current_task.duration -= 10
                self.current_task.reward -= 10     
            else :
                self.order_tasks_queue(self.perception.priority)   
        else :
            self.order_tasks_queue('deadline')
                
        # Actualizar si existen recursos a optimizar
        if len(self.perception.resource_priority) > 0 :
            for resource in self.current_task.resources:
                if resource.name in self.perception.resource_priority and resource.total >= 10 and self.current_task.reward >= 10:
                    resource.total -= 10
                    self.current_task.reward -= 10
        

        if True :
            print(f'Creencias actualizadas del agente {self.id} :')
            print("----------------------")
            print(self.beliefs)
            print(f'trabajando en la tarea {self.current_task}')
            print(self.task_queue)



####################### DESIRES ##############################


    def generate_desires(self, verbose=False):
            """
            Genera los deseos del agente basados en sus creencias.

            """
            # Deseo de trabajar si el trabajador está motivado
            if self.beliefs['motivated']:
                self.desires['work'] = True
            else :
                self.desires['work'] = False

            # Deseo de reportar el progreso si es necesario
            if self.beliefs['progress_reported'] == -1 :
                self.desires['report_progress'] = True
            else :
                self.desires['report_progress'] = False

            # Deseo de cooperar si se requiere
            if self.beliefs['cooperation_required'] == -1:
                for friend,value in self.perception.coworkers.items():
                    if value == 0 and self.beliefs['friendships'][friend] > self.min_friendship:
                        self.desires['cooperate'] = True
            else:
                self.desires['cooperate'] = False

            # Deseo de reportar o solucionar un problema
            if self.beliefs['problem_detected'] == -1 :
                if self.problem_solving >= (self.perception.problem_severity * random.uniform(0,2) ): 
                    self.desires['avoid_problems'] = False
                else :
                    self.desires['avoid_problems'] = True

            # Deseo de descansar si no hay tareas disponibles y se necesita recuperar energía
            if not self.beliefs['task_assigned'] or self.current_energy <= self.min_energy:
                self.desires['keep_energy'] = True 
            else :
                self.desires['keep_energy'] = False


            if verbose :
                print(f'Deseos generados por el agente {self.id} :')
                print("----------------------")
                for desire,value in self.desires.items():
                    if value : print(desire)

            
        
        ####################### INTENTIONS ############################

    def generate_intentions(self, verbose = False):
        """
        Convierte los deseos en intenciones basadas en las creencias actuales y las prioridades.
        """
        # Si el agente no tiene deseo de trabajar su intencion es descansar
        if not self.desires['work'] and random.random() > 0.1: # 90% de probabilidad de descansar
            self.intentions['rest'] = True

        # Si el agente tiene el deseo de trabajar y tiene alguna tarea, tendra la intencion de hacerla
        if self.desires['work'] and self.beliefs['task_assigned'] :
            if self.current_task != None and self.beliefs['task_progress'] < self.current_task.duration:
                self.intentions['do_task'] = True
            else :
                self.intentions['get_work'] = True

        # Si el agente no tiene deseos de resolver los problemas, los escalara al PM
        if self.desires['avoid_problems'] :
            self.intentions['escalate_problem'] = True
        else:
            if self.beliefs['problem_detected'] == -1:
                self.intentions['solve_problem'] = random.random() < self.beliefs['team_motivation'] / 100  # intencion de resolver el problema segun la motivacion del equipo
                self.intentions['escalate_problem'] = not self.intentions['solve_problem'] 

        # Si el agente tiene deseo de cooperar y no esta realizando ninguna tarea
        if self.desires['cooperate'] and not self.intentions['do_task']:
            self.intentions['cooperate'] = random.random() > 0.1  # 90% de probabilidad de cooperar
         
        # Si el agente termino una tarea reporta el progreso o si lo requiere
        if self.current_task != None and (self.beliefs['task_progress'] >= self.current_task.duration or self.desires['report_progress']):
            self.intentions['report_progress'] = True


        if verbose :
            print(f'Intenciones generadas por el agente {self.id} :')
            print("----------------------")  
            for intention,value in self.intentions.items():
                if value : print(intention)
            

    ####################### EXECUTE ACTION #######################

    def execute_intentions(self, verbose=False):
        """
        Ejecuta las intenciones generadas.
        """
        rest = False
        report_problem = False
        escalate_problem = False
        report_progress = False
        get_task = False
        work = False
        cooperate = False
        # Descansar si el agente tiene esa intencion
        if self.intentions['rest'] :
            self.intentions['rest'] = False
            if not self.perception.task_available :
                self.motivation += random.randint(5, 15)
            rest = True
            return WorkerAction(new_state=0, work=work, get_task=get_task, report_progress=report_progress, cooperate=cooperate, escalate_problem=escalate_problem, report_problem=report_problem, rest=rest)
        
        # Resolver el problema si fue detectado
        if self.intentions['solve_problem'] :
            self.beliefs['task_progress'] -= self.perception.problem_severity
            if random.random() < 0.2 :
                self.problem_solving += 1
            self.intentions['solve_problem'] = False
            self.beliefs['problem_detected'] = 0
            report_problem = True
            work = True
            return WorkerAction(new_state=1, work=work, get_task=get_task, report_progress=report_progress, cooperate=cooperate, escalate_problem=escalate_problem, report_problem=report_problem, rest=rest)
        
        # Conseguir una tarea si no se tiene ninguna
        if self.intentions['get_work'] and len(self.task_queue) > 0 :
            self.intentions['get_work'] = False
            get_task = True

        # Reportar progreso de una tarea si el PM lo requiere
        if self.intentions['report_progress'] :
            self.intentions['report_progress'] = False
            self.desires['report_progress'] = False
            self.beliefs['progress_reported'] = 1
            report_progress=True
            return WorkerAction(new_state=1, work=work, get_task=get_task, report_progress=report_progress, cooperate=cooperate, escalate_problem=escalate_problem, report_problem=report_problem, rest=rest)
        
        # Escalar el problema al PM
        if self.intentions['escalate_problem'] :
            self.intentions['escalate_problem'] = False
            self.beliefs['problem_detected'] = 0
            escalate_problem = True
            return WorkerAction(new_state=1, work=work, get_task=get_task, report_progress=report_progress, cooperate=cooperate, escalate_problem=escalate_problem, report_problem=report_problem, rest=rest)
        
        # Hacer la tarea actual
        if self.intentions['do_task'] and self.beliefs['task_assigned'] :
            work = True
        
        # Cooperar con otro agente
        if self.intentions['cooperate'] :
            self.intentions['cooperate'] = False
            cooperate=True
        
        return WorkerAction(new_state=1, work=work, get_task=get_task, report_progress=report_progress, cooperate=cooperate, escalate_problem=escalate_problem, report_problem=report_problem, rest=rest)
    

    # Metodo para que el agente actúe dada una percepcion del Medio

    def act(self, P : WorkerPerception, verbose = False) -> WorkerAction:
        self.perception = P
        self.brf(verbose=verbose)
        self.generate_desires(verbose=verbose)
        self.generate_intentions(verbose=verbose)
        return self.execute_intentions(verbose=True)
    
    def order_tasks_queue(self, priority):
        if priority == 'tasks':  # Ordenar por duración (las de menor duración primero)
            self.task_queue.sort(key=lambda task: task.duration)
        elif priority == 'priority':  # Ordenar por prioridad (las de mayor prioridad primero)
            self.task_queue.sort(key=lambda task: task.priority, reverse=True)
        elif priority == 'reward':  # Ordenar por recompensa (las de mayor recompensa primero)
            self.task_queue.sort(key=lambda task: task.reward, reverse=True)
        elif priority == 'deadline': # Ordenar por fecha de entrega maxima
            self.task_queue.sort(key=lambda task: task.deadline)
        else:
            raise ValueError(f"Prioridad desconocida: {priority}")
        
    def __str__(self):
        return (f"\n WorkerAgent (ID: {self.id}):\n"
                f"  Current Task: {self.current_task}\n"
                f"  Task Queue: {self.task_queue}\n"
                f"  Coworkers: {self.coworkers}\n"
                f"  Current Energy: {self.current_energy}/{self.max_energy}\n"
                f"  Motivation: {self.motivation} (Min: {self.min_motivation})\n"
                f"  Problem Solving: {self.problem_solving}\n"
                f"  Beliefs: {self.beliefs}\n"
                f"  Desires: {[desire for desire, value in self.desires.items() if value ]}\n"
                f"  Intentions: {[intention for intention, value in self.intentions.items() if value]}")



        

    
