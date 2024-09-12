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
                    "name": string,
                    "start": string (in YYYY-MM-DD format),
                    "deadline": string (in YYYY-MM-DD format),
                    "priority": int,
                    "duration": int,
                    "reward": int,
                    "difficulty": int,
                    "problems_probability": float,
                    "dependencies": [int],  # list of task ids this task depends on
                    "resources": [
                        {
                        "name": string,
                        "total": int,
                        "cost": float
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
        {'selftext': 'In the morning, we need to implement the user authentication module for the web application. This task involves creating login and registration endpoints, integrating with OAuth2 for third-party logins, and ensuring proper password hashing and storage in the database.'},
        
        {'selftext': 'By the afternoon, we need to refactor the existing payment processing code. This will include optimizing the checkout flow, improving error handling, and ensuring compliance with the latest security standards like PCI-DSS. Make sure to update the unit tests to reflect the changes.'},
        
        {'selftext': 'Later in the day, we should review the pull requests from the development team for the new feature branch. This task includes checking for code quality, ensuring the coding standards are followed, and testing the feature manually to verify that it works as expected before merging into the main branch.'},
        
        {'selftext': 'Before the end of the day, we need to set up the continuous integration (CI) pipeline to automate the deployment process. This task involves configuring the build server, integrating with Docker for containerization, and setting up automated tests to run with each deployment.'},
        
        {'selftext': 'We need to perform a comprehensive code review of the new REST API endpoints that were added this week. This task includes ensuring that all API endpoints follow RESTful principles, are well-documented, and handle error cases properly. Any performance bottlenecks should also be identified and optimized.'},
        
        {'selftext': 'During the sprint planning meeting tomorrow, we need to define the user stories for the upcoming features in the mobile app. Each story should include clear acceptance criteria and an estimated time for completion. Ensure that dependencies between stories are identified to prevent blockers during development.'},
        
        {'selftext': 'By the end of the week, we should deploy the latest version of the application to the staging environment. This task includes running final integration tests, performing a smoke test to verify the core functionality, and preparing a deployment plan for the production environment.'},
        
        {'selftext': 'We need to implement the caching mechanism for the data-heavy endpoints in the API. This task involves integrating Redis as the caching solution and ensuring that frequently accessed data is stored in memory to improve response times.'},
        
        {'selftext': 'On Friday, we need to hold a retrospective meeting to discuss the last sprint’s successes and areas for improvement. Each team member should share their feedback on the sprint process, and we should identify action items to make the next sprint more efficient.'},
        
        {'selftext': 'Before the release on Monday, we need to run a performance test on the application to ensure it can handle the expected traffic load. This task involves using tools like JMeter to simulate concurrent users, analyzing the response times, and identifying any potential bottlenecks.'},
        
        {'selftext': 'We need to design the database schema for the new project. This includes defining all the necessary tables, relationships, and indexes. This task is critical as it will impact all future development steps.'},
        
        {'selftext': 'Once the database schema is designed, we can proceed with setting up the backend API. This includes creating all the necessary endpoints for CRUD operations and ensuring proper authentication and authorization.'},
        
        {'selftext': 'Before we can start working on the frontend, we need to finalize the wireframes and UI designs. These wireframes will serve as a blueprint for the development of the user interface.'},
        
        {'selftext': 'After the wireframes are approved, we can begin developing the frontend. This task involves implementing the user interface, ensuring responsiveness, and integrating with the backend API.'},
        
        {'selftext': 'Once the backend API is functional, we need to implement integration tests to ensure all API endpoints are working as expected. These tests will cover various scenarios, including edge cases.'},
        
        {'selftext': 'Before deployment, we must perform user acceptance testing (UAT). This step ensures that the system meets all business requirements and works correctly for the end-users.'},
        
        {'selftext': 'After all the development and testing phases are completed, we can proceed with the deployment to the staging environment. This involves configuring the servers and deploying the application to test it in a live-like environment.'},
        
        {'selftext': 'After successful deployment to the staging environment, we need to perform a load test to ensure that the system can handle the expected number of users. Any performance bottlenecks should be identified and resolved.'},
        
        {'selftext': 'Finally, we will deploy the system to production. This task involves setting up the production environment and ensuring that all systems are ready for the official release. We also need to monitor the application for any issues post-release.'}

    ]


    processed_posts = trainer.process_posts(trainer, tasks_example)

    print("Processed posts results:")
    for i, result in enumerate(processed_posts, start=1):
        tasks, resources = result
        print(f"\nPost {i} results:")
        print(f"Tasks: {tasks}")
        print(f"Resources: {resources}")
