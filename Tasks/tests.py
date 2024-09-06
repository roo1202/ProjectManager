from PMOntologic.Task import Task
from datetime import datetime


tasks = [
    Task(id=0, start=datetime.now(), deadline=datetime.now(), priority=1, status="Not Started", duration=10, reward=100),
    Task(id=1, start=datetime.now(), deadline=datetime.now(), priority=1, status="Not Started", duration=10, reward=100),
    Task(id=2, start=datetime.now(), deadline=datetime.now(), priority=2, status="Not Started", duration=20, reward=200),
    Task(id=3, start=datetime.now(), deadline=datetime.now(), priority=3, status="Not Started", duration=30, reward=300),
    Task(id=4, start=datetime.now(), deadline=datetime.now(), priority=4, status="Not Started", duration=40, reward=400),
    Task(id=5, start=datetime.now(), deadline=datetime.now(), priority=5, status="Not Started", duration=50, reward=500),
    Task(id=6, start=datetime.now(), deadline=datetime.now(), priority=6, status="Not Started", duration=60, reward=600),
    Task(id=7, start=datetime.now(), deadline=datetime.now(), priority=7, status="Not Started", duration=70, reward=700),
    Task(id=8, start=datetime.now(), deadline=datetime.now(), priority=8, status="Not Started", duration=80, reward=800),
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

def generate_test()
    return tasks