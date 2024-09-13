import numpy as np
import random
import warnings
import random
import copy
import pandas as pd
import time
from datetime import datetime
from Tasks.GeneticAlgorithm.Permutations_generator_heuristics import generate_permutation
from Tasks.task import Task
import warnings
warnings.filterwarnings('ignore')

class Tasks_combination:
    """
    Esta clase representa una combinacion de tareas, con unas características iniciales definidas
    por una combinación de tareas aleatorias en un array que representa las unidades de tiempo definidas. El rango de posibles
    valores para cada variable puede estar acotado por la cantidad de tareas posibles a hacer en esa unidad de tiempo.
    
    Parameters
    ----------
    tasks : `list`
        lista de tareas a combinar

    verbose : `bool`, optional
        mostrar información del Tasks_combination creado. (default ``False``)

    Attributes
    ----------
    n_variables : `int`
        número de variables que definen al Tasks_combination.

    variable_values : `numpy.ndarray`
        array con el valor de cada una de las variables o tareas asignadas a cada etapa de tiempo.

    fitness : `float`
        valor de fitness del Tasks_combination.

    function_value : `float`
        valor de la función objetivo para el Tasks_combination.

    Raises
    ------
    raise Exception
        si `limites_inf` es distinto de None y su longitud no coincide con
        `n_variables`.

    raise Exception
        si `limites_sup` es distinto de None y su longitud no coincide con
        `n_variables`.

    
    """

    def tasks_combinator(self, tasks) -> list[Task]:
        tasks_copy = [task for task in tasks]
        random.shuffle(tasks_copy)

        # while len(tasks_copy) > self.n_variables:
        #     i, j = random.sample(range(len(tasks_copy)), 2)
            
        #     if self.limites_sup[i] >= tasks_copy[i].tasks_count() :
        #         continue

        #     if len(tasks_copy[i].dependencies) > 0:
        #         try:
        #             # Intentamos combinar la tarea actual con la primera dependencia
        #             tasks_copy[i] = tasks_copy[i].dependencies[0][0].combine(tasks_copy[i], tasks_copy[tasks_copy.index((tasks_copy[i].dependences[0][1]))])
                    
        #             # Actualizamos la segunda tarea con la última tarea
        #             tasks_copy[tasks_copy.index((tasks_copy[i].dependencies[0][1]))] = tasks_copy[-1]
        #         except:
                    
        #             tasks_copy[i] = Dependence.combine(tasks_copy[i], tasks_copy[j])
        #             tasks_copy[j] = tasks_copy[-1]

        #     tasks_copy.pop()

        return tasks_copy

    
    def __init__(self, n_variables, tasks={}, verbose=False):

        # Número de variables del Tasks_combination
        self.n_variables = n_variables
        # Valor de las variables del Tasks_combination
        self.variable_values = generate_permutation(tasks)
        # Fitness del Tasks_combination
        self.fitness = None
        # Valor de la función objetivo
        self.function_value = None
        
        
        # INFORMACIÓN DEL PROCESO (VERBOSE)
        # ----------------------------------------------------------------------
        if verbose:
            print("Nuevo Tasks_combination creado")
            print("----------------------")
            print("Valor variables: " + str(self.variable_values))
            print("Valor función objetivo: " + str(self.function_value))
            print("Fitness: " + str(self.fitness))
            print("")

    def __repr__(self):
        """
        Información que se muestra cuando se imprime un objeto Tasks_combination.

        """

        texto = "Tasks_combination" \
                + "\n" \
                + "---------" \
                + "\n" \
                + "Valor variables: " + str(self.variable_values) \
                + "\n" \
                + "Valor función objetivo: " + str(self.function_value) \
                + "\n" \
                + "Fitness: " + str(self.fitness) \
                + "\n" 

        return(texto)

    def calculate_fitness(self, objective_function, optimization, verbose = False):
        """
        Este método obtiene el fitness del Tasks_combination calculando el valor que toma
        la función objetivo con el valor de sus variables.
        
        Parameters
        ----------
        funcion_objetivo : `function`
            función que se quiere optimizar.

        optimizacion : {'maximize', 'minimize'}
            ver notas para más información.

        verbose : `bool`, optional
            mostrar información del proceso por pantalla. (default ``False``)
          
        Raises
        ------
        raise Exception
            si el argumento `optimizacion` es distinto de 'maximize' o
            'minimize'

        Notes
        -----
        Cada Tasks_combination de la población debe ser evaluado para cuantificar su
        bondad como solución al problema, a esta cuantificación se le llama
        fitness.
       
        Dependiendo de si se trata de un problema de maximización o minimización,
        la relación del fitness con la función objetivo :`f` puede ser:

        - Maximización: el Tasks_combination tiene mayor fitness cuanto mayor es el valor
         de la función objetivo :`f(Tasks_combination)`.

        - Minimización: el Tasks_combination tiene mayor fitness cuanto menor es el valor
         de la función objetivo :`f(Tasks_combination)`, o lo que es lo mismo,
         cuanto mayor es el valor de la función objetivo, menor el fitness.
         El algoritmo genético selecciona los Tasks_combinations de mayor fitness, por 
         lo que, para problemas de minimización, el fitness puede calcularse como
         :-f(Tasks_combination) o también : frac{1}{1+f(Tasks_combination)}.


        """

        # COMPROBACIONES INICIALES: EXCEPTIONS Y WARNINGS
        # ----------------------------------------------------------------------
        if not optimization in ["maximize", "minimize"]:
            raise Exception(
                "El argumento optimizacion debe ser: 'maximize' o 'minimize'"
                )

        # EVALUACIÓN DE LA FUNCIÓN OBJETIVO CON LAS VARIABLES DEL Tasks_combination Y
        # CÁLCULO DEL FITNESS
        # ----------------------------------------------------------------------
        self.function_value = objective_function(self.variable_values)
        if optimization == "maximize":
            self.fitness = self.function_value
        elif optimization == "minimize":
            self.fitness = -self.function_value

        # INFORMACIÓN DEL PROCESO (VERBOSE)
        # ----------------------------------------------------------------------
        if verbose:
            print("El Tasks_combination ha sido evaluado")
            print("-----------------------------")
            print("Valor función objetivo: " + str(self.function_value))
            print("Fitness: " + str(self.fitness))
            print("")

    def mutate(self, mutation_prob=0.01, distribution="aleatoria", media_distribucion=1,
              sd_distribucion=1, min_distribution=-1, max_distribution=1,
              verbose=False):
        """
        Este método somete al Tasks_combination a un proceso de mutación en el que, cada
        una de sus posiciones, puede verse modificada con una probabilidad 
        `prob_mut`. Tras mutar, los atributos `function_value` y `fitness` se
        reinician.
        
        Parameters
        ----------
        prob_mut : `float`, optional
            probabilidad que tiene cada posición del Tasks_combination de mutar.
            (default 0.01)

        distribucion : {"normal", "uniforme", "aleatoria"}, optional
            distribución de la que obtener el factor de mutación.
            (default "uniforme")

        media_distribucion : `float`, optional
            media de la distribución si se selecciona `distribucion = "normal"`
            (default 1)

        sd_distribucion : `float`, optional
            desviación estándar de la distribución si se selecciona
            `distribucion = "normal"`. (default 1)

        min_distribucion : `float`, optional
            mínimo de la distribución si se selecciona 
            `distribucion = "uniforme"`. (default -1)

        max_distribucion : `float`, optional
            máximo de la distribución si se selecciona 
            `distribucion = "uniforme"`. (default +1)
        
        verbose : `bool`, optional
            mostrar información del proceso por pantalla. (default ``False``)

        Raises
        ------
        raise Exception
            si el argumento `distribucion` es distinto de 'normal', 'uniforme' o
            'aleatoria'.


        Notes
        -----
        El proceso de mutación añade diversidad al proceso y evita que el
        algoritmo caiga en mínimos locales por que todos los Tasks_combinations sean
        demasiado parecidos de una generación a otra. Existen diferentes
        estrategias para controlar la magnitud del cambio que puede provocar una
        mutación.

        - Distribución uniforme: la mutación de la posición i se consigue
        sumándole al valor de i un valor extraído de una distribución uniforme,
        por ejemplo una entre [-1,+1].

        - Distribución normal: la mutación de la posición i se consigue sumándole
         al valor de i un valor extraído de una distribución normal, comúnmente
         centrada en 0 y con una determinada desviación estándar. Cuanto mayor
         la desviación estándar, con mayor probabilidad la mutación introducirá
         cambios grandes.

        - Aleatorio: la mutación de la posición i se consigue reemplazando el
        valor de i por nuevo valor aleatorio dentro del rango permitido para esa
        variable. Esta estrategia suele conllevar mayores variaciones que las dos
        anteriores.

        Hay que tener en cuenta que, debido a las mutaciones, un valor que
        inicialmente estaba dentro del rango permitido puede salirse de él.
        Una forma de evitarlo es: si el valor tras la mutación excede alguno de
        los límites acotados, se sobrescribe con el valor del límite. Es decir,
        se permite que los valores se alejen como máximo hasta el límite impuesto.

        """

        # COMPROBACIONES INICIALES: EXCEPTIONS Y WARNINGS
        # ----------------------------------------------------------------------
        if not distribution in ["normal", "uniforme", "aleatoria"]:
            raise Exception(
                "El argumento distribucion debe ser: 'normal', 'uniforme' o " \
                + "'aleatoria'"
                )

        # SELECCIÓN PROBABILISTA DE POSICIONES (VARIABLES) QUE MUTAN
        #-----------------------------------------------------------------------
        posiciones_mutadas = np.random.uniform(
                                low=0,
                                high=1,
                                size=self.n_variables
                             )
        posiciones_mutadas = posiciones_mutadas < mutation_prob

        # MODIFICACIÓN DE LOS VALORES DE LAS VARIABLES SELECCIONADAS
        #-----------------------------------------------------------------------
        # Si la distribución seleccionada es "uniforme" o "normal", se extrae un
        # valor aleatorio de la distribución elegida que se suma para modificar
        # la/las posiciones mutadas.

        if distribution in ["normal", "uniforme"]:
            if distribution == "normal":
                factor_mut = np.random.normal(
                                loc   = media_distribucion,
                                scale = sd_distribucion,
                                size  = np.sum(posiciones_mutadas)
                             )
            if distribution == "uniforme":
                factor_mut = np.random.uniform(
                                low  = min_distribution,
                                high = max_distribution,
                                size = np.sum(posiciones_mutadas)
                             )
            self.variable_values[posiciones_mutadas] = \
                self.variable_values[posiciones_mutadas] + factor_mut


        # Si la distribución seleccionada es "aleatoria", se sobreescribe el
        # valor de la variable con un nuevo valor aleatorio dentro de los 
        # límites establecidos.
        if distribution == "aleatoria":
            indices = []
            for i in np.flatnonzero(posiciones_mutadas):
                indices.append(i)
            random.shuffle(indices)
            valor_copy = copy.deepcopy(self.variable_values)
            count = 0
            for i in np.flatnonzero(posiciones_mutadas):
                self.variable_values[i] = valor_copy[indices[count]]
                count += 1


        # REINICIO DEL VALOR Y DEL FITNESS
        #-----------------------------------------------------------------------
        # Dado que el Tasks_combination ha mutado, el valor de su fitness y de la
        # función objetivo ya no son validos.
        self.fitness = None
        self.function_value = None

        # INFORMACIÓN DEL PROCESO (VERBOSE)
        # ----------------------------------------------------------------------
        if verbose:
            print("El Tasks_combination ha sido mutado")
            print("---------------------------")
            print("Total mutaciones: " + str(np.sum(posiciones_mutadas)))
            print("Valor variables: " + str(self.variable_values))
            print("")



