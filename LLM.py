import os
import time
import google.generativeai as genai
from dotenv import load_dotenv
from typing import List
import concurrent.futures
from concurrent.futures import ThreadPoolExecutor
import numpy as np

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
                For each task, provide the following attributes: 
                id, start, deadline, priority, duration, reward, difficulty, problems_probability. 
                For each resource, provide name, total, cost.
                """,
                "Return only the tasks and resources."
            ]
        ).start_chat(history=[])

    def analyze(self, message):
        print(f"Processing message: {message}")
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

    def parse_response(self, response_text):
        print(f"Response from Gemini: {response_text}")
        tasks = []
        resources = []

        # Aquí debes implementar la lógica para extraer tareas y recursos desde el texto de la respuesta
        # Un ejemplo sencillo podría ser buscar palabras clave y llenar los datos de las tareas y recursos
        if "limpiar el piso" in response_text:
            tasks.append({"id": 1, "name": "Limpiar el piso", "start": "comienzo del día", "deadline": "mediodía"})

        return tasks, resources

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
    posts = [
        {'selftext': 'Al comienzo del día necesitamos limpiar el piso y luego acomodar los muebles.'},
        {'selftext': 'En la tarde tenemos que preparar la comida.'},
        # Otros textos...
    ]

    processed_posts = trainer.process_posts(trainer, posts)

    print("Processed posts results:")
    for result in processed_posts:
        print(result)

