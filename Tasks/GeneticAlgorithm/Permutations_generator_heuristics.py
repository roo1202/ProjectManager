from Tasks.task import Task
import random
from typing import List

def generate_permutation(tasks: List[Task]) -> List[Task]:
    '''
        Generar una permutation con un grado de aleatoriedad, utilizando orden topologico y una funcion de ponderacion
    '''
    graph = get_graph(tasks)
    
    order = topologic_order(graph)
    
    #return random_order(order)
    return pondered_order(order, tasks)

def get_graph(tasks: List[Task]) -> dict[int, List[Task]]:
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

def topologic_order(graph: dict[int, List[Task]]) -> List[List[Task]]:
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
    
    queue = []
    for key in indegree:
        if indegree[key] == 0:
            queue.append(key)
            level[key] = 0
    
    mx = 0
    while queue:
        key = queue.pop(0)
        mx = max(mx, level[key])
        
        for task in graph[key]:
            indegree[task.id] -= 1
            
            if indegree[task.id] == 0:
                queue.append(task.id)
                level[task.id] = level[key] + 1
    
    order = [[] for i in range(mx + 1)]
    
    for key in level:
        order[level[key]].append(key)
    
    return order

def random_order(order: List[List[Task]], tasks) -> List[Task]:
    '''
        Generar una permutacion aleatoria en cada uno de los niveles
    '''
    
    for i in range(len(order)):
        random.shuffle(order[i])
    
    permutation = []
    for level in order:
        permutation += level
    
    return [tasks[x] for x in permutation]

def pondered_order(order: List[List[Task]], tasks) -> List[Task]:
    '''
        Generar una permutacion ponderada en cada uno de los niveles
    '''
    
    for i in range(len(order)):
        order[i].sort(key=lambda x:random.random()*tasks[x].reward/(tasks[x].duration * tasks[x].duration * tasks[x].difficulty * tasks[x].problems_probability * int((tasks[x].deadline-tasks[x].start).total_seconds())), reverse=True)
    
    permutation = []
    for level in order:
        permutation += level
    
    return [tasks[x] for x in permutation]