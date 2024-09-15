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
                The resources can be repeated across tasks as they represent what each task needs. Return only the JSON object without any explanations or text formatting like backticks or extra characters. 
                The response must be a valid JSON object.
                """
            ]
        ).start_chat(history=[])

    def analyze(self, message):
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
        # Eliminar posibles símbolos como backticks o texto extra
        response_text = response_text.strip().strip('```json').strip('```')
        
        try:
            # Convertir la respuesta de texto en un diccionario de Python
            data = json.loads(response_text)
            tasks = data.get("tasks", [])
            resources = []
            
            # Extraer los recursos dentro de las tareas, sin preocuparse de duplicados
            for task in tasks:
                if "resources" in task:
                    resources.extend(task["resources"])

            # Eliminar duplicados en la lista de recursos
            unique_resources = {resource['id']: resource for resource in resources}.values()

            return tasks, list(unique_resources)
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
    {'selftext': 'In the morning, we need to set up the development environment. This is a high-priority task that should be completed early in the project, with an expected duration of 2 units of time. After that, we will proceed with designing the database schema. This is a medium-priority task and will take 3 units of time, but it can only start once the development environment has been configured. Following the database design, we will implement the backend API. This task has a high priority, a duration of 4 units of time, and must be done after the database schema is completed. It will require two developers and a server application. Once the backend API is ready, we can move on to developing the frontend. This task is of lower priority and will take 5 units of time. It will depend on the completion of the backend API and will require two front-end developers and one UX designer. After the frontend is implemented, we need to run integration tests to ensure everything works properly. This task is high priority, takes 3 units of time, and depends on the frontend being ready. It will be carried out by one QA engineer using a dedicated testing environment. Once integration tests are passed, the system will be deployed in the staging environment. This deployment is a high-priority task that will take 2 units of time. It will depend on the successful completion of the integration tests and will be handled by a DevOps engineer using the staging server. Before the final deployment, a code review will be performed. This is a medium-priority task with a duration of 1 unit of time. It can only start after the staging deployment has been completed. Finally, after the code review, the system will be deployed to production. This task is high priority, will take 1 unit of time, and depends on the code review. The deployment will be handled by the DevOps engineer using the production server.'},
    ]

    processed_posts = trainer.process_posts(trainer, tasks_example)

    print("Processed posts results:")
    for i, result in enumerate(processed_posts, start=1):
        tasks, resources = result
        print(f"\nPost {i} results:")
        print(f"Tasks: {tasks}")
        print(f"Resources: {resources}")