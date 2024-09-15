import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import numpy as np
import json

class TaskAnalyzer:
    def __init__(self, config_file='.env'):
        load_dotenv(config_file)
        self.api_key = os.environ['GENAI_API_KEY']
        genai.configure(api_key=self.api_key)

        self.chat = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction=[
                """
                You are a project manager assistant. Analyze the following text and identify all the tasks and resources.
                Return the tasks and resources in valid JSON format only, without any additional symbols or formatting. 
                For each task, provide the following attributes in this exact structure: 
                {
                "tasks": [
                    {
                    "id": int,
                    "start": int,
                    "deadline": int,
                    "priority": int,
                    "duration": int,
                    "reward": int,
                    "difficulty": int,
                    "problems_probability": float,
                    "dependencies": [int],  # list of task ids this task depends on
                    "resources": [
                        {
                        "id": int,
                        "total": int,
                        }
                    ]
                    }
                ]
                }
                Return only the JSON object without any explanations or text formatting like backticks or extra characters. 
                The response must be a valid JSON object.
                """
            ]
        ).start_chat(history=[])


    def analyze(self, message):
        #print(f"Processing message: {message}")
        response = self.get_gemini_score(message)
        if response:
            tasks, resources = self.parse_response(response.text.strip())
            return tasks, resources
        return [], []  # Devuelve listas vacías si no hay respuesta

    def get_gemini_score(self, message):
        try:
            response = self.chat.send_message(f'Identify the tasks and resources in the following text:\n\n{message}')
            return response
        except genai.types.BlockedPromptException as e:
            print(f"The prompt was blocked: {e}")
            return None
        except Exception as e:  # Captura cualquier otra excepción inesperada
            print(f"An error occurred: {e}")
            return None


    def parse_response(self, response_text):
        #print(f"Response from Gemini: {response_text}")
        
        # Eliminar posibles símbolos como backticks o texto extra
        response_text = response_text.strip().strip('```json').strip('```')
        
        try:
            # Convertir la respuesta de texto en un diccionario de Python
            data = json.loads(response_text)
            tasks = data.get("tasks", [])
            resources = []
            
            # Extraer los recursos dentro de las tareas, si es necesario
            for task in tasks:
                if "resources" in task:
                    resources.extend(task["resources"])
            
            return tasks, resources
        except json.JSONDecodeError as e:
            print(f"Error decoding JSON: {e}")
            return [], []


    def process_post(self, post):
        message = post.get('selftext', '')
        if not message:
            print("No message found in post.")
            return None
        tasks, resources = self.analyze(message)
        return tasks, resources

    @staticmethod
    def process_posts(trainer, posts_subset):
        results = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = [executor.submit(trainer.process_post, post) for post in posts_subset]
            for future in concurrent.futures.as_completed(futures):
                result = future.result()
                if result:
                    results.append(result)
        return results

if __name__ == "__main__":
    trainer = TaskAnalyzer()

    # Procesar un conjunto de posts para extraer tareas y recursos
    tasks_example = [
    {'selftext': 'Task 1 involves setting up the user authentication module. It is a high-priority task and should be completed early, ideally between task positions 0 and 2 in the project timeline. Duration is 2 units of time.'},
    
    {'selftext': 'Task 2 is to design the database schema. This task has medium priority and can be done between task positions 2 and 5. It has a duration of 3 units and will depend on Task 1 being completed first.'},
    
    {'selftext': 'Task 3 is to implement the frontend. This task is dependent on Task 2 (database schema) and should start once the database is ready. It has a low priority and a duration of 4 units. The task can be done between positions 5 and 9.'},
    
    {'selftext': 'Task 4 is to set up the continuous integration pipeline. This is a short but critical task, with high priority. It should be done between task positions 9 and 10, and it only takes 1 unit of time.'},
    
    {'selftext': 'Task 5 involves the final deployment of the project. It is the last task and will depend on all previous tasks being completed. It can be done between task positions 10 and 12 and has a duration of 2 units.'},
    
    {'selftext': 'Task 6 is to review the code. This task has low priority, but it must be completed between task positions 8 and 11. The duration of the task is 2 units.'}
]



    processed_posts = trainer.process_posts(trainer, tasks_example)

    print("Processed posts results:")
    for i, result in enumerate(processed_posts, start=1):
        tasks, resources = result
        print(f"\nPost {i} results:")
        print(f"Tasks: {tasks}")
        print(f"Resources: {resources}")
