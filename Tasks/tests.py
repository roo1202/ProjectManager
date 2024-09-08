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