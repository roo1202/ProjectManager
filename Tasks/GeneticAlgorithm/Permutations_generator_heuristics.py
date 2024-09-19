from collections import deque
from Tasks.task import Task
import random
from typing import List, Dict

def generate_permutation(tasks: List[Task], verbose=False) -> List[Task]:
    '''
        Generar una permutation con un grado de aleatoriedad, utilizando orden topologico y una funcion de ponderacion
    '''
    graph = get_graph(tasks)
    if verbose:
        print("Estructura del grafo: ")
        print(graph)
    
    order = topologic_order(graph)
    if verbose:
        print("Orden topologico: ")
        print(order)
    
    order = mutation(graph, order)
    if verbose:
        print("Orden topologico mutado: ")
        print(order)
    
    return pondered_order(order, tasks)

def get_graph(tasks: List[Task]) -> Dict[int, List[Task]]:
    '''
        Generar un grafo de las dependencias a partir de una Lista de tareas
    '''
    graph = {}
    
    for task in tasks:
        graph[task.id] = []
    
    for task in tasks:
        for dependency in task.dependencies:
                graph[dependency.id].append(task)
            
    return graph

def topologic_order(graph: Dict[int, List[Task]]) -> List[List[int]]:
    '''
        Ordenar un grafo topologicamente
    '''
    
    indegree = {}
    level = {}
    for key in graph:
        indegree[key] = 0
    
    for key in graph:
        for task in graph[key]:
            indegree[task.id] += 1
    
    queue = deque()
    for key in indegree:
        if indegree[key] == 0:
            queue.append(key)
            level[key] = 0
    
    max_level = 0
    while queue:
        key = random.choice(queue)
        queue.remove(key)
        max_level = max(max_level, level[key])
        
        for task in graph[key]:
            indegree[task.id] -= 1
            
            if indegree[task.id] == 0:
                queue.append(task.id)
                level[task.id] = level[key] + 1
    
    order = [[] for _ in range(max_level + 1)]
    
    for key in level:
        order[level[key]].append(key)
    
    return order

def random_order(order: List[List[int]], tasks: List[Task]) -> List[Task]:
    '''
        Generar una permutacion aleatoria en cada uno de los niveles
    '''
    
    for i in range(len(order)):
        random.shuffle(order[i])
    
    permutation = []
    for level in order:
        permutation += level
    
    dict = {}

    for task in tasks:
        dict[task.id] = task
    
    return [dict[x] for x in permutation]

def pondered_order(order: List[List[int]], tasks: List[Task]) -> List[Task]:
    '''
        Generar una permutacion ponderada en cada uno de los niveles
    '''
    dict = {}

    for task in tasks:
        dict[task.id] = task

    for i in range(len(order)):
        order[i].sort(key=lambda x:random.random()*dict[x].reward/(dict[x].duration * dict[x].duration * dict[x].difficulty * dict[x].problems_probability * (dict[x].deadline-dict[x].start)), reverse=True)
    
    permutation = []
    for level in order:
        permutation += level
    
    return [dict[x] for x in permutation]


def mutation(graph: Dict[int, List[Task]], order: List[List[int]]) -> List[List[int]]:
    '''
        Dado un orden topologico y una lista de tareas, `empuja` una tarea al siguiente nivel junto con todas las tareas que dependen d esta
    '''
    
    new_order = [[] for i in range(len(order) + 2)]
    
    task_index = random.randint(0, len(graph) - 1)
    
    for i,k in enumerate(graph.keys()):
        if i == task_index:
            task_index = k
            break

    task_level = 0
    
    for level, tasks in enumerate(order):
        if task_index in tasks:
            task_level = level       
            
    queue = deque()
    queue.append((task_index, task_level+1))
    processed_tasks = set()
    
    while queue:
        current_task, current_level = queue.popleft()
        new_order[current_level].append(current_task)
        
        processed_tasks.add(current_task)
        
        for task in graph[current_task]:
            queue.append((task.id, current_level + 1))
    
    for i in range(len(order)):
        for task in order[i]:
            if task not in processed_tasks:
                new_order[i].append(task)
    
    return new_order

def dependency_aware_crossover(parent1: List[Task], parent2: List[Task], verbose =False) -> List[Task]:
    '''
        Realiza un crossover respetando las dependencias entre las tareas.
        Combina dos permutaciones garantizando que el orden de las dependencias no se rompa.
    '''
    child = []
    placed_tasks = set()

    segment_length = random.randint(1, len(parent1) // 2) 
    for task in parent1[:segment_length]:
        child.append(task)
        placed_tasks.add(task.id)
    
    for task in parent2:
        if task.id not in placed_tasks:
            dependencies_satisfied = all(dependency.id in placed_tasks for dependency in task.dependencies)
            if dependencies_satisfied:
                child.append(task)
                placed_tasks.add(task.id)
    
    for task in parent1:
        if task.id not in placed_tasks:
            child.append(task)
            placed_tasks.add(task.id)
    
    return child
