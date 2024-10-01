from collections import deque
import random
from PMOntologic.PMO import *
from Simulation.Rule import Agent, Rule
from Tasks.GeneticAlgorithm.Population import Population
from Tasks.GeneticAlgorithm.Tasks_combination import Tasks_combination, optimization_function
import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

class PMperception ():
    def __init__ (self,
                  reward,
                  actual_time=0,
                  reports=[],           #[(worker_id, task_id, progress)]
                  workers_state=[],     #[(worker_id, state)]
                  resources=[],         #[(resource_id, count)]
                  problems=[],          #[task_id]
                  solved_problems=[],   #[worker_id]
                  risks=[],             #[Risk]
                  opportunities=[],     #[Opportunities]
                  lazzy_agents=[],      #[worker_id]
                  team_motivation=0,
                  success=None,
                ) -> None:
        self.actual_time = actual_time
        self.workers_state = workers_state
        self.resources = resources
        self.problems = problems
        self.solved_problems = solved_problems
        self.team_motivation = team_motivation
        self.risks = risks
        self.opportunities = opportunities
        self.reports = reports
        self.lazzy_agents = lazzy_agents
        self.success = success
        self.reward = reward

    def __str__(self):
        return (f"\n PMperception:\n"
                f"  Actual Time: {self.actual_time}\n"
                f"  Reports: {self.reports}\n"
                f"  Workers' State: {self.workers_state}\n"
                f"  Resources: {self.resources}\n"
                f"  Problems: {self.problems}\n"
                f"  Solved Problems: {self.solved_problems}\n"
                f"  Team Motivation: {self.team_motivation}\n"
                f"  Risks: {self.risks}\n"
                f"  Opportunities: {self.opportunities}")



class PMAction():
    def __init__(self,
                 assignments=[],        #[(id_agente, tarea)]
                 ask_reports=[],        #[id_agente]
                 planning=None,
                 reassign=[],           #[(id_agente, tarea)]
                 work_on=None,          # tarea
                 cooperations=[],       #[((id_agente_1, id_agente_2), tarea)]
                 evaluate_performance=False,
                 motivate=[],           #[id_agente] 
                 priority=None, 
                 optimize=[],
                 take_chance=None
                ) -> None:
        self.assignments = assignments
        self.ask_reports = ask_reports
        self.planning = planning
        self.reassign = reassign
        self.work_on = work_on
        self.cooperations = cooperations
        self.evaluate_performance = evaluate_performance
        self.motivate = motivate
        self.priority = priority
        self.optimize = optimize
        self.take_chance = take_chance

    def __str__(self):
        return (f"\n PMAction:\n"
                f"  Assignments: {self.assignments}\n"
                f"  Ask Reports: {self.ask_reports}\n"
                f"  Planning: {self.planning}\n"
                f"  Reassign: {self.reassign}\n"
                f"  Work On: {self.work_on}\n"
                f"  Cooperations: {self.cooperations}\n"
                f"  Evaluate Performance: {self.evaluate_performance}\n"
                f"  Motivate: {self.motivate}\n"
                f"  Priority: {self.priority}\n"
                f"  Optimize: {self.optimize}\n"
                f"  Take Chance: {self.take_chance}")


class PMAgent(Agent):
    def __init__(self, min_motivation_team, initial_perception, rules, active_rules, ordered_tasks = None, project:Project = None, risky : float = 0.2, work_prob = 0.1, cooperation_prob = 0.5, exploration_rate : float = 0.1, generate_rules = False):
        self.perception = initial_perception
        self.project = project if project != None else Project()
        self.ordered_tasks = deque(self.get_best_permutation([task for task in self.project.tasks.values()])) if ordered_tasks == None else ordered_tasks
        self.risky = risky
        self.min_motivation_team = min_motivation_team
        self.milestones_count = 0
        self.average_time = sum([task.duration + 0.5 * task.difficulty for task in self.project.tasks.values()]) / len(self.project.tasks)
        self.work_prob = work_prob
        self.exploration_rate = exploration_rate
        self.generate_rules = generate_rules
        self.generator = None
        self.rules = rules  
        self.active_rules = active_rules
      
        self.beliefs = {
            'tasks': {task.id : 0 for task in self.project.tasks.values()},                  # {task_name: status} -1 fail, 0 not started, 1 finished
            'resources': {resource.id : resource.total for resource in self.project.resources.values()},              # {resource_name: available_amount}
            'resources_to_optimize':[],   # [resource_name]
            'workers':{},                 # {worker_id: (state, problem_solving}
            'team': self.perception.team_motivation, # team motivation
            'solved_problems':{},         # {worker_id : count}
            'problems': [],               # [task_id]
            'project': 0,                 # suma de los tiempos de las tareas realizadas
            'reward': 0,                  # suma de las recompenzas alcanzadas por las tareas hechas
            'milestones': {},             # {resource : [(time, count)]} para determinado recurso una lista de : para el tiempo time, debe haber el count
            'ask_report_at':{},           # {worker_id : time to ask for report}
            'tasks_completed_by':{},      # {worker_id : count} numero de tareas completadas por el trabajador
            'project_average_time': 0,
            'max_reward': 0,
            'cooperation_prob': cooperation_prob,
            'solutions': {},
            'lazzy_agents': {},           # {worker_id : count} cantidad de veces que el agente ha reportado problemas que habria podido resolver

            'rules': self.rules,          # {rule_id : Rule}

            'active_rules': self.active_rules         # [rule_id]
        }
        
        self.desires = {
            'assign':False,                 # deseo de asignar tareas
            'reassign':False,               #       de reasignar las tareas reportadas como problemas
            'cooperate':False,              #       de mandar a agentes a cooperar en una tarea dificil
            'work': False,                  #       de trabajar en uno de los problemas
            'ask_report': False,            #       de pedir reportes
            'number_of_tasks' : False,      #       de completar la mayor cantidad de tareas posibles
            'priority_of_tasks': False,     #       de completar primero las tareas de mayor prioridad
            'rewards': False,               #       de completar las tareas con mejores recompensas
            'optimize_resources': False,    #       de gastar la menor cantidad de recursos posibles
            'on_time': False,               #       de realizar las tareas antes de su deadline
            'avoid_risks': False,           #       de evitar riesgos
            'get_chances': False,           #       de tomar las oportunidades que se presenten
            'motivation': False,            #       de tener al equipo de trabajo motivado
        }

        self.intentions = {
            'assign':False,                 # intencion de asignar tareas
            'reassign':False,               #           de reasignar las tareas reportadas como problemas
            'cooperate':False,              #           de mandar a agentes a cooperar en una tarea dificil
            'ask_report': False,            #           de pedir reportes
            'evaluate': False,              #           de evaluar el progreso de los trabajadores
            'planning': False,              #           de planificar las tareas
            'work': False,                  #           de trabajar en uno de los problemas
            'motivate': False,              #           de motivar al equipo de trabajo
            'priority': False,              #           de cambiar la prioridad del equipo
            'optimize': False,              #           de optimizar algun recurso
            'prevention': False,            #           de prevenir riesgos activos
            'take_chance': False,           #           de tomar las oportunidades activas
        }


