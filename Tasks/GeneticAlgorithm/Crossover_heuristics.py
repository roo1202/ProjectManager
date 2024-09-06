import random
import sys
from Tasks.GeneticAlgorithm.Tasks_combination import Tasks_combination
from Tasks.task import Task

def crossing_by_cut_off_point(parent1, parent2 , mode='aleatorio'):
    # Validación del modo
    if mode not in ['aleatorio', 'inteligente']:
        raise ValueError("El modo debe ser 'aleatorio' o 'inteligente'.")
    if len(parent1) != len(parent2) :
        raise ValueError("Los padres deben tener la misma cantidad de genes")

    # Definición del punto de corte
    if mode == 'aleatorio':
        cut_point = random.randint(1, len(parent1) - 1)
    else:  # modo inteligente
        evaluation1 = find_acumulative_imposible_tasks(parent1)
        evaluation2 = find_acumulative_imposible_tasks(parent2)
        total = evaluation2[len(parent2)-1]
        min = sys.maxsize
        cut_point = len(parent1)//2
        for i in range(0,len(parent1)-1):
            if evaluation1[i] + (total - evaluation2[i]) < min :
                min = evaluation1[i] + (total - evaluation2[i])
                cut_point = i
        

    # Cruce de las permutaciones
    child = parent1[:cut_point] + [task for task in parent2 if task not in parent1[:cut_point]]
  
    return child

def find_acumulative_imposible_tasks(permutation):
    # Búsqueda del punto de corte basado en el subarreglo con menos tareas imposibles
    imposible_tasks = [None] * len(permutation)
    completed_tasks = set()
    actual_time = 0

    if len(permutation[0].dependencies) > 0 : imposible_tasks[0] = 1
    else : imposible_tasks[0] = 0
    
    for index in range(1,len(permutation)):
        # Verificar si todas las dependencias de la tarea están completas
        imposible = False
        for tarea_dependiente in permutation[index].dependencies:
            if tarea_dependiente not in completed_tasks:
                imposible = True
                break

        # Sumar la duración de la tarea al tiempo actual
        actual_time += permutation[index].duration
        
        # Si la tarea finaliza después de su deadline
        if actual_time > permutation[index].deadline:
            imposible = True
        
        # Marcar la tarea como completada
        completed_tasks.add(permutation[index])

        if(imposible) : imposible_tasks[index] = imposible_tasks[index-1] + 1
        else : imposible_tasks[index] = imposible_tasks[index-1]

    return imposible_tasks