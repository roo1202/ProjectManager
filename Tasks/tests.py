from PMOntologic.Resource import Resource
from Simulation.WorkerAgent import WorkerPerception
from Tasks.task import Task
from datetime import datetime

from datetime import datetime, timedelta

import random

tasks = [
    Task(id=0, start=datetime.now(), deadline=datetime.now() + timedelta(days=1), priority=1, status="Not Started", duration=10, reward=100, difficulty=random.randint(1, 5), problems_probability=random.random()),
    Task(id=1, start=datetime.now() - timedelta(days=1), deadline=datetime.now() + timedelta(days=2), priority=1, status="Not Started", duration=10, reward=100, difficulty=random.randint(1, 5), problems_probability=random.random()),
    Task(id=2, start=datetime.now() - timedelta(days=2), deadline=datetime.now() + timedelta(days=3), priority=2, status="Not Started", duration=20, reward=200, difficulty=random.randint(1, 5), problems_probability=random.random()),
    Task(id=3, start=datetime.now() - timedelta(days=3), deadline=datetime.now() + timedelta(days=4), priority=3, status="Not Started", duration=30, reward=300, difficulty=random.randint(1, 5), problems_probability=random.random()),
    Task(id=4, start=datetime.now() - timedelta(days=4), deadline=datetime.now() + timedelta(days=5), priority=4, status="Not Started", duration=40, reward=400, difficulty=random.randint(1, 5), problems_probability=random.random()),
    Task(id=5, start=datetime.now() - timedelta(days=5), deadline=datetime.now() + timedelta(days=6), priority=5, status="Not Started", duration=50, reward=500, difficulty=random.randint(1, 5), problems_probability=random.random()),
    Task(id=6, start=datetime.now() - timedelta(days=6), deadline=datetime.now() + timedelta(days=7), priority=6, status="Not Started", duration=60, reward=600, difficulty=random.randint(1, 5), problems_probability=random.random()),
    Task(id=7, start=datetime.now() - timedelta(days=7), deadline=datetime.now() + timedelta(days=8), priority=7, status="Not Started", duration=70, reward=700, difficulty=random.randint(1, 5), problems_probability=random.random()),
    Task(id=8, start=datetime.now() - timedelta(days=8), deadline=datetime.now() + timedelta(days=9), priority=8, status="Not Started", duration=80, reward=800, difficulty=random.randint(1, 5), problems_probability=random.random()),
    Task(id=9, start=datetime.now() - timedelta(days=9), deadline=datetime.now() + timedelta(days=10), priority=8, status="Not Started", duration=80, reward=800, difficulty=random.randint(1, 5), problems_probability=random.random()),
]


tasks[1].dependencies.append(tasks[0])

tasks[2].dependencies.append(tasks[0])
tasks[2].dependencies.append(tasks[1])

tasks[3].dependencies.append(tasks[1])

tasks[4].dependencies.append(tasks[1])

tasks[5].dependencies.append(tasks[2])

tasks[6].dependencies.append(tasks[2])

tasks[7].dependencies.append(tasks[4])
tasks[7].dependencies.append(tasks[5])

tasks[8].dependencies.append(tasks[6])

tasks[9].dependencies.append(tasks[7])
tasks[9].dependencies.append(tasks[8])

def generate_test():
    return tasks

perceptions = [
    WorkerPerception(task_available=False, team_motivation=100),
    WorkerPerception(task_available=True),
    WorkerPerception(task_available=True, task_progress=10),
    WorkerPerception(task_available=True, task_progress=20, problem_detected=True, problem_severity=7)
]



# Instancias de recursos para un proyecto de software

# Desarrolladores
developers = Resource(id="Developers", total=10, cost=50000)
# Testers
testers = Resource(id="Testers", total=5, cost=40000)
# Servidores (para desarrollo y producción)
servers = Resource(id="Servers", total=8, cost=20000)
# Licencias de software (herramientas de desarrollo, testing, etc.)
licenses = Resource(id="Licenses", total=30, cost=10000)
# Equipos de trabajo (laptops, estaciones de trabajo)
workstations = Resource(id="Workstations", total=15, cost=15000)
# Base de datos (servidores de base de datos)
databases = Resource(id="Databases", total=3, cost=25000)
# Almacenamiento en la nube
cloud_storage = Resource(id="CloudStorage", total=50, cost=10000)
# Red (ancho de banda, routers, etc.)
network = Resource(id="Network", total=5, cost=5000)
# Soporte técnico (servicios de soporte y mantenimiento)
technical_support = Resource(id="TechnicalSupport", total=2, cost=30000)
# Herramientas de gestión de proyectos (licencias de herramientas como Jira, Trello)
project_management_tools = Resource(id="ProjectManagementTools", total=20, cost=8000)