############### BRF - Belief Revision Function #####################

    def brf(self, verbose=False):
        """
        Actualiza las creencias del agente basándose en las percepciones y las creencias actuales.
        """
        # Actualizar el estado de los trabajadores
        for worker,state in self.perception.workers_state:
            self.beliefs['workers'][worker] = (state, self.beliefs['workers'][worker][1])

        # Actualizar los recursos y las recompenzas
        for resource, count in self.perception.resources :
            self.beliefs['resources'][resource] = count
        self.beliefs['reward'] = self.perception.reward

        # Actualizar los recursos que esten por debajo de lo planeado
        for resource in self.beliefs['resources'] :
            if len(self.beliefs['milestones'][resource]) > 0 and self.beliefs['milestones'][resource][0][0] <= self.perception.actual_time :
                if self.beliefs['milestones'][resource][0][1] > self.beliefs['resources'][resource] :
                    if not resource in self.beliefs['resources_to_optimize']:
                        self.beliefs['resources_to_optimize'].append(resource)
                else :
                    self.milestones_count += 1
                    if resource in self.beliefs['resources_to_optimize']:
                        self.beliefs['resources_to_optimize'].remove(resource)
                self.beliefs['milestones'][resource].pop(0)

        # Actualizar la motivacion del equipo
        self.beliefs['team'] = self.perception.team_motivation

        # Actualizar los problemas resueltos por los trabajadores
        for worker in self.perception.solved_problems :
            self.beliefs['solved_problems'][worker] += 1
            if self.beliefs['solved_problems'][worker] % 3 == 0 :
                self.beliefs['workers'][worker] = (self.beliefs['workers'][worker][0], self.beliefs['workers'][worker][1] * 1.05)      # Aumentamos la confianza en ese agente

        # Actualizar los problemas a solucionar
        for task_id in self.perception.problems :
            if task_id not in self.beliefs['problems']:
                self.beliefs['problems'].append(task_id)
            if task_id in self.beliefs['solutions'].keys():
                #print('disminuyendo probabilidad de ' + self.beliefs['solutions'][task_id] + ' al no resultar efectivo')
                if self.beliefs['solutions'][task_id] == 'cooperation_prob' :
                    self.beliefs['cooperation_prob'] = max(self.beliefs['cooperation_prob'] - 0.05, 0)
                    self.work_prob += 0.05
                else :
                    self.beliefs['cooperation_prob'] = min(self.beliefs['cooperation_prob'] + 0.05, 1)
                
        
        # Actualizar los reportes
        for worker, task, progress in self.perception.reports :
            self.beliefs['ask_report_at'][worker] = self.perception.actual_time + self.average_time
            if self.project.tasks[task].duration <= progress :    
                self.beliefs['tasks'][task] = 1
                self.beliefs['project'] += self.project.tasks[task].duration
                self.beliefs['tasks_completed_by'][worker] += 1


        # Actualizar la percepcion de trabajo de los agentes
        for worker in self.perception.lazzy_agents:
            self.beliefs['lazzy_agents'][worker] += 1
            if self.beliefs['lazzy_agents'][worker] % 3 == 0 :
                self.beliefs['workers'][worker] = (self.beliefs['workers'][worker][0], self.beliefs['workers'][worker][1] * 0.95)

        # Actualizar si la oportunidad tomada fue exito o fracaso
        if self.perception.success != None :
            self.risky = min(self.risky + 0.035, 1) if self.perception.success else max(self.risky - 0.035, 0)

        # Mandamos al agente a pensar si es tiempo
        if self.generate_rules and random.random() < 0.05:
            self.think_own_rules()

        if self.perception.actual_time % 150 == 0 :
            self.generate_milestones(5)

        if verbose:
            print('Creencias actualizadas del PM :')
            print("----------------------")
            for item, value in self.beliefs.items():
                print(item)
                print(value)


    ####################### DESIRES ##############################


    def generate_desires(self, verbose=False):
        """
        Genera los deseos del agente basados en sus creencias y en las metas propuestas.

        """
        # Ordenamos las reglas segun su peso 
        #print(self.beliefs['active_rules'])
        self.beliefs['active_rules'].sort(key = lambda x: self.beliefs['rules'][x].weight)

        for rule_id in self.beliefs['active_rules']:
            self.beliefs['rules'][rule_id].evaluate(self)

  
        if verbose :
                print(f'Deseos generados por el project manager :')
                print("----------------------")
                for desire,value in self.desires.items():
                    if value : print(desire)   


        ####################### INTENTIONS ############################

    def generate_intentions(self, verbose = False):
        """
        Convierte los deseos en intenciones basadas en las creencias actuales y las prioridades.
        """
        # Actualizar la intencion de asignar tareas 
        self.intentions['assign'] = self.desires['assign']

        # Actualizar la intencion de asignar tareas reportadas como problemas o trabajar en las mismas 
        self.intentions['work'] = self.desires['work']
        self.intentions['cooperate'] = self.desires['cooperate']
        self.intentions['reassign'] = self.desires['reassign']

        # Actualizar la intencion de pedir reporte de progreso
        self.intentions['ask_report'] = self.desires['ask_report']

        # Actualizar la intencion de motivar al equipo si esta el deseo
        self.intentions['motivate'] = self.desires['motivation']

        # Actualizar la prioridad del equipo
        self.intentions['priority'] = self.desires['number_of_tasks'] or self.desires['priority_of_tasks'] or self.desires['rewards'] or self.desires['on_time']

        # Actualizar si se quiere optimizar algun recurso
        self.intentions['optimize'] = self.desires['optimize_resources']

         # Actualizar si se quiere prevenir los riesgos
        self.intentions['prevention'] = self.desires['avoid_risks']

         # Actualizar si se quiere tomar alguna oportunidad
        self.intentions['take_chance'] = self.desires['get_chances']

        if random.random() < self.exploration_rate:
            # El agente explora, elige intenciones menos óptimas o no usuales
            chosen = random.choice(['work', 'reassign', 'cooperate'])
            self.intentions[chosen] = True

        if verbose :
            print(f'Intenciones generadas por el Project Manager :')
            print("----------------------")  
            for intention,value in self.intentions.items():
                if value : print(intention)


   ####################### EXECUTE ACTION #######################

    def execute_intentions(self, verbose=False):
        """
        Ejecuta las intenciones generadas.
        """
        # Buscamos entre los riesgos activos, los recursos a los que puede impactar
        if self.intentions['prevention'] :
            special = ['time', 'number_of_tasks', 'priority_of_tasks', 'rewards' ]
            self.intentions['prevention'] = False
            for risk in self.perception.risks :
                for impact in risk.impact:
                    if not impact in self.beliefs['resources_to_optimize'] and not impact in special:
                        self.beliefs['resources_to_optimize'].append(impact)    
                self.desires['on_time'] = self.desires['on_time'] or 'time' in risk.impact
                self.desires['number_of_tasks'] = self.desires['number_of_tasks'] or 'number_of_tasks' in risk.impact
                self.desires['priority_of_tasks'] = self.desires['priority_of_tasks'] or 'priority_of_tasks' in risk.impact
                self.desires['rewards'] = self.desires['rewards'] or 'rewards' in risk.impact

        # Buscamos reasignar las tareas problematicas
        reassign = []
        if self.intentions['reassign'] :
            for problem in self.beliefs['problems'] :
                d = self.project.tasks[problem].difficulty
                for worker in self.beliefs['workers']:
                    if self.beliefs['workers'][worker][1] >= d:
                        reassign.append((worker,problem))
                        self.beliefs['solutions'][problem] = 'reassignment_prob'
                        self.beliefs['problems'].remove(problem)
                        break
            self.intentions['reassign'] = False

        # Buscamos resolver los problemas mandando a agentes a cooperar
        cooperations = []
        if self.intentions['cooperate'] :
            self.intentions['cooperate'] = False
            workers = [ (w,t[1]) for w,t in self.beliefs['workers'].items()]
            for task in self.beliefs['problems']:
                i = random.randint(0,len(workers)-2)
                iterations = 0
                while workers[i][1] + workers[i+1][1] < self.project.tasks[task].difficulty and iterations < 10 :
                    i = random.randint(0,len(workers)-2) 
                    iterations += 1
                if workers[i][1] + workers[i+1][1] >= self.project.tasks[task].difficulty:
                    cooperations.append(((workers[i][0],workers[i+1][0]), task))
                    self.beliefs['solutions'][task] = 'cooperation_prob'
                    self.beliefs['problems'].remove(task)
                    break
        
        # Buscamos una asignacion que hacer si tenemos la intencion
        assignments = []
        if self.intentions['assign'] :
            self.intentions['assign'] =  False
            available = []
            for worker in self.beliefs['workers']:
                if self.beliefs['workers'][worker][0] == 0 :
                    available.append((worker, self.beliefs['workers'][worker][1]))
            available.sort(key=lambda x : x[1])
            tasks = []
            count = len(available)
            for i in range(min(count*3, len(self.ordered_tasks))):
                task = self.ordered_tasks.popleft()
                tasks.append((task.id, task.difficulty))
            # tasks.sort(key=lambda x : x[1])
            # for i,(task,_) in enumerate(tasks):
            #     assignments.append((available[i%count][0], task))
            count_tasks = {agent : 0 for agent,_ in available}
            for task, difficulty in tasks:
                filtered_workers = [w for w in available if count_tasks[w[0]] < 3]
                # Encontramos el trabajador cuyo 'problem solving' esté más cerca de la dificultad
                best_worker = min(filtered_workers, key=lambda w: abs(w[1] - difficulty))
                # Asignamos la tarea al trabajador seleccionado
                assignments.append((best_worker[0],task))
                count_tasks[best_worker[0]] += 1

        # Buscamos si quedo alguna tarea con demasiada dificultad como para reasignarla
        work_on = None
        if self.intentions['work'] and len(self.beliefs['problems']) > 0 :
            self.intentions['work'] = False
            work_on = self.beliefs['problems'][0]

        # Buscamos si el equipo necesita motivacion, y motivar a los que mas problemas han resuelto
        motivate = []
        if self.intentions['motivate'] :
            self.intentions['motivate'] = False
            workers = [(worker, count) for worker,count in self.beliefs['solved_problems'].items()]
            workers.sort(key=lambda par : par[1], reverse=True)
            for i in range(min(3,len(workers))) :
                motivate.append(workers[i][0])
            
        # Buscamos si tenemos alguna prioridad activa
        priority = None
        if self.intentions['priority'] :
            if self.desires['number_of_tasks'] : priority = 'tasks'
            if self.desires['priority_of_tasks'] : priority = 'priority'
            if self.desires['rewards'] : priority = 'reward'
            if self.desires['on_time'] : priority = 'time'
            # Si hay mas de una prioridad se sobrescribe, este orden es arbitrario 

        # Mandamos a optimizar recursos que sean necesarios
        optimize = []
        if self.intentions['optimize'] and len(self.beliefs['resources_to_optimize']) > 0:
            self.intentions['optimize'] = False
            optimize = self.beliefs['resources_to_optimize']

        # Buscamos las oportunidades que no nos afecten recursos ya afectados
        opportunities = []
        opportunity_taken = None
        if self.intentions['take_chance']:
            self.intentions['take_chance'] = False
            for opportunity in self.perception.opportunities:
                flag = False
                for impact in opportunity.impact:
                    if impact in self.beliefs['resources_to_optimize'] or (impact == 'time' and self.desires['on_time']):
                        flag = True
                        break
                if not flag:
                    opportunities.append(opportunity)
            if len(opportunities) == 0:
                opportunities = self.perception.opportunities
            best_opportunities = []
            for opportunity in opportunities:
                count = 0
                for benefit in opportunity.benefits:
                    if benefit in self.beliefs['resources_to_optimize'] or (benefit == 'time' and self.desires['on_time']):
                        count += 1
                if count > 0:
                    best_opportunities.append((opportunity, count))
            if len(best_opportunities) > 0 :
                best_opportunities.sort(key=lambda x : x[1], reverse=True)
                opportunity_taken = best_opportunities[0][0]
            else :
                i = random.randint(0, len(opportunities)-1)
                opportunity_taken = opportunities[i]

        # Buscamos que agentes deben reportar sus progresos si tenemos la intencion activa
        ask_reports = []
        if self.intentions['ask_report'] :
            self.intentions['ask_report'] = False
            for worker in self.beliefs['ask_report_at'] :
                if self.beliefs['workers'][worker][0] == 1 and self.beliefs['ask_report_at'][worker] <= self.perception.actual_time:
                    ask_reports.append(worker)

        return PMAction(assignments=assignments, ask_reports=ask_reports, reassign=reassign, work_on=work_on, cooperations=cooperations, motivate=motivate, priority=priority, optimize=optimize, take_chance=opportunity_taken)



    # Metodo para que el agente actúe dada una percepcion del Medio
    def act(self, P : PMperception, verbose = False) -> PMAction:
        self.perception = P
        self.brf(verbose=verbose)
        self.generate_desires(verbose=verbose)
        self.generate_intentions(verbose=verbose)
        return self.execute_intentions(verbose=verbose)
    
    # Le damos a conocer los trabajadores y su capacidad al PM
    def know_workers(self, workers):
        for id,ps in workers:
            self.beliefs['workers'][id] = (0,ps)
            self.beliefs['ask_report_at'][id] = self.average_time
            self.beliefs['solved_problems'][id] = 0
            self.beliefs['tasks_completed_by'][id] = 0
            self.beliefs['lazzy_agents'][id] = 0
        self.generate_milestones(10)
        if self.generate_rules:
            self.generator = RulesGenerator()


    # Buscamos el orden de taras mas optimo
    def get_best_permutation(self,tasks) :
        population = Population(50, tasks )
        population.optimize(optimization_function, 'maximize', n_generations=20 , distribution="aleatoria", mutation_pob=10)
        # print(population.optimal_variable_values)
        return population.optimal_variable_values
    
    
    def generate_milestones(self, n: int):
        """
        Genera hitos y proyecciones para el proyecto utilizando lógica difusa para
        valorar la situación del equipo y ajustar el tipo de hitos.
        """
        without = 0
        with_ = 0
        reward = 0
        count = 0

        # Generamos los hitos basados en la valoración del tipo
        for task in self.project.tasks.values():
            if task.status == 0:
                count += 1
                without += task.duration
                with_ += task.difficulty
                reward += task.reward
        project_average_time = (2 * without + with_) // 2
        self.beliefs['project_average_time'] = project_average_time
        self.beliefs['max_reward'] = reward
        self.average_time = project_average_time // count
        milestone_average_time = project_average_time // n
        without = 0
        with_ = 0
        next_milestone = 0
        resources_estimate = {resource.id: 0 for resource in self.project.resources.values()}

        self.beliefs['milestones']['tasks'] = []
        self.beliefs['milestones']['milestones'] = []
        self.beliefs['milestones']['priority'] = []

        # Recolectamos los datos necesarios para la evaluación difusa
        motivation_value = self.beliefs['team']
        problem_solving_value = sum(worker[1] for worker in self.beliefs['workers'].values()) / len(self.beliefs['workers'])
        reward = (self.beliefs['reward'] / self.beliefs['max_reward']) * 100
        project = self.beliefs['project'] / self.beliefs['project_average_time'] * 100
        
        # Pasamos los datos al sistema difuso
        progress_evaluation.input['motivation'] = motivation_value
        progress_evaluation.input['problem_solving'] = problem_solving_value
        progress_evaluation.input['reward'] = reward
        progress_evaluation.input['progress'] = project
        
        # Ejecutamos la simulación difusa para obtener como va el proyecto
        progress_evaluation.compute()
        if 'progress_evaluation' in progress_evaluation.output.keys():
            progress_evaluation_value = progress_evaluation.output['progress_evaluation']
        else: # En caso de que ninguna regla cubra el caso 
            progress_evaluation_value = 50

        # Evaluamos las reglas creadas por el propio agente segun su efectividad al aplicarlas
        if progress_evaluation_value < 40 :
            e = -1
        else :
            e = 1
        for rule in self.beliefs['active_rules']:
            if 'my_own_rule' in rule:
                self.beliefs['rules'][rule].weight += e
                

        # Definimos el tipo de hitos basado en la evaluación difusa
        if progress_evaluation_value < 40:
            milestone_type = 'conservador'
        elif 40 <= progress_evaluation_value <= 70:
            milestone_type = 'normal'
        else:
            milestone_type = 'entusiasta'

        #print(f"Tipo de hitos generado: {milestone_type}")

        for i, task in enumerate(self.ordered_tasks):
            without += task.duration
            with_ += task.difficulty
            time = (2 * without + with_) // 2
            resources_time = time

            # Ajuste según el tipo de hito
            if milestone_type == 'conservador':
                resources_time = 0.9 * time
                time *= 1.1  # Retrasamos los hitos
            elif milestone_type == 'entusiasta':
                time *= 0.9  # Aceleramos los hitos
                resources_time = 1.05 * time

            for resource in task.resources:
                resources_estimate[resource.id] += resource.total

            if time >= next_milestone:
                self.beliefs['milestones']['tasks'].append((self.perception.actual_time + time, i+1))

                for resource_id, count in resources_estimate.items():
                    remaining = self.project.resources[resource_id].total - count
                    self.beliefs['milestones'].setdefault(resource_id, []).append((self.perception.actual_time + resources_time, remaining))

                completed_milestones = len(self.beliefs['milestones']['tasks']) // 2
                self.beliefs['milestones']['milestones'].append((self.perception.actual_time + time, completed_milestones))

                next_milestone = time + milestone_average_time

        self.beliefs['milestones']['priority'].append((1000000000, 'rewards'))



    def think_own_rules(self):
        # Aqui el agente sera capaz de ver que condiciones se cumplen, y crear reglas con ellas segun su experiencia

        conditions = [
            (lambda beliefs: len(beliefs['workers']) < 5, "small team"),  # equipos pequeños
            (lambda beliefs: len(beliefs['workers']) > 5 and len(beliefs['workers']) < 15, "medium team"),  # medianos
            (lambda beliefs: len(beliefs['workers']) > 15, "big team"),  # grandes

            (lambda beliefs: sum(worker[1] for worker in beliefs['workers'].values()) // len(beliefs['workers']) <= 25, "poorly prepared team"),  # poco preparados
            (lambda beliefs: sum(worker[1] for worker in beliefs['workers'].values()) // len(beliefs['workers']) > 25 and sum(worker[1] for worker in beliefs['workers'].values()) // len(beliefs['workers']) <= 60, "moderately prepared team"),  # medianamente preparados
            (lambda beliefs: sum(worker[1] for worker in beliefs['workers'].values()) // len(beliefs['workers']) > 60, "highly prepared team"),  # altamente preparados

            (lambda beliefs: beliefs['team'] <= 30, "unmotivated team"),  # poco motivados
            (lambda beliefs: beliefs['team'] > 30 and beliefs['team'] <= 60, "moderately motivated team"),  # medianamente motivados
            (lambda beliefs: beliefs['team'] > 60, "highly motivated team"),  # altamente motivados

            (lambda beliefs: beliefs['cooperation_prob'] < 0.3, "uncooperative team"),  # poco colaborativos
            (lambda beliefs: beliefs['cooperation_prob'] >= 0.3 and beliefs['cooperation_prob'] <= 0.6, "moderately collaborative team"),  # medianamente colaborativos
            (lambda beliefs: beliefs['cooperation_prob'] > 0.6, "highly collaborative team"),  # altamente colaborativos

            (lambda beliefs: sum(count for count in beliefs['lazzy_agents'].values()) // len(beliefs['lazzy_agents']) < 5, "highly working team"),  # trabajadores
            (lambda beliefs: sum(count for count in beliefs['lazzy_agents'].values()) // len(beliefs['lazzy_agents']) >= 5 and sum(count for count in beliefs['lazzy_agents'].values()) // len(beliefs['lazzy_agents']) < 10, "moderately hardworking team"),  # medianamente trabajadores
            (lambda beliefs: sum(count for count in beliefs['lazzy_agents'].values()) // len(beliefs['lazzy_agents']) >= 10, "not very hardworking team"),  # poco trabajadores

            (lambda beliefs: sum(tasks for tasks in beliefs['tasks_completed_by'].values()) // len(beliefs['tasks']) < 0.33, "few tasks completed"),  # pocas tareas completadas
            (lambda beliefs: sum(tasks for tasks in beliefs['tasks_completed_by'].values()) // len(beliefs['tasks']) >= 0.33 and sum(tasks for tasks in beliefs['tasks_completed_by'].values()) // len(beliefs['tasks']) <= 0.66, "medium number of tasks completed"),  # mediano número de tareas
            (lambda beliefs: sum(tasks for tasks in beliefs['tasks_completed_by'].values()) // len(beliefs['tasks']) > 0.66, "many tasks completed"),  # muchas tareas completadas

            (lambda beliefs: len(beliefs['problems']) <= 3, "few problems"),  # pocos problemas
            (lambda beliefs: len(beliefs['problems']) > 3 and len(beliefs['problems']) < 7, "average number of problems"),  # cantidad media de problemas
            (lambda beliefs: len(beliefs['problems']) >= 7, "many problems"),  # muchos problemas

            (lambda beliefs: beliefs['reward'] < 0.33 * beliefs['max_reward'], "less than 30 percent of the rewards earned"),  # menos del 30% de los premios
            (lambda beliefs: beliefs['reward'] > 0.33 * beliefs['max_reward'] and beliefs['reward'] < 0.66 * beliefs['max_reward'], "between 30 and 60 percent of the rewards"),  # entre el 30% y 60% de los premios
            (lambda beliefs: beliefs['reward'] > 0.66 * beliefs['max_reward'], "more than 60 percent of the rewards earned"),  # más del 60% de los premios

            (lambda beliefs: beliefs['project'] < 0.33 * beliefs['project_average_time'], "less than 30 percent of project time"),  # menos del 30% del tiempo del proyecto
            (lambda beliefs: beliefs['project'] > 0.33 * beliefs['project_average_time'] and beliefs['project'] < 0.66 * beliefs['project_average_time'], "between 30 and 60 percent of the project time"),  # entre el 30% y 60% del tiempo del proyecto
            (lambda beliefs: beliefs['project'] > 0.66 * beliefs['project_average_time'], "more than 60 percent of project time")  # más del 60% del tiempo del proyecto
        ]

        true_conditions = []

        for condition in conditions:
            if condition[0](self.beliefs):
                true_conditions.append(condition)

        string_conditions = '['
        for condition in true_conditions:
            string_conditions = string_conditions + condition[1] + ','
        string_conditions = string_conditions[:-1] + ']'

        answer = self.generator.generate_rule(string_conditions)
        print(answer)

        desires = []
        chosen_conditions = []
        description = ''

        for condition in true_conditions:
            if condition[1] in answer:
                chosen_conditions.append(condition[0])
                description = description + condition[1] + '\n'

        description += ' => '

        for desire in self.desires.keys():
            if desire in answer :
                desires.append(desire) 
                description += desire + '\n'
  
        my_own_rule = OwnRule(id='my_own_rule' + str(len(self.beliefs['rules'])), weight=1, description= description, desires=desires, conditions=chosen_conditions)

        self.beliefs['rules'][my_own_rule.id] = my_own_rule
        self.beliefs['active_rules'].append(my_own_rule.id)


############################ RULES ################################

class OwnRule(Rule):
    # Regla que le sirve al agente para crear otras reglas
    def __init__(self, id, weight, description, desires, conditions):
        super().__init__(id, weight, description)
        self.desires = desires
        self.conditions = conditions

    def evaluate(self, agent: PMAgent):
        # Evaluamos si todas las condiciones se cumplen y activamos los deseos
        for condition in self.conditions:
            if not condition(agent.beliefs):
                return
        for desire in self.desires:
            agent.desires[desire] = True

class ReduceTimeRule(Rule):
    def __init__(self):
        self.id = 'ReduceTime'
        self.weight = 1
        self.description = 'Desire to reduce task time if the proposed plan is not met'

    def evaluate(self, agent: PMAgent):
        # Deseo de reducir el tiempo de las tareas si no cumple el plan propuesto
        if len(agent.beliefs['milestones']['tasks']) > 0 and agent.beliefs['milestones']['tasks'][0][0] <= agent.perception.actual_time :
            total = sum(agent.beliefs['tasks_completed_by'][worker] for worker in agent.beliefs['tasks_completed_by'])
            if total < agent.beliefs['milestones']['tasks'][0][1] :
                agent.desires['on_time'] = True
            else:
                agent.desires['on_time'] = False
                agent.milestones_count += 1
            agent.beliefs['milestones']['tasks'].pop(0)

class OptimizeResourceRule(Rule):
    def __init__(self):
        self.id = 'OptimizeResourc'
        self.weight = 2
        self.description = 'Desire to optimize a certain resource'

    def evaluate(self, agent: PMAgent):
        # Deseo de optimizar cierto recurso 
        if len(agent.beliefs['resources_to_optimize']) > 0 :
            agent.desires['optimize_resources'] = True


class AvoidRisksRule(Rule):
    def __init__(self):
        self.id = 'AvoidRisks'
        self.weight = 3
        self.description = 'Desire to avoid risks'

    def evaluate(self, agent: PMAgent):
        # Deseo de evitar riesgos
        if len(agent.perception.risks) > 0:
            risk_factor = random.uniform(0, 1)
            if risk_factor > agent.risky + (1 - agent.beliefs['team'] / 100):  # Adaptar lo arriesgado que sera según motivación
                agent.desires['avoid_risks'] = True
        else:
            agent.desires['avoid_risks'] = False

class ForgetRisksRule(Rule):
    def __init__(self):
        self.id = 'ForgetRisks'
        self.weight = 3
        self.description = 'Desire to forget risks completely'

    def evaluate(self, agent: PMAgent):
        # Deseo de olvidarse de los riesgos y no preocuparse mas por ellos
        if agent.risky >= 0.8 :
            if 'AvoidRisks' in agent.beliefs['active_rules']:
                agent.beliefs['active_rules'].remove('AvoidRisks') 
            agent.desires['avoid_risks'] = False


class TakeOpportunitiesRule(Rule):
    def __init__(self):
        self.id = 'TakeOpportunities'
        self.weight = 4
        self.description = 'Desire to take opportunities'

    def evaluate(self, agent: PMAgent):
        # Deseo de tomar oportunidades
        if len(agent.perception.opportunities) > 0 and random.random() < agent.risky + len(agent.perception.opportunities)/10 :
            agent.desires['get_chances'] = True
        else:
            agent.desires['get_chances'] = False


class KeepMotivationRule(Rule):
    def __init__(self):
        self.id = 'KeepMotivation'
        self.weight = 5
        self.description = 'Desire to keep team motivation above a certain value'

    def evaluate(self, agent: PMAgent):
        # Deseo de mantener la motivacion del equipo por encima de cierto valor
        if agent.beliefs['team'] <= agent.min_motivation_team :
            agent.desires['motivation'] = True 
        if len(agent.beliefs['milestones']['milestones']) > 0 and agent.beliefs['milestones']['milestones'][0][0] <= agent.perception.actual_time:
            if agent.beliefs['milestones']['milestones'][0][1] <= agent.milestones_count :
                agent.desires['motivation'] = True 
                agent.milestones_count += 1
                agent.beliefs['milestones']['milestones'].pop(0)
            else:
                agent.generate_milestones(len(agent.ordered_tasks)//5)

class ChangeTargetRule(Rule):
    def __init__(self):
        self.id = 'ChangeTarget'
        self.weight = 6
        self.description = 'Desire to do short tasks to increase the number of tasks, or priority tasks, or tasks with better rewards'

    def evaluate(self, agent: PMAgent):
        # Deseo de hacer tareas cortas para aumentar el numero de tareas, o tareas prioritarias, o tareas con mejores recompensas
        if len(agent.beliefs['milestones']['priority']) > 0 and agent.beliefs['milestones']['priority'][0][0] <= agent.perception.actual_time :
            if not agent.beliefs['milestones']['priority'][0][1] in agent.desires.keys():
                raise Exception('Hito con una prioridad no reconocida')
            else :
                agent.desires[self.beliefs['milestones']['priority'][0][1]] = True
            agent.beliefs['milestones']['priority'].pop(0)
            

class AssignRule(Rule):
    def __init__(self):
        self.id = 'Assign'
        self.weight = 7
        self.description = 'Update the desire to assign tasks if there are idle agents'

    def evaluate(self, agent: PMAgent):
        # Deseo de asignar tareas si hay agentes desocupados
        flag = False
        for state,_ in agent.beliefs['workers'].values():
            if state == 0:
                flag = True
                break
        agent.desires['assign'] = flag and len(agent.ordered_tasks) != 0


class ProblemsRule(Rule):
    def __init__(self):
        self.id = 'Problems'
        self.weight = 8
        self.description = 'Update the desire to assign tasks reported as problems or work on them'

    def evaluate(self, agent: PMAgent):
        # Deseo de asignar tareas reportadas como problemas o trabajar en las mismas 
        if len(agent.beliefs['problems']) > 0:
            max_ps = max(agent.beliefs['workers'][worker][1] for worker in agent.beliefs['workers'])
            max_problem = max(agent.project.tasks[task].difficulty for task in agent.beliefs['problems'])
            min_problem = min(agent.project.tasks[task].difficulty for task in agent.beliefs['problems'])

            r = random.random()
            agent.desires['work'] = max_problem > max_ps and r < agent.work_prob 
            agent.desires['cooperate'] =  r < agent.beliefs['cooperation_prob']
            agent.desires['reassign'] = min_problem < max_ps and r > agent.beliefs['cooperation_prob']
    

class AskReportRule(Rule):
    def __init__(self):
        self.id = 'AskReport'
        self.weight = 9
        self.description = 'Update the wish to request a progress report'

    def evaluate(self, agent: PMAgent):
         # Deseo de pedir reporte de progreso
        agent.desires['ask_report'] = False
        for _, time in agent.beliefs['ask_report_at'].items():
            if time <= agent.perception.actual_time:
                agent.desires['ask_report'] = True
                break


class DeleteActiveRule(Rule):
    def __init__(self):
        self.id = 'DeleteActive'
        self.weight = 10
        self.description = 'Delete active rules'

    def evaluate(self, agent: PMAgent):
         # Regla para eliminar las reglas que no resultaron efectivas
        for id,rule in agent.beliefs['rules'].items():
            if rule.weight <= 0 and id in agent.beliefs['active_rules']:
                agent.beliefs['active_rules'].remove(id)




################################## FUZZY LOGIC #######################################

# ¿Por qué no usar lógica difusa para que nuestro agente valore la situación del proyecto y genere hitos a corde?

import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl

# Definir las variables difusas 
motivation = ctrl.Antecedent(np.arange(0, 101, 1), 'motivation')
problem_solving = ctrl.Antecedent(np.arange(0, 101, 1), 'problem_solving')
reward = ctrl.Antecedent(np.arange(0, 101, 1), 'reward')
progress = ctrl.Antecedent(np.arange(0, 101, 1), 'progress')

# Definir la salida difusa (tipo de hitos)
progress_evaluation = ctrl.Consequent(np.arange(0, 101, 1), 'milestone_type')

# Funciones de pertenencia para la motivación
motivation['low'] = fuzz.trimf(motivation.universe, [0, 0, 50])
motivation['medium'] = fuzz.trimf(motivation.universe, [30, 50, 70])
motivation['high'] = fuzz.trimf(motivation.universe, [50, 100, 100])

# Funciones de pertenencia para la capacidad de resolución de problemas
problem_solving['low'] = fuzz.trimf(problem_solving.universe, [0, 0, 50])
problem_solving['medium'] = fuzz.trimf(problem_solving.universe, [30, 50, 70])
problem_solving['high'] = fuzz.trimf(problem_solving.universe, [50, 100, 100])

# Funciones de pertenencia para el progreso del proyecto
progress['low'] = fuzz.trimf(progress.universe, [0, 0, 50])
progress['medium'] = fuzz.trimf(progress.universe, [30, 50, 70])
progress['high'] = fuzz.trimf(progress.universe, [50, 100, 100])

# Funciones de pertenencia para las recompensas del proyecto
reward['low'] = fuzz.trimf(reward.universe, [0, 0, 50])
reward['medium'] = fuzz.trimf(reward.universe, [30, 50, 70])
reward['high'] = fuzz.trimf(reward.universe, [50, 100, 100])

# Funciones de pertenencia para el tipo de hitos
progress_evaluation['bad'] = fuzz.trimf(progress_evaluation.universe, [0, 0, 50])
progress_evaluation['normal'] = fuzz.trimf(progress_evaluation.universe, [30, 50, 70])
progress_evaluation['good'] = fuzz.trimf(progress_evaluation.universe, [50, 100, 100])

# Crear reglas
# Regla 1: Si la motivación es baja y la capacidad de resolución de problemas es baja, entonces el proyecto va mal.
rule1 = ctrl.Rule(motivation['low'] & problem_solving['low'], progress_evaluation['bad'])
# Regla 2: Si la motivación es media y la capacidad de resolución de problemas es media, entonces el proyecto va normal.
rule2 = ctrl.Rule(motivation['medium'] & problem_solving['medium'], progress_evaluation['normal'])
# Regla 3: Si la motivación es alta y la capacidad de resolución de problemas es alta, entonces el proyecto va bien.
rule3 = ctrl.Rule(motivation['high'] & problem_solving['high'], progress_evaluation['good'])
# Regla 4: Si el progreso del proyecto es bajo y las recompensas son bajas, el proyecto va mal.
rule4 = ctrl.Rule(progress['low'] & reward['low'], progress_evaluation['bad'])
# Regla 5: Si el progreso del proyecto es medio y las recompensas son medias, el proyecto va normal.
rule5 = ctrl.Rule(progress['medium'] & reward['medium'], progress_evaluation['normal'])
# Regla 6: Si el progreso del proyecto es alto y las recompensas son altas, el proyecto va bien.
rule6 = ctrl.Rule(progress['high'] & reward['high'], progress_evaluation['good'])
# Regla 7: Si la motivación es alta pero la capacidad de resolución de problemas es baja, y el progreso es bajo, el proyecto va mal (aunque haya buena motivación, se tienen problemas serios).
rule7 = ctrl.Rule(motivation['high'] & problem_solving['low'] & progress['low'], progress_evaluation['bad'])
# Regla 8: Si la motivación es media y la resolución de problemas es media, pero las recompensas son bajas, el proyecto va mal.
rule8 = ctrl.Rule(motivation['medium'] & problem_solving['medium'] & reward['low'], progress_evaluation['bad'])
# Regla 9: Si la motivación es alta y la capacidad de resolución de problemas es media, y el progreso es medio, el proyecto va normal.
rule9 = ctrl.Rule(motivation['high'] & problem_solving['medium'] & progress['medium'], progress_evaluation['normal'])
# Regla 10: Si la motivación es alta, la capacidad de resolución de problemas es alta y las recompensas son altas, el proyecto va bien.
rule10 = ctrl.Rule(motivation['high'] & problem_solving['high'] & reward['high'], progress_evaluation['good'])
# Regla 11: Si todas las variables son bajas, el proyecto va mal.
rule11 = ctrl.Rule(motivation['low'] & problem_solving['low'] & progress['low'] & reward['low'], progress_evaluation['bad'])
# Regla 12: Si todas las variables son medias, el proyecto va normal.
rule12 = ctrl.Rule(motivation['medium'] & problem_solving['medium'] & progress['medium'] & reward['medium'], progress_evaluation['normal'])
# Regla 13: Si todas las variables son altas, el proyecto va bien.
rule13 = ctrl.Rule(motivation['high'] & problem_solving['high'] & progress['high'] & reward['high'], progress_evaluation['good'])
# Regla 14: Si la motivación es baja y la recompensa es baja, el progreso es malo.
rule14 = ctrl.Rule(motivation['low'] & reward['low'], progress_evaluation['bad'])
# Regla 15: Si la motivación es media y la recompensa es alta, el progreso es normal.
rule15 = ctrl.Rule(motivation['medium'] & reward['high'], progress_evaluation['normal'])
# Regla 16: Si la capacidad de resolución de problemas es alta y el progreso es alto, el progreso es bueno.
rule16 = ctrl.Rule(problem_solving['high'] & progress['high'], progress_evaluation['good'])
# Regla 17: Si la capacidad de resolución de problemas es baja y el progreso es medio, el progreso es malo.
rule17 = ctrl.Rule(problem_solving['low'] & progress['medium'], progress_evaluation['bad'])
# Regla 18: Si el progreso es bajo y la recompensa es alta, el progreso es normal (compensación por recompensas).
rule18 = ctrl.Rule(progress['low'] & reward['high'], progress_evaluation['normal'])
# Regla 19: Si la motivación es alta, la capacidad de resolución de problemas es baja, pero la recompensa es alta, el progreso es normal.
rule19 = ctrl.Rule(motivation['high'] & problem_solving['low'] & reward['high'], progress_evaluation['normal'])
# Regla 20: Si la motivación es alta, el progreso es medio, y la recompensa es media, el progreso es bueno.
rule20 = ctrl.Rule(motivation['high'] & progress['medium'] & reward['medium'], progress_evaluation['good'])

# Crear el sistema de control difuso con todas las reglas
progress_ctrl = ctrl.ControlSystem([
    rule1, rule2, rule3, rule4, rule5, rule6, rule7, rule8, rule9, rule10,
    rule11, rule12, rule13, rule14, rule15, rule16, rule17, rule18, rule19, rule20
])
progress_evaluation = ctrl.ControlSystemSimulation(progress_ctrl)


################################ RULES GENERATOR #########################################

class RulesGenerator:
    def __init__(self, config_file='.env'):
        load_dotenv(config_file)
        self.api_key = os.environ['GENAI_API_KEY']
        genai.configure(api_key=self.api_key)
        
        self.chat = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="""
            You are an intelligent agent with BDI architecture that simulates a project manager. I will provide you with a list of wishes that could be activated, 
            so that later, when I give you a list of conditions that are met in the simulation, you can choose wishes from that list that you believe those conditions or a subset 
            of them would activate. . I want you to only return me a list with the subset of conditions that you chose, and another list with the subset of desires that would be activated. 
            Below I provide you with an example of what your answer should be, remember, I don't want any additional explanation, just the lists.
            conditions = ["small team", "average number of problems"]
            desires = ['reassign', 'work', 'on time'].
            The wish list is: ['assign', 'reassign', 'cooperate', 'work', 'ask_report', 'number_of_tasks', 'priority_of_tasks', 'rewards', 'optimize_resources', 'on_time', 'avoid_risks', 'get_chances', 'motivation']
            A small explanation of what each wish means in this context:
            'assign' desire to assign more tasks to workers;
            'reassign' desire to reassign tasks reported as problems;
            'cooperate' desire to send agents to cooperate in a difficult task;
            'work' desire to work on one of the problems even if the project manager loses availability for workers;
            'ask_report' desire to ask workers for task reports
            'number_of_tasks' desire to complete as many tasks as possible
            'priority_of_tasks' desire to complete highest priority tasks first
            'rewards' desire to complete tasks with better rewards
            'optimize_resources' desire to spend as few resources as possible
            'on_time' desire to complete tasks before their deadlines and reduce their time
            'avoid_risks' desire to avoid risks
            'get_chances' desire to take opportunities that present themselves
            'motivation' desire to have the work team motivated
            Now that you know the wishes, I will proceed to send you lists of conditions for you to choose from.
            """
        ).start_chat(history=[])
        

    def generate_rule(self, string : str = 'empty'):
        if string == 'empty':
            raise Exception('Conditions for rules cannot be empty')

        # Generar el mensaje para el modelo LLM
        message = f"""
        The list of conditions is as follows: {string}
        """
        response = self.chat.send_message(message)
        return response.text.strip()