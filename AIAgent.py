from openai import OpenAI
import openai
import logging
import json
import os

client = OpenAI()

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
    
    def run(self, user_prompt: str, tools: list):
        '''This functions is the orches
        trator'''
        action_plan = self.__plan_tasks(user_prompt)
        execution_plan = self.__plan_tools(action_plan, tools)
        pass
        #return action_plan
        

    def __plan_tasks(self, user_prompt: str)-> json:
        '''This plans the task the LLM will do'''
        planner_system_prompt = (
            "You are a sophisticated planner Agent. "
            "Your job is to break down complex user questions into sequential, simple tasks. "
            "Return a JSON object with a single key  "
            " - 'tasks': list[string] #which contains a list of strings."
        )
        
        action_plan = self.call_llm(planner_system_prompt, user_prompt)
        logger.info(f'The action plan is: {action_plan}')
        action_plan = json.loads(action_plan.output_text) # converts string to JSON
        self.plan = True
        return action_plan
    
    def __plan_tools(self, action_plan: list, tools: list) -> json:
        '''Calls the functions that are necessary to fullfill the tasks'''
        execution_plan = []
        execution_system_prompt  = (
            "You are a sophisticated planner Agent. "
            "Your job is to find the correct given tools to the system to solve the given tasks."
            "The available tools and the task you will get from the user"
            "If no tools fit to Task write None"
            "Return a JSON object with a single key  "
            " - 'task': {task}"
            " - 'function': string # name of the tool"
        )
        for task in action_plan["tasks"]:
            logger.info(f'Checking Task: {task}')
            user_prompt = (f"I have the following task to do: {task}"  
                           f"I can use the following tools: {tools} to solve the taks "
                            "Tell me the correct tool to use for a given task"
                           f"Here is the full list of tasks {action_plan}"
            )
            response = self.call_llm(execution_system_prompt ,user_prompt)
            execution_plan.append(response.output_text)
        logger.info(f'The action plan is: {execution_plan}')
        return execution_plan
    
    def __execute_plan():
        pass


system_prompt = "You are a usefull assistant"
user_prompt = "What is the combine mass of Earth and jupiter" #"Write a one-sentence bedtime story about a unicorn."
# 1. Define a list of callable tools for the model
tools = [
    {
        "type": "function",
        "name": "get_planet_mass",
        "description": "Get the mass of a given planet.",
        "parameters": {
            "type": "object",
            "properties": {
                "planet": {
                    "type": "string",
                    "description": "Mass of the earth in kg",
                },
            },
            "required": ["planet"],
        },
    },
    {
        "type": "function",
        "name": "calculate",
        "description": "Sum two numbers together",
        "parameters": {
            "type": "object",
            "properties": {
                "number1": {
                    "type": "number",
                    "description": "The first number",
                },
                "number2": {
                    "type": "number",
                    "description": "The second number",
                },
            },
            "required": ["number1", "number2"],
        },
    },
]

if os.environ.get("OPENAI_API_KEY"):
    my_Agent = Agent()
    response = my_Agent.run(user_prompt, tools)
    #logger.info(f"Output: \n {response.output_text}.")
else:
    print("No OPENAI_API_KEY is set. You can find your API key at https://platform.openai.com/account/api-keys.")