# Crear tareas

task1 = Task(id=1, start=0, deadline=20, priority=5, duration=10, reward=80, difficulty=50, problems_probability=0.1)
task1.resources = [Resource(id="Developers", total=1, cost=50000), Resource(id="Workstations", total=8, cost=15000)]  # Requiere 10 developers y 15 workstations

task2 = Task(id=2, start=0, deadline=30, priority=3, duration=20, reward=60, difficulty=40, problems_probability=0.05)
task2.resources = [Resource(id="Testers", total=1, cost=40000),  Resource(id="Servers", total=1, cost=20000)]  # Requiere 5 testers y 8 servers

task3 = Task(id=3, start=0, deadline=15, priority=4, duration=10, reward=90, difficulty=60, problems_probability=0.15)
task3.resources = [Resource(id="Developers", total=2, cost=50000), Resource(id="Databases", total=1, cost=25000), Resource(id="Licenses", total=10, cost=10000)]  # Requiere 10 developers, 3 databases y 30 licenses

task4 = Task(id=4, start=10, deadline=50, priority=4, duration=15, reward=70, difficulty=55, problems_probability=0.2)
task4.resources = [Resource(id="CloudStorage", total=30, cost=10000), Resource(id="TechnicalSupport", total=1, cost=30000)]  # Requiere 50 unidades de cloud storage y 2 de soporte técnico
task4.dependencies = [task1]  # Depende de task1

task5 = Task(id=5, start=20, deadline=50, priority=2, duration=10, reward=50, difficulty=30, problems_probability=0.05)
task5.resources = [Resource(id="ProjectManagementTools", total=15, cost=8000), Resource(id="Licenses", total=10, cost=10000)]  # Requiere 20 unidades de herramientas de gestión y 30 licencias
task5.dependencies = [task2]  # Depende de task2

task6 = Task(id=6, start=10, deadline=70, priority=1, duration=20, reward=40, difficulty=20, problems_probability=0.1)
task6.resources = [Resource(id="Network", total=1, cost=5000), Resource(id="Databases", total=1, cost=25000)]  # Requiere 5 unidades de network y 3 databases
task6.dependencies = [task4]  # Depende de task4

task7 = Task(id=7, start=30, deadline=80, priority=3, duration=40, reward=60, difficulty=50, problems_probability=0.1)
task7.resources = [Resource(id="Developers", total=2, cost=50000),  Resource(id="Servers", total=2, cost=20000), Resource(id="Licenses", total=5, cost=10000)]  # Requiere 10 developers, 8 servers y 30 licencias
task7.dependencies = [task3, task5]  # Depende de task3 y task5

task8 = Task(id=8, start=20, deadline=100, priority=2, duration=10, reward=70, difficulty=40, problems_probability=0.05)
task8.resources = [Resource(id="CloudStorage", total=10, cost=10000), Resource(id="Testers", total=4, cost=40000)]  # Requiere 50 unidades de cloud storage y 5 testers
task8.dependencies = [task6]  # Depende de task6

task9 = Task(id=9, start=40, deadline=110, priority=5, duration=20, reward=90, difficulty=70, problems_probability=0.25)
task9.resources = [Resource(id="Developers", total=1, cost=50000), Resource(id="TechnicalSupport", total=1, cost=30000)]  # Requiere 10 developers y 2 unidades de soporte técnico
task9.dependencies = [task7]  # Depende de task7

task10 = Task(id=10, start=40, deadline=110, priority=4, duration=30, reward=85, difficulty=60, problems_probability=0.2)
task10.resources = [Resource(id="Workstations", total=2, cost=15000),  Resource(id="Servers", total=2, cost=20000), Resource(id="Databases", total=1, cost=25000)]  # Requiere 15 workstations, 8 servers y 3 databases
task10.dependencies = [task8, task9]  # Depende de task8 y task9

