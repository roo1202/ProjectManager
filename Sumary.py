import os
import google.generativeai as genai
from dotenv import load_dotenv
import json

class SummaryGenerator:
    def __init__(self, config_file='.env'):
        load_dotenv(config_file)
        self.api_key = os.environ['GENAI_API_KEY']
        genai.configure(api_key=self.api_key)

        self.chat = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            system_instruction="""
            You are a project assistant. Based on the provided project manager (PM) and worker data, generate a concise and structured summary. 
            The summary should include information on:
            1. Task assignment and completion.
            2. Worker performance and trust levels.
            3. Problems reported and cooperation levels.
            4. Worker activity (who is working and who is resting).
            Return the summary as a structured text.
            """
        ).start_chat(history=[])

    def generate_summary(self, pm_data, workers_data):
        pm_data_json = json.dumps(pm_data)
        workers_data_json = json.dumps(workers_data)

        # Generar el mensaje para el modelo LLM
        message = f"""
        PM data: {pm_data_json}
        Worker data: {workers_data_json}
        """
        response = self.chat.send_message(message)
        return response.text.strip()

if __name__ == "__main__":
    generator = SummaryGenerator()

    # Datos completos del Project Manager (PM)
    pm_data = [
        {"time": 0, "pm_assignments": 27, "completed_tasks": 0, "fail_tasks": 0, "problems_count": 0, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 10, "pm_assignments": 0, "completed_tasks": 3, "fail_tasks": 0, "problems_count": 0, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 20, "pm_assignments": 0, "completed_tasks": 8, "fail_tasks": 0, "problems_count": 0, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 30, "pm_assignments": 0, "completed_tasks": 12, "fail_tasks": 0, "problems_count": 0, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 40, "pm_assignments": 0, "completed_tasks": 13, "fail_tasks": 0, "problems_count": 0, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 50, "pm_assignments": 0, "completed_tasks": 20, "fail_tasks": 0, "problems_count": 1, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 60, "pm_assignments": 0, "completed_tasks": 23, "fail_tasks": 0, "problems_count": 1, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 70, "pm_assignments": 9, "completed_tasks": 25, "fail_tasks": 0, "problems_count": 2, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 80, "pm_assignments": 3, "completed_tasks": 26, "fail_tasks": 0, "problems_count": 2, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 90, "pm_assignments": 9, "completed_tasks": 28, "fail_tasks": 0, "problems_count": 3, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 100, "pm_assignments": 0, "completed_tasks": 30, "fail_tasks": 0, "problems_count": 3, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 110, "pm_assignments": 6, "completed_tasks": 33, "fail_tasks": 0, "problems_count": 3, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 120, "pm_assignments": 0, "completed_tasks": 36, "fail_tasks": 0, "problems_count": 4, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 130, "pm_assignments": 0, "completed_tasks": 40, "fail_tasks": 0, "problems_count": 4, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 140, "pm_assignments": 0, "completed_tasks": 42, "fail_tasks": 0, "problems_count": 5, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 150, "pm_assignments": 3, "completed_tasks": 46, "fail_tasks": 0, "problems_count": 7, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 160, "pm_assignments": 6, "completed_tasks": 48, "fail_tasks": 0, "problems_count": 7, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 170, "pm_assignments": 0, "completed_tasks": 51, "fail_tasks": 0, "problems_count": 8, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 180, "pm_assignments": 6, "completed_tasks": 54, "fail_tasks": 0, "problems_count": 9, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 190, "pm_assignments": 3, "completed_tasks": 54, "fail_tasks": 0, "problems_count": 10, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 50), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 200, "pm_assignments": 3, "completed_tasks": 56, "fail_tasks": 0, "problems_count": 15, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 52.5), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 210, "pm_assignments": 0, "completed_tasks": 58, "fail_tasks": 0, "problems_count": 17, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 52.5), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 220, "pm_assignments": 6, "completed_tasks": 61, "fail_tasks": 0, "problems_count": 17, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 52.5), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 230, "pm_assignments": 0, "completed_tasks": 63, "fail_tasks": 0, "problems_count": 17, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 52.5), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 240, "pm_assignments": 0, "completed_tasks": 64, "fail_tasks": 0, "problems_count": 19, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 52.5), ("trabajador_5", 62), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 250, "pm_assignments": 0, "completed_tasks": 67, "fail_tasks": 0, "problems_count": 22, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 52.5), ("trabajador_5", 65.10000000000001), ("trabajador_6", 67), ("trabajador_7", 20), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 260, "pm_assignments": 3, "completed_tasks": 69, "fail_tasks": 0, "problems_count": 24, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 52.5), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 270, "pm_assignments": 3, "completed_tasks": 71, "fail_tasks": 0, "problems_count": 25, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 52.5), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 280, "pm_assignments": 0, "completed_tasks": 74, "fail_tasks": 0, "problems_count": 27, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 52.5), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 290, "pm_assignments": 0, "completed_tasks": 77, "fail_tasks": 0, "problems_count": 28, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 52.5), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 300, "pm_assignments": 0, "completed_tasks": 77, "fail_tasks": 0, "problems_count": 30, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 60), ("trabajador_4", 52.5), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 64)]', "cooperation_prob": 0.5},
        {"time": 310, "pm_assignments": 6, "completed_tasks": 82, "fail_tasks": 0, "problems_count": 32, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 63.0), ("trabajador_4", 52.5), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 67.2)]', "cooperation_prob": 0.5},
        {"time": 320, "pm_assignments": 3, "completed_tasks": 82, "fail_tasks": 0, "problems_count": 33, "escalate_problem_count": 0, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 64), ("trabajador_3", 63.0), ("trabajador_4", 52.5), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 67.2)]', "cooperation_prob": 0.5},
        {"time": 330, "pm_assignments": 4, "completed_tasks": 85, "fail_tasks": 0, "problems_count": 34, "escalate_problem_count": 1, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 67.2), ("trabajador_3", 63.0), ("trabajador_4", 52.5), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 67.2)]', "cooperation_prob": 0.5},
        {"time": 340, "pm_assignments": 0, "completed_tasks": 87, "fail_tasks": 0, "problems_count": 35, "escalate_problem_count": 1, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 67.2), ("trabajador_3", 63.0), ("trabajador_4", 52.5), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 67.2)]', "cooperation_prob": 0.5},
        {"time": 350, "pm_assignments": 0, "completed_tasks": 91, "fail_tasks": 0, "problems_count": 35, "escalate_problem_count": 1, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 67.2), ("trabajador_3", 63.0), ("trabajador_4", 52.5), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 67.2)]', "cooperation_prob": 0.5},
        {"time": 360, "pm_assignments": 0, "completed_tasks": 92, "fail_tasks": 0, "problems_count": 38, "escalate_problem_count": 1, "trust_in_agents": '[("trabajador_1", 27), ("trabajador_2", 67.2), ("trabajador_3", 63.0), ("trabajador_4", 52.5), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 67.2)]', "cooperation_prob": 0.5},
        {"time": 370, "pm_assignments": 0, "completed_tasks": 95, "fail_tasks": 0, "problems_count": 40, "escalate_problem_count": 1, "trust_in_agents": '[("trabajador_1", 28.35), ("trabajador_2", 67.2), ("trabajador_3", 63.0), ("trabajador_4", 55.125), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 67.2)]', "cooperation_prob": 0.5},
        {"time": 380, "pm_assignments": 0, "completed_tasks": 96, "fail_tasks": 0, "problems_count": 40, "escalate_problem_count": 1, "trust_in_agents": '[("trabajador_1", 28.35), ("trabajador_2", 67.2), ("trabajador_3", 63.0), ("trabajador_4", 55.125), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 67.2)]', "cooperation_prob": 0.5},
        {"time": 390, "pm_assignments": 0, "completed_tasks": 97, "fail_tasks": 0, "problems_count": 41, "escalate_problem_count": 2, "trust_in_agents": '[("trabajador_1", 28.35), ("trabajador_2", 67.2), ("trabajador_3", 63.0), ("trabajador_4", 55.125), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 67.2)]', "cooperation_prob": 0.5},
        {"time": 400, "pm_assignments": 0, "completed_tasks": 98, "fail_tasks": 0, "problems_count": 42, "escalate_problem_count": 2, "trust_in_agents": '[("trabajador_1", 28.35), ("trabajador_2", 67.2), ("trabajador_3", 63.0), ("trabajador_4", 55.125), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 67.2)]', "cooperation_prob": 0.5},
        {"time": 410, "pm_assignments": 0, "completed_tasks": 99, "fail_tasks": 0, "problems_count": 42, "escalate_problem_count": 2, "trust_in_agents": '[("trabajador_1", 28.35), ("trabajador_2", 67.2), ("trabajador_3", 63.0), ("trabajador_4", 55.125), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 67.2)]', "cooperation_prob": 0.5},
        {"time": 420, "pm_assignments": 0, "completed_tasks": 100, "fail_tasks": 0, "problems_count": 42, "escalate_problem_count": 2, "trust_in_agents": '[("trabajador_1", 28.35), ("trabajador_2", 67.2), ("trabajador_3", 63.0), ("trabajador_4", 55.125), ("trabajador_5", 65.10000000000001), ("trabajador_6", 70.35000000000001), ("trabajador_7", 21.0), ("trabajador_8", 30), ("trabajador_9", 67.2)]', "cooperation_prob": 0.5},
    ]


    # Datos completos de los trabajadores
    workers_data = [
        {"time": 0, "worker_id": "trabajador_1", "new_state": 1, "work": False, "rest": False},
        {"time": 0, "worker_id": "trabajador_2", "new_state": 1, "work": False, "rest": False},
        {"time": 0, "worker_id": "trabajador_3", "new_state": 1, "work": False, "rest": False},
        {"time": 0, "worker_id": "trabajador_4", "new_state": 1, "work": False, "rest": False},
        {"time": 0, "worker_id": "trabajador_5", "new_state": 1, "work": False, "rest": False},
        {"time": 0, "worker_id": "trabajador_6", "new_state": 1, "work": False, "rest": False},
        {"time": 0, "worker_id": "trabajador_7", "new_state": 1, "work": False, "rest": False},
        {"time": 0, "worker_id": "trabajador_8", "new_state": 1, "work": False, "rest": False},
        {"time": 0, "worker_id": "trabajador_9", "new_state": 1, "work": False, "rest": False},
        {"time": 10, "worker_id": "trabajador_1", "new_state": 1, "work": False, "rest": False},
        {"time": 10, "worker_id": "trabajador_2", "new_state": 1, "work": True, "rest": False},
        {"time": 10, "worker_id": "trabajador_3", "new_state": 1, "work": False, "rest": False},
        {"time": 10, "worker_id": "trabajador_4", "new_state": 1, "work": False, "rest": False},
        {"time": 10, "worker_id": "trabajador_5", "new_state": 1, "work": True, "rest": False},
        {"time": 10, "worker_id": "trabajador_6", "new_state": 1, "work": True, "rest": False},
        {"time": 10, "worker_id": "trabajador_7", "new_state": 1, "work": True, "rest": False},
        {"time": 10, "worker_id": "trabajador_8", "new_state": 1, "work": True, "rest": False},
        {"time": 10, "worker_id": "trabajador_9", "new_state": 1, "work": True, "rest": False},
        {"time": 20, "worker_id": "trabajador_1", "new_state": 1, "work": True, "rest": False},
        {"time": 20, "worker_id": "trabajador_2", "new_state": 1, "work": False, "rest": True},
        {"time": 20, "worker_id": "trabajador_3", "new_state": 1, "work": True, "rest": False},
        {"time": 20, "worker_id": "trabajador_4", "new_state": 1, "work": True, "rest": False},
        {"time": 20, "worker_id": "trabajador_5", "new_state": 1, "work": False, "rest": True},
        {"time": 20, "worker_id": "trabajador_6", "new_state": 1, "work": False, "rest": True},
        {"time": 20, "worker_id": "trabajador_7", "new_state": 1, "work": False, "rest": True},
        {"time": 20, "worker_id": "trabajador_8", "new_state": 1, "work": False, "rest": True},
        {"time": 20, "worker_id": "trabajador_9", "new_state": 1, "work": True, "rest": False},
        {"time": 30, "worker_id": "trabajador_1", "new_state": 1, "work": False, "rest": True},
        {"time": 30, "worker_id": "trabajador_2", "new_state": 1, "work": True, "rest": False},
        {"time": 30, "worker_id": "trabajador_3", "new_state": 1, "work": False, "rest": True},
        {"time": 30, "worker_id": "trabajador_4", "new_state": 1, "work": False, "rest": True},
        {"time": 30, "worker_id": "trabajador_5", "new_state": 1, "work": True, "rest": False},
        {"time": 30, "worker_id": "trabajador_6", "new_state": 1, "work": True, "rest": False},
        {"time": 30, "worker_id": "trabajador_7", "new_state": 1, "work": True, "rest": False},
        {"time": 30, "worker_id": "trabajador_8", "new_state": 1, "work": True, "rest": False},
        {"time": 30, "worker_id": "trabajador_9", "new_state": 1, "work": False, "rest": True},
        {"time": 40, "worker_id": "trabajador_1", "new_state": 1, "work": True, "rest": False},
        {"time": 40, "worker_id": "trabajador_2", "new_state": 1, "work": True, "rest": False},
        {"time": 40, "worker_id": "trabajador_3", "new_state": 1, "work": True, "rest": False},
        {"time": 40, "worker_id": "trabajador_4", "new_state": 1, "work": True, "rest": False},
        {"time": 40, "worker_id": "trabajador_5", "new_state": 1, "work": False, "rest": True},
        {"time": 40, "worker_id": "trabajador_6", "new_state": 1, "work": True, "rest": False},
        {"time": 40, "worker_id": "trabajador_7", "new_state": 1, "work": True, "rest": False},
        {"time": 40, "worker_id": "trabajador_8", "new_state": 1, "work": True, "rest": False},
        {"time": 40, "worker_id": "trabajador_9", "new_state": 1, "work": True, "rest": False},
        {"time": 50, "worker_id": "trabajador_1", "new_state": 1, "work": False, "rest": True},
        {"time": 50, "worker_id": "trabajador_2", "new_state": 1, "work": False, "rest": True},
        {"time": 50, "worker_id": "trabajador_3", "new_state": 1, "work": False, "rest": True},
        {"time": 50, "worker_id": "trabajador_4", "new_state": 1, "work": False, "rest": True},
        {"time": 50, "worker_id": "trabajador_5", "new_state": 1, "work": True, "rest": False},
        {"time": 50, "worker_id": "trabajador_6", "new_state": 1, "work": False, "rest": True},
        {"time": 50, "worker_id": "trabajador_7", "new_state": 1, "work": False, "rest": True},
        {"time": 50, "worker_id": "trabajador_8", "new_state": 1, "work": True, "rest": False},
        {"time": 50, "worker_id": "trabajador_9", "new_state": 1, "work": True, "rest": False},
        {"time": 60, "worker_id": "trabajador_1", "new_state": 1, "work": True, "rest": False},
        {"time": 60, "worker_id": "trabajador_2", "new_state": 1, "work": True, "rest": False},
        {"time": 60, "worker_id": "trabajador_3", "new_state": 1, "work": True, "rest": False},
        {"time": 60, "worker_id": "trabajador_4", "new_state": 1, "work": True, "rest": False},
        {"time": 60, "worker_id": "trabajador_5", "new_state": 1, "work": False, "rest": True},
        {"time": 60, "worker_id": "trabajador_6", "new_state": 1, "work": True, "rest": False},
        {"time": 60, "worker_id": "trabajador_7", "new_state": 1, "work": True, "rest": False},
        {"time": 60, "worker_id": "trabajador_8", "new_state": 1, "work": True, "rest": False},
        {"time": 60, "worker_id": "trabajador_9", "new_state": 1, "work": True, "rest": False},
        {"time": 70, "worker_id": "trabajador_1", "new_state": 1, "work": False, "rest": True},
        {"time": 70, "worker_id": "trabajador_2", "new_state": 1, "work": False, "rest": True},
        {"time": 70, "worker_id": "trabajador_3", "new_state": 1, "work": False, "rest": True},
        {"time": 70, "worker_id": "trabajador_4", "new_state": 1, "work": False, "rest": True},
        {"time": 70, "worker_id": "trabajador_5", "new_state": 1, "work": True, "rest": False},
        {"time": 70, "worker_id": "trabajador_6", "new_state": 1, "work": False, "rest": True},
        {"time": 70, "worker_id": "trabajador_7", "new_state": 1, "work": False, "rest": True},
        {"time": 70, "worker_id": "trabajador_8", "new_state": 1, "work": True, "rest": False},
        {"time": 70, "worker_id": "trabajador_9", "new_state": 1, "work": True, "rest": False},
        {"time": 80, "worker_id": "trabajador_1", "new_state": 1, "work": True, "rest": False},
        {"time": 80, "worker_id": "trabajador_2", "new_state": 1, "work": True, "rest": False},
        {"time": 80, "worker_id": "trabajador_3", "new_state": 1, "work": True, "rest": False},
        {"time": 80, "worker_id": "trabajador_4", "new_state": 1, "work": True, "rest": False},
        {"time": 80, "worker_id": "trabajador_5", "new_state": 1, "work": False, "rest": True},
        {"time": 80, "worker_id": "trabajador_6", "new_state": 1, "work": True, "rest": False},
        {"time": 80, "worker_id": "trabajador_7", "new_state": 1, "work": True, "rest": False},
        {"time": 80, "worker_id": "trabajador_8", "new_state": 1, "work": True, "rest": False},
        {"time": 80, "worker_id": "trabajador_9", "new_state": 1, "work": True, "rest": False},
        {"time": 90, "worker_id": "trabajador_1", "new_state": 1, "work": False, "rest": True},
        {"time": 90, "worker_id": "trabajador_2", "new_state": 1, "work": False, "rest": True},
        {"time": 90, "worker_id": "trabajador_3", "new_state": 1, "work": False, "rest": True},
        {"time": 90, "worker_id": "trabajador_4", "new_state": 1, "work": False, "rest": True},
        {"time": 90, "worker_id": "trabajador_5", "new_state": 1, "work": True, "rest": False},
        {"time": 90, "worker_id": "trabajador_6", "new_state": 1, "work": False, "rest": True},
        {"time": 90, "worker_id": "trabajador_7", "new_state": 1, "work": False, "rest": True},
        {"time": 90, "worker_id": "trabajador_8", "new_state": 1, "work": True, "rest": False},
        {"time": 90, "worker_id": "trabajador_9", "new_state": 1, "work": True, "rest": False},
        {"time": 100, "worker_id": "trabajador_1", "new_state": 1, "work": True, "rest": False},
        {"time": 100, "worker_id": "trabajador_2", "new_state": 1, "work": True, "rest": False},
        {"time": 100, "worker_id": "trabajador_3", "new_state": 1, "work": True, "rest": False},
        {"time": 100, "worker_id": "trabajador_4", "new_state": 1, "work": True, "rest": False},
        {"time": 100, "worker_id": "trabajador_5", "new_state": 1, "work": False, "rest": True},
        {"time": 100, "worker_id": "trabajador_6", "new_state": 1, "work": True, "rest": False},
        {"time": 100, "worker_id": "trabajador_7", "new_state": 1, "work": True, "rest": False},
        {"time": 100, "worker_id": "trabajador_8", "new_state": 1, "work": True, "rest": False},
        {"time": 100, "worker_id": "trabajador_9", "new_state": 1, "work": True, "rest": False},
        {"time": 110, "worker_id": "trabajador_1", "new_state": 1, "work": False, "rest": True},
        {"time": 110, "worker_id": "trabajador_2", "new_state": 1, "work": False, "rest": True},
        {"time": 110, "worker_id": "trabajador_3", "new_state": 1, "work": False, "rest": True},
        {"time": 110, "worker_id": "trabajador_4", "new_state": 1, "work": False, "rest": True},
        {"time": 110, "worker_id": "trabajador_5", "new_state": 1, "work": True, "rest": False},
        {"time": 110, "worker_id": "trabajador_6", "new_state": 1, "work": False, "rest": True},
        {"time": 110, "worker_id": "trabajador_7", "new_state": 1, "work": False, "rest": True},
        {"time": 110, "worker_id": "trabajador_8", "new_state": 1, "work": True, "rest": False},
        {"time": 110, "worker_id": "trabajador_9", "new_state": 1, "work": True, "rest": False},
        {"time": 120, "worker_id": "trabajador_1", "new_state": 1, "work": True, "rest": False},
        {"time": 120, "worker_id": "trabajador_2", "new_state": 1, "work": True, "rest": False},
        {"time": 120, "worker_id": "trabajador_3", "new_state": 1, "work": True, "rest": False},
        {"time": 120, "worker_id": "trabajador_4", "new_state": 1, "work": True, "rest": False},
        {"time": 120, "worker_id": "trabajador_5", "new_state": 1, "work": False, "rest": True},
        {"time": 120, "worker_id": "trabajador_6", "new_state": 1, "work": True, "rest": False},
        {"time": 120, "worker_id": "trabajador_7", "new_state": 1, "work": True, "rest": False},
        {"time": 120, "worker_id": "trabajador_8", "new_state": 1, "work": True, "rest": False},
        {"time": 120, "worker_id": "trabajador_9", "new_state": 1, "work": True, "rest": False},
        {"time": 130, "worker_id": "trabajador_1", "new_state": 1, "work": False, "rest": True},
        {"time": 130, "worker_id": "trabajador_2", "new_state": 1, "work": False, "rest": True},
        {"time": 130, "worker_id": "trabajador_3", "new_state": 1, "work": False, "rest": True},
        {"time": 130, "worker_id": "trabajador_4", "new_state": 1, "work": False, "rest": True},
        {"time": 130, "worker_id": "trabajador_5", "new_state": 1, "work": True, "rest": False},
        {"time": 130, "worker_id": "trabajador_6", "new_state": 1, "work": False, "rest": True},
        {"time": 130, "worker_id": "trabajador_7", "new_state": 1, "work": False, "rest": True},
        {"time": 130, "worker_id": "trabajador_8", "new_state": 1, "work": True, "rest": False},
        {"time": 130, "worker_id": "trabajador_9", "new_state": 1, "work": True, "rest": False},
    ]


    # Generar resumen
    summary = generator.generate_summary(pm_data, workers_data)
    print("Generated Summary:")
    print(summary)
