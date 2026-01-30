from openai import OpenAI
import logging
import json

api_key = "YOUR KEY"
client = OpenAI(api_key=api_key)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

def get_planet_mass(planet):
    planet = planet["planet"].lower().strip() #planet.lower().strip()
    masses = {
        "earth": "5 kg",
        "mars": "10 kg",
        "jupiter": "15 kg"
    }
    return masses.get(planet, "Unknown planet.")
    
def calculate(number1, number2):
    # #A risky tool in production, but perfect for a demo!
    return json.dumps({"result": number1 + number2})


class Agent():
    def __init__(self):
        self.plan = False # checks if the agent has a plan
        self.system_prompt = "You are a usefull assistant"


    @staticmethod # function never needs to access data stored inside the class
    def call_llm(system_prompt: str, user_prompt: str, model: str = "gpt-4.1-nano", temperature: float = 0.7):
        
        logger.info(f"Calling LLM ({model})...")
        response = client.responses.create(
            model=model,
            temperature=temperature,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )

        logger.debug(f"Response: ({response})")
        logger.info("LLM response received successfully.")
        
        return response
    
    def run(self, user_prompt: str):
        action_plan = self.__plan(user_prompt)
        return action_plan
        

    def __plan(self, user_prompt: str):
        '''This plans the task the LLM will do'''
        planner_system_prompt = (
            "You are a sophisticated planner Agent. "
            "Your job is to break down complex user questions into sequential, simple tasks. "
            "Return a JSON object with a single key 'tasks' which contains a list of strings."
        )
        action_plan = self.call_llm(planner_system_prompt, user_prompt)
        self.plan = True
        return action_plan
    
    def __execute(self, action_plan: list):
        '''Calls the functions that are necessary'''
        for task in action_plan:
            user_prompt = (f"I have the following task to do {task}" 
                            "I can use the following functions to solve the taks "
                            "Tell me the correct function to use"
            )
            self.call_llm(user_prompt)
        pass


system_prompt = "You are a usefull assistant"
user_prompt = "What is the combine mass of Earth and jupiter" #"Write a one-sentence bedtime story about a unicorn."
my_Agent = Agent()
response = my_Agent.run(user_prompt)
logger.info(f"Output: \n {response.output_text}.")
