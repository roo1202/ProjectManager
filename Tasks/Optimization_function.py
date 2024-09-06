import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl
import matplotlib.pyplot as plt

def create_fuzzy_system(max_num_tasks, max_total_time, max_total_resources, max_total_rewards, max_high_priority_tasks):

    # Definir el rango de valores para cada variable usando el valor máximo proporcionado
    num_tasks = ctrl.Antecedent(np.arange(0, max_num_tasks + 1, 1), 'num_tasks')
    total_time = ctrl.Antecedent(np.arange(0, max_total_time + 1, 1), 'total_time')
    total_resources = ctrl.Antecedent(np.arange(0, max_total_resources + 1, 1), 'total_resources')
    total_rewards = ctrl.Antecedent(np.arange(0, max_total_rewards + 1, 1), 'total_rewards')
    high_priority_tasks = ctrl.Antecedent(np.arange(0, max_high_priority_tasks + 1, 1), 'high_priority_tasks')

    # Definir la variable de salida que representa la calidad de la permutación
    quality = ctrl.Consequent(np.arange(0, 101, 1), 'quality')

    # Definir funciones de membresía triangulares para las variables de entrada
    num_tasks['low'] = fuzz.trimf(num_tasks.universe, [0, 0, max_num_tasks * 0.33])
    num_tasks['medium'] = fuzz.trimf(num_tasks.universe, [0, max_num_tasks * 0.5, max_num_tasks])
    num_tasks['high'] = fuzz.trimf(num_tasks.universe, [max_num_tasks * 0.33, max_num_tasks, max_num_tasks])

    total_time['short'] = fuzz.trimf(total_time.universe, [0, 0, max_total_time * 0.33])
    total_time['medium'] = fuzz.trimf(total_time.universe, [0, max_total_time * 0.5, max_total_time])
    total_time['long'] = fuzz.trimf(total_time.universe, [max_total_time * 0.33, max_total_time, max_total_time])

    total_resources['low'] = fuzz.trimf(total_resources.universe, [0, 0, max_total_resources * 0.33])
    total_resources['medium'] = fuzz.trimf(total_resources.universe, [0, max_total_resources * 0.5, max_total_resources])
    total_resources['high'] = fuzz.trimf(total_resources.universe, [max_total_resources * 0.33, max_total_resources, max_total_resources])

    total_rewards['low'] = fuzz.trimf(total_rewards.universe, [0, 0, max_total_rewards * 0.33])
    total_rewards['medium'] = fuzz.trimf(total_rewards.universe, [0, max_total_rewards * 0.5, max_total_rewards])
    total_rewards['high'] = fuzz.trimf(total_rewards.universe, [max_total_rewards * 0.33, max_total_rewards, max_total_rewards])

    high_priority_tasks['low'] = fuzz.trimf(high_priority_tasks.universe, [0, 0, max_high_priority_tasks * 0.33])
    high_priority_tasks['medium'] = fuzz.trimf(high_priority_tasks.universe, [0, max_high_priority_tasks * 0.5, max_high_priority_tasks])
    high_priority_tasks['high'] = fuzz.trimf(high_priority_tasks.universe, [max_high_priority_tasks * 0.33, max_high_priority_tasks, max_high_priority_tasks])

    # Definir funciones de membresía automáticas para la variable de salida
    quality.automf(7)

    # Definir las reglas difusas
    rules = [
        ctrl.Rule(num_tasks['high'] & total_time['short'] & total_resources['low'] & total_rewards['high'] & high_priority_tasks['high'], quality['excellent']),
        ctrl.Rule(num_tasks['high'] & total_time['medium'] & total_resources['low'] & total_rewards['high'] & high_priority_tasks['high'], quality['good']),
        ctrl.Rule(num_tasks['medium'] & total_time['medium'] & total_resources['medium'] & total_rewards['medium'] & high_priority_tasks['medium'], quality['average']),
        ctrl.Rule(num_tasks['low'] & total_time['long'] & total_resources['high'] & total_rewards['low'] & high_priority_tasks['low'], quality['poor']),
        ctrl.Rule(num_tasks['medium'] & total_time['short'] & total_resources['medium'] & total_rewards['high'] & high_priority_tasks['high'], quality['decent']),
        ctrl.Rule(num_tasks['high'] & total_time['medium'] & total_resources['low'] & total_rewards['medium'] & high_priority_tasks['medium'], quality['good']),
        ctrl.Rule(num_tasks['low'] & total_time['short'] & total_resources['low'] & total_rewards['low'] & high_priority_tasks['medium'], quality['poor']),
        ctrl.Rule(num_tasks['medium'] & total_time['long'] & total_resources['high'] & total_rewards['medium'] & high_priority_tasks['low'], quality['average']),
        ctrl.Rule(num_tasks['high'] & total_time['medium'] & total_resources['medium'] & total_rewards['high'] & high_priority_tasks['medium'], quality['good']),
        ctrl.Rule(num_tasks['low'] & total_time['long'] & total_resources['high'] & total_rewards['high'] & high_priority_tasks['low'], quality['dismal']),
        ctrl.Rule(num_tasks['medium'] & total_time['short'] & total_resources['low'] & total_rewards['low'] & high_priority_tasks['high'], quality['mediocre']),
        ctrl.Rule(num_tasks['high'] & total_time['long'] & total_resources['low'] & total_rewards['medium'] & high_priority_tasks['medium'], quality['average']),
        ctrl.Rule(num_tasks['low'] & total_time['short'] & total_resources['high'] & total_rewards['medium'] & high_priority_tasks['low'], quality['decent']),
        ctrl.Rule(num_tasks['medium'] & total_time['medium'] & total_resources['medium'] & total_rewards['low'] & high_priority_tasks['high'], quality['mediocre']),
    ]

    # Crear el sistema de control difuso
    quality_ctrl = ctrl.ControlSystem(rules)

    # Crear la simulación del sistema de control
    quality_eval = ctrl.ControlSystemSimulation(quality_ctrl)

    return quality_eval

def evaluate_permutation(quality_eval, num_tasks_val, total_time_val, total_resources_val, total_rewards_val, high_priority_tasks_val):
    
    # Proveer las entradas al sistema de control difuso seleccionado
    quality_eval.input['num_tasks'] = num_tasks_val
    quality_eval.input['total_time'] = total_time_val
    quality_eval.input['total_resources'] = total_resources_val
    quality_eval.input['total_rewards'] = total_rewards_val
    quality_eval.input['high_priority_tasks'] = high_priority_tasks_val

    # Computar la salida (defuzzificación)
    try:
        quality_eval.compute()
    except Exception as e:
        print(f"Error computing the system: {e}")
        return None

    return quality_eval.output['quality']

# Ejemplo de uso:
max_values = {
    'max_num_tasks': 100,
    'max_total_time': 500,
    'max_total_resources': 50,
    'max_total_rewards': 10000,
    'max_high_priority_tasks': 80,
}

quality_eval = create_fuzzy_system(**max_values)

quality_score = evaluate_permutation(quality_eval, 100, 500, 10, 10000, 79)
print(f"Quality Score: {quality_score}")
