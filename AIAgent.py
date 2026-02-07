from openai import OpenAI
import openai
import logging
import json
import os
from tools import get_planet_mass, calculate, tools_schema

client = OpenAI()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)


available_functions = {
    "get_planet_mass": get_planet_mass,
    "calculate": calculate
}

class Agent():
    def __init__(self, available_tools_dict):
        self.plan = False # checks if the agent has a plan
        self.system_prompt = "You are a usefull assistant"
        self.available_tools_dict = available_tools_dict

    # Structured Plan-and-Execute Agent
    def run_plan_execute(self, user_prompt: str, tools: list):
        '''This functions is the orchestrator'''
        action_plan = self.__plan_tasks(user_prompt)
        execution_plan = self.__plan_tools(action_plan, tools)
        return self.call_llm(f'Answer the question of the user based on the {execution_plan} we created to solve the problem. Also explain how you get to the answer.', user_prompt)

    # The Reasoning 
    @staticmethod # function never needs to access data stored inside the class
    def call_llm(system_prompt: str, user_prompt: str, model: str = "gpt-4.1-nano", temperature: float = 0.7):
        
        response = client.responses.create(
            model=model,
            temperature=temperature,
            input=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
        )
        return response
        
    # The Brain: We ask a LLM that to plan
    def __plan_tasks(self, user_prompt: str)-> json:
        '''This plans the task the LLM will do'''
        planner_system_prompt = (
            "You are a sophisticated planner Agent. "
            "Your job is to break down complex user questions into sequential, simple tasks. "
            "Return a JSON object with a single key  "
            " - 'tasks': list[string] #which contains a list of strings."
        )
        
        action_plan = self.call_llm(planner_system_prompt, user_prompt)
        logger.info(f'The action plan is: {action_plan.output_text}')
        action_plan = json.loads(action_plan.output_text) # converts string to JSON
        self.plan = True
        return action_plan
    
    # The Environment: this is where the wokr happens
    def __plan_tools(self, action_plan: list, tools: list) -> json:
        '''Calls the functions that are necessary to fullfill the tasks'''
        execution_plan = []
        response = ""
        execution_system_prompt  = (
            "You are a sophisticated planner Agent. "
            "Your job is to find the correct given tools to the system to solve the given tasks."
            "The available tools and the task you will get from the user"
            "If no tools fit to Task write None"
            "Return a JSON object with a single key  "
            " - 'id: int #unique id to identify the task "
            " - 'task': {task}"
            " - 'function': string # name of the tool"
            " - 'properties: list # properties to execute the function"
            " - 'dependencies': list # id's if the needed results of other tasks"
        )
        for task in action_plan["tasks"]:
            logger.info(f"******************Execute Task: {task} *******************")
            user_prompt = (f"I have the following task to do: {task}"  
                           f"I can use the following tools: {tools} to solve the taks "
                            "Tell me the correct tool to use for a given task"
                           f"Here is the full list of tasks {action_plan}"
                           F"Here are the executions that are already done {execution_plan} take the results of tasks have dependencies."
            )

            max_retries = 3
            attempts = 0
            success = False
            
            # Find the Tools we have available to solve the task
            while attempts < max_retries and not success:
                try:
                    # 1. Call the LLM
                    response = self.call_llm(execution_system_prompt ,user_prompt)
                    logger.info(f'Execute Task: {response.output_text}')
                    # 2. Attempt to parse JSON
                    response = json.loads(response.output_text)
                    # 3. If successful, extract data and break the while loop
                    kwargs = response["properties"]
                    func_name = response["function"]
                    success = True
                except (json.JSONDecodeError, KeyError) as e:
                    attempts += 1
                    logger.warning(f"Attempt {attempts} failed with error: {e}. Retrying...")
                    if attempts == max_retries:
                        logger.error("Max retries reached. Moving to next task or handling failure.")
                        raise RuntimeError("Max retries reached. Moving to next task or handling failure.")
            
            # Execute the Tools we have available to solve the task
            if func_name in self.available_tools_dict:
                logger.info(f"Execute Function {func_name} with {kwargs}...")
                function_to_call = self.available_tools_dict[func_name]
                result = function_to_call(*kwargs) 
                response["result"] = result # Add Result to the task. 
                logger.info(f"Result of {func_name}: {result}")
            execution_plan.append(response)
        logger.info(f'The execution plan is: {execution_plan}')
        return execution_plan
    
    def __execute_plan():
        pass


system_prompt = "You are a usefull assistant"
user_prompt = "What is the combine mass of Earth and jupiter" #"Write a one-sentence bedtime story about a unicorn."

if os.environ.get("OPENAI_API_KEY"):
    my_Agent = Agent(available_functions) # create Agent
    response = my_Agent.run(user_prompt, tools_schema)
    logger.info(f"Output: \n {response.output_text}.")
else:
    print("No OPENAI_API_KEY is set. You can find your API key at https://platform.openai.com/account/api-keys.")


