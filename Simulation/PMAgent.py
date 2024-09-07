import collections
import random
from PMOntologic.PMO import *
from Tasks.GeneticAlgorithm.Population import Population
from Tasks.GeneticAlgorithm.Tasks_combination import Tasks_combination, optimization_function

class PMperception ():
    def __init__ (self,
                  actual_time=0,
                  reports=[],           #[(worker_id, task_id, progress)]
                  workers_state=[],     #[(worker_id, state)]
                  resources=[],         #[(resource_id, count)]
                  problems=[],          #[task_id]
                  solved_problems=[],   #[worker_id]
                  risks=[],             #[Risk]
                  opportunities=[],     #[Opportunities]
                  team_motivation=0,
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


    

class PMAgent:
    def __init__(self, min_motivation_team, initial_perception, project:Project = None, risky : float = 0.2):
        self.perception = initial_perception
        self.project = project if project != None else Project()
        self.ordered_tasks : collections.deque = self.get_best_permutation(self.project.tasks)
        self.risky = risky
        self.min_motivation_team = min_motivation_team
        self.milestones_count = 0
        self.average_time = 0

        self.beliefs = {
            'tasks': {task.id : -1 for task in self.project.tasks.values()},                  # {task_name: status} -1 not even started, 0 in progress, 1 finished
            'resources': {resource.id : resource.total for resource in self.project.resources.values()},              # {resource_name: available_amount}
            'resources_to_optimize':[],   # [resource_name]
            'workers':{},                 # {worker_id: (state, problem_solving}
            'team': 0,                    # team motivation
            'solved_problems':{},         # {worker_id : count}
            'problems': [],               # [task_id]
            'project': 0,                 # suma de los tiempos de las tareas realizadas
            'milestones': {},             # {resource : [(time, count)]} para determinado recurso una lista de : para el tiempo time, debe haber el count
            'ask_report_at':{},           # {worker_id : time to ask for report}
            'tasks_completed_by':{}       # {worker_id : count} numero de tareas completadas por el trabajador
        }
        
        self.desires = {
            'number_of_tasks' : False,      # deseo de completar la mayor cantidad de tareas posibles
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

        self.generate_milestones(10)


############### BRF - Belief Revision Function #####################

    def brf(self, verbose=False):
        """
        Actualiza las creencias del agente basándose en las percepciones y las creencias actuales.
        """
        # Actualizar el estado de los trabajadores
        for worker,state in self.perception.workers_state:
            self.beliefs['workers'][worker] = state

        # Actualizar los recursos 
        for resource, count in self.perception.resources :
            self.beliefs['resources'][resource] = count

        # Actualizar los recursos que esten por debajo de lo planeado
        for resource in self.beliefs['resources'] :
            if self.beliefs['milestones'][resource][0][0] <= self.perception.actual_time :
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

        # Actualizar los problemas a solucionar
        for task_id in self.perception.problems :
            self.beliefs['problems'].append(task_id)

        # Actualizar los reportes
        for worker, task, progress in self.perception.reports :
            self.beliefs['ask_report_at'][worker]+= self.average_time
            if self.project.tasks[task].duration <= progress :    
                self.beliefs['tasks'][task] = 1
                self.beliefs['project'] += self.project.tasks[task].duration
                self.beliefs['tasks_completed_by'][worker] += 1
            else :
                self.beliefs['tasks'][task] = 0

        if verbose:
            print('Creencias actualizadas del PM :')
            print("----------------------")
            print(self.beliefs)


    ####################### DESIRES ##############################


    def generate_desires(self, verbose=False):
        """
        Genera los deseos del agente basados en sus creencias y en las metas propuestas.

        """
        # Deseo de reducir el tiempo de las tareas si no cumple el plan propuesto
        if self.beliefs['milestones']['tasks'][0][0] <= self.perception.actual_time :
            total = sum(self.beliefs['tasks_completed_by'][worker] for worker in self.beliefs['tasks_completed_by'])
            if total < self.beliefs['milestones']['tasks'][0][1] :
                self.desires['on_time'] = True
            else:
                self.desires['on_time'] = False
                self.milestones_count += 1
            self.beliefs['milestones']['tasks'].pop(0)

        # Deseo de optimizar cierto recurso 
        if len(self.beliefs['resources_to_optimize']) > 0 :
            self.desires['optimize_resources'] = True

        # Deseo de evitar riesgos
        if len(self.perception.risks) > 0 and random.random() > self.risky :
            self.desires['avoid_risks'] = True
        else:
            self.desires['avoid_risks'] = False

        # Deseo de tomar oportunidades
        if len(self.perception.opportunities) > 0 and random.random() < self.risky :
            self.desires['get_chances'] = True
        else:
            self.desires['get_chances'] = False

        # Deseo de mantener la motivacion del equipo por encima de cierto valor
        if self.beliefs['team'] <= self.min_motivation_team :
            self.desires['motivation'] = True 
        if self.beliefs['milestones']['milestones'][0][0] <= self.perception.actual_time:
            if self.beliefs['milestones']['milestones'][0][1] <= self.milestones_count :
                self.desires['motivation'] = True 
                self.milestones_count += 1
            self.beliefs['milestones']['milestones'].pop(0)

        # Deseo de hacer tareas cortas para aumentar el numero de tareas, o tareas prioritarias, o tareas con mejores recompensas
        if self.beliefs['milestones']['priority'][0][0] <= self.perception.actual_time :
            if not self.beliefs['milestones']['priority'][0][1] in self.desires.keys():
                raise Exception('Hito con una prioridad no reconocida')
            else :
                self.desires[self.beliefs['milestones']['priority'][0][1]] = True
            self.beliefs['milestones']['priority'].pop(0)
            

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
        # Actualizar la intencion de asignar tareas si hay agentes desocupados
        flag = False
        for state,_ in self.beliefs['workers'].values():
            if state == 0:
                flag = True
                break
        self.intentions['assign'] = flag

        # Actualizar la intencion de asignar tareas reportadas como problemas o trabajar en las mismas 
        if len(self.perception.problems) > 0:
            max_ps = max(self.beliefs['workers'][worker][1] for worker in self.beliefs['workers'])
            max_problem = max(self.project.tasks[task].difficulty for task in self.perception.problems)
            min_problem = min(self.project.tasks[task].difficulty for task in self.perception.problems)
            if max_problem > max_ps :
                self.intentions['work'] = True
                if min_problem < max_ps:
                    self.intentions['reassign'] = True
            else:
                self.intentions['reassign'] = True

        # Actualizar la intencion de pedir reporte de progreso
        self.intentions['ask_report'] = False
        for _, time in self.beliefs['ask_report_at']:
            if time <= self.perception.actual_time:
                self.intentions['ask_report'] = True
                break
            
        # Actualizar la intencion de motivar al equipo si esta el deseo
        self.intentions['motivate'] = self.desires['motivation']

        # Actualizar la prioridad del equipo
        self.intentions['priority'] = self.desires['number_of_tasks'] or self.desires['priority_of_task'] or self.desires['rewards'] or self.desires['on_time']

        # Actualizar si se quiere optimizar algun recurso
        self.intentions['optimize'] = self.desires['optimize_resources']

         # Actualizar si se quiere prevenir los riesgos
        self.intentions['prevention'] = self.desires['avoid_risks']

         # Actualizar si se quiere tomar alguna oportunidad
        self.intentions['take_chance'] = self.desires['get_chances']


   ####################### EXECUTE ACTION #######################

    def execute_intentions(self, verbose=False):
        """
        Ejecuta las intenciones generadas.
        """
        # Buscamos entre los riesgos activos, los recursos a los que puede impactar
        if self.intentions['prevention'] :
            for risk in self.perception.risks :
                time = False
                for impact in risk.impact:
                    if not impact in self.beliefs['resources_to_optimize']:
                        self.beliefs['resources_to_optimize'].append(impact)    
                    if impact == 'time' : time = True
                self.desires['on_time'] = self.desires['on_time'] or time

        # Buscamos reasignar las tareas problematicas
        reassign = []
        if self.intentions['reassign'] :
            for problem in self.beliefs['problems'] :
                d = self.project.tasks[problem].difficulty
                for worker in self.beliefs['workers']:
                    if self.beliefs['workers'][worker][1] >= d:
                        reassign.append((worker,problem))
                        self.beliefs['problems'].remove(problem)

        # Buscamos una asignacion que hacer si tenemos la intencion, y mandar a cooperar en tareas dificiles
        assignments = []
        cooperations = []
        if self.intentions['assign'] :
            available = []
            for worker in self.beliefs['workers']:
                if self.beliefs['workers'][worker][0] == 0 :
                    available.append((worker, self.beliefs['workers'][worker][1]))
            available.sort(key=lambda x : x[1])
            for task in self.beliefs['problems']:
                for i in range(len(available)-1):
                    if available[i][1] + available[i+1][1] >= self.project.tasks[task].difficulty :
                        cooperations.append(((available[i][0],available[i+1][0]), task))
                        self.beliefs['problems'].remove(task)
                        break
            tasks = []
            count = len(available)
            for i in range(min(count*3, len(self.ordered_tasks))):
                task = self.ordered_tasks.popleft()
                tasks.append((task.id, task.difficulty))
            tasks.sort(key=lambda x : x[1])
            for i,(worker,_) in enumerate(available) :
                if i*3 < len(tasks) : assignments.append((worker, tasks[i*3][0]))
                if i*3 + 1 < len(tasks) : assignments.append((worker, tasks[i*3 + 1][0]))
                if i*3 + 2 < len(tasks) : assignments.append((worker, tasks[i*3 + 2][0]))

        # Buscamos si quedo alguna tarea con demasiada dificultad como para reasignarla
        work_on = None
        if self.intentions['work'] and len(self.beliefs['problems']) > 0 :
            work_on = self.beliefs['problems'][0]

        # Buscamos si el equipo necesita motivacion, y motivar a los que mas problemas han resuelto
        motivate = []
        if self.intentions['motivate'] :
            workers = [(worker, count) for worker,count in self.beliefs['solved_problems'].items()]
            workers.sort(key=lambda par : par[1], reverse=True)
            motivate.append(workers[0][0])
            motivate.append(workers[1][0])
            motivate.append(workers[2][0])

        # Buscamos si tenemos alguna prioridad activa
        priority = None
        if self.intentions['priority'] :
            if self.desires['number_of_tasks'] : priority = 'tasks'
            if self.desires['priority_of_tasks'] : priority = 'priority'
            if self.desires['rewards'] : priority = 'rewards'
            if self.desires['on_time'] : priority = 'time'
            # Si hay mas de una prioridad se sobrescribe, este orden es arbitrario 

        # Mandamos a optimizar recursos que sean necesarios
        optimize = []
        if self.intentions['optimize'] and len(self.beliefs['resources_to_optimize']) > 0:
            optimize = self.beliefs['resources_to_optimize']

        # Buscamos las oportunidades que no nos afecten recursos ya afectados
        opportunities = []
        opportunity_taken = None
        if self.intentions['take_chance']:
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
            for worker in self.beliefs['ask_report_at'] :
                if self.beliefs['ask_report_at'][worker] <= self.perception.actual_time:
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

    # Buscamos el orden de taras mas optimo
    def get_best_permutation(tasks) :
        population = Population(50, tasks )
        population.optimize(optimization_function, 'maximize', n_generations=20 , distribution="aleatoria", mutation_prob=0.1 )
        return population.optimal_variable_values
    
    # Generamos los hitos y proyecciones
    def generate_milestones(self, n : int):
        # Calculamos el tiempo que tomarian las tareas, sin y con problemas
        without, with_ = 0
        for task in self.project.tasks.values():
            without += task.duration
            with_ += task.difficulty
        project_average_time = (2 * without + with_) // 2
        self.average_time = project_average_time
        milestone_average_time = project_average_time // n # Partimos el proyecto en n hitos
        without, with_, next_milestone = 0
        resources_estimate = {}
        for i,task in enumerate(self.ordered_tasks) :
            without += task.duration
            with_ += task.difficulty
            time = (2 * without + with_) // 2
            for resource in task.resources:
                resources_estimate[resource.id] += resource.total
            if time >= next_milestone :
                self.beliefs['milestones']['tasks'].append((time, i+1))
                for id,count in resources_estimate.items():
                    self.beliefs['milestones'][id].append((time, self.project.resources[id].total - count))
                self.beliefs['milestones']['milestones'].append((time, len(resources_estimate)//2 ))
                next_milestone = time + milestone_average_time
        # Poner metas de prioridad
        self.beliefs['milestones']['priority'].append((1000000000, 'rewards'))

