import streamlit as st
from LLM import TaskAnalyzer, analyze_string_input
import random
from PMOntologic.PMO import Project
from PMOntologic.Resource import Resource
from Simulation.Simulator import Simulator
from Simulation.Environment import WorkCenter
from Simulation.PMAgent import PMAgent, PMperception
from Simulation.WorkerAgent import WorkerAgent
from Tasks.GeneticAlgorithm.Population import Population
from Tasks.GeneticAlgorithm.Tasks_combination import optimization_function
from Tasks.task import Task

agents = [
    WorkerAgent('trabajador_1', problem_solving=random.randint(10,70), friendship=random.random()),
    WorkerAgent('trabajador_2', problem_solving=random.randint(10,70), friendship=random.random()),
    WorkerAgent('trabajador_3', problem_solving=random.randint(10,70), friendship=random.random()),
    WorkerAgent('trabajador_4', problem_solving=random.randint(10,70), friendship=random.random()),
]

trainer = TaskAnalyzer()

# Título de la aplicación
st.title("Análisis de Tareas en Lenguaje Natural")

# Descripción
st.write("Introduce un texto en lenguaje natural para identificar tareas y recursos usando un modelo de lenguaje.")

# Entrada de texto
user_input = st.text_area("Introduce tu texto aquí:")

# Botón para procesar
if st.button('Procesar'):
    if user_input:
        # Llamar a la función analyze_string_input y obtener los resultados
        task_instances = analyze_string_input(trainer, user_input)
        
        # Mostrar los resultados de las tareas
        st.write("**Tareas identificadas:**")
        if task_instances:
            for task in task_instances:
                st.write(f"- ID: {task.id}, Prioridad: {task.priority}, Duración: {task.duration} unidades, Deadline: {task.deadline}")
                st.write(f"Dependencias: {[t.id for t in task.dependencies]}")
                st.write(f"Recursos: {[r.id for r in task.resources]}")
        else:
            st.write("No se identificaron tareas.")
            
        tasks = task_instances
        resources = {}
        for task in tasks:
            for resource in task.resources:
                if resource.id not in resources.keys():
                    resources[resource.id] = resource.total
                else:
                    resources[resource.id] += resource.total
        resources_list = [Resource(resource, cant*1.2) for resource,cant in resources.items()]
        
        project = Project(objective='number_of_tasks',tasks=tasks, resources=resources_list)
        
        pm = PMAgent(min_motivation_team=20, initial_perception=PMperception(actual_time=0, team_motivation=80), project=project)
        pm.know_workers([(agent.id,agent.problem_solving) for agent in agents])

        simulator = Simulator(WorkCenter)
        
        env = simulator.StartSimulation(1000, agents, pm, project)
        
        summary = generator.generate_summary(env.environment.pm_logs, env.environment.workers_logs)
        st.write("Generated Summary:")
        st.write(summary)
    else:
        st.write("Por favor, introduce un texto para procesar.")
