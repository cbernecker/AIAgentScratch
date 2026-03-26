import re
from openai import OpenAI
from tools import  tools, tools_schema
import json
client = OpenAI()

system_prompt = """
You are a dynamic AI Agent. You work in a continuous 
loop of 
- Thought, 
- Action, 
- Observation.

Your available tools are:
- get_planet_mass("planet", "planet_name": dict): Returns the mass of a given planet..
- calculate("number1", "number2": dict): Evaluates a math expression.

Use the following format exactly:
Question: the input question you must answer
Thought: you should always think about what to do
Action: the action to take, should be one of [get_planet_mass, calculate]
Action Input: the input to the action

(You will then receive an Observation from the environment)
Thought: I now know the answer
Final Answer: the final answer to the original input question
"""

class Agent():
    def __init__(self, system_prompt, available_tools_dict):
        self.plan = False # checks if the agent has a plan
        self.system_prompt = system_prompt
        self.available_tools_dict = available_tools_dict

    # The Reasoning 
    @staticmethod #function never needs to access data stored inside the class
    def call_llm(messages: list,
                 model: str = "gpt-4.1-nano", 
                 temperature: float = 0.7,
                 json_output: bool = False):
        

            response = client.responses.create(
                model=model,
                temperature=temperature,
                input=messages
            )
            
            return response.output_text
    
    def execute_tool(self, func_name, kwargs):
        function_to_call = self.available_tools_dict[func_name]
        return function_to_call(kwargs)  
    
    
    def react_agent(self, user_question, max_turns=5):
        # Initialize our conversational memory with the system prompt
        messages = [
            {"role": "system", "content": self.system_prompt},
            {"role": "user", "content": f"Question: {user_question}"}
        ]
        
        turn_count = 0
        
        while turn_count < max_turns:
            print(f"\n--- Turn {turn_count + 1} ---")
            
            # 1. Get the LLM's response (The Thought + Action)
            response = my_react_agent.call_llm(messages)
            print(response)
            
            # Add the LLM's generation to the memory
            messages.append({"role": "assistant", "content": response})
            
            # 2. Check if the agent has reached a conclusion
            if "Final Answer:" in response:
                print("\n✅ Task Complete.")
                #print(json.dumps(messages, indent=2))
                return response.split("Final Answer:")[-1].strip()
            
            # 3. Parse the Action and Action Input using Regex
            action_match = re.search(r"Action: (.*)", response)
            input_match = re.search(r"Action Input: (.*)", response)
            
            if action_match and input_match:
                action = action_match.group(1).strip()
                action_input = input_match.group(1).strip()
                
                # 4. The Observation Phase (Python takes control)
                print(f"⚙️ System Executing: {action}({action_input})")
                try:
                    action_input = json.loads(action_input)
                    observation_result = my_react_agent.execute_tool(action, action_input)
                except (TypeError, ValueError, json.JSONDecodeError) as error_messgae:
                    observation_result = error_messgae
                # Format the observation and feed it back to the agent
                observation_text = f"Observation: {observation_result}"
                messages.append({"role": "user", "content": observation_text})
                print(observation_text)
                
            else:
                # If the LLM breaks the API contract, gently correct it
                messages.append({"role": "user", "content": "Error: Invalid format. Please provide an Action and Action Input, or a Final Answer."})
                
            turn_count += 1
        return "❌ Agent timed out before reaching a final answer."

my_react_agent = Agent(system_prompt, tools)
my_react_agent.react_agent("What is the combine mass of Earth and jupiter")