# def optimization_function(permutacion):
#     penalizacion_total = 0
#     reward_total = 0
#     tiempo_actual = 0
#     tareas_completadas = set()
    
#     for _, task in enumerate(permutacion):
#         # Verificar si las dependencias de la tarea están completas
#         for tarea_dependiente in task.dependencies:
#             if tarea_dependiente not in tareas_completadas:
#                 # Penalización alta si se intenta realizar una tarea antes de completar sus dependencias
#                 penalizacion_total += (4 - task.priority) * 100  # Penalización arbitraria alta

#         # Sumar la duración de la tarea al tiempo actual
#         tiempo_actual += task.duration
        
#         # Si la tarea finaliza después de su deadline
#         if tiempo_actual > task.deadline:
#             # Calcular la penalización
#             penalizacion = (tiempo_actual - task.deadline) * (4 -task.priority)
#             penalizacion_total += penalizacion
#         else:
#             # Agregar reward si la tarea se completa antes o a tiempo
#             reward_total += task.reward
        
#         # Marcar la tarea como completada
#         tareas_completadas.add(task) 

#     # Calcular la puntuación final
#     puntuacion_final = reward_total - penalizacion_total 
#     return puntuacion_final

def optimization_function(permutacion):
    penalizacion_total = 0
    reward_total = 0
    tiempo_actual = 0
    tareas_completadas = set()
    dificultad_anterior = None

    for i, task in enumerate(permutacion):
        # Verificar si las dependencias de la tarea están completas
        for tarea_dependiente in task.dependencies:
            if tarea_dependiente not in tareas_completadas:
                # Penalización alta si se intenta realizar una tarea antes de completar sus dependencias
                penalizacion_total += (5 - task.priority) * 100  # Penalización basada en la prioridad
                break  # Salimos, ya que no se puede completar la tarea debido a la dependencia
        
        # Sumar la duración de la tarea al tiempo actual
        tiempo_actual += task.duration
        
        # Si la tarea finaliza después de su deadline
        if tiempo_actual > task.deadline:
            # Penalización proporcional al tiempo excedido y la prioridad
            penalizacion_total += (tiempo_actual - task.deadline) * (5 - task.priority)

        else:
            # Bonificación si la tarea se completa antes o justo a tiempo
            reward_total += task.reward
        
        # Evaluar la variedad de dificultad
        if dificultad_anterior is not None:
            # Bonificación si la dificultad es diferente
            if abs(task.difficulty - dificultad_anterior) > 10:  # Diferencia significativa
                reward_total += 5  # Pequeña bonificación por variedad de dificultad
            else:
                penalizacion_total += 2  # Penalización si hay muchas dificultades iguales
        
        # Actualizar la dificultad anterior
        dificultad_anterior = task.difficulty
        
        # Marcar la tarea como completada
        tareas_completadas.add(task)
    
    # Calcular la puntuación final
    puntuacion_final = reward_total - penalizacion_total
    return puntuacion_final


    