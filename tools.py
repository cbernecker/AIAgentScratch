import json

def get_planet_mass(planet):
    # Ensure we are working with a string and cleaning it up
    if isinstance(planet, dict):
        planet = planet.get("planet", "")
    else:
        raise ValueError("Type doesnt' match please provide a dictionary with planet as key and planetname as value. Like {'planet': 'Earth'}")

    planet = str(planet).lower().strip()

    masses = {
        "earth": "5.972e24",
        "mars": "6.39e23",
        "jupiter": "1.898e27"
    }
    return masses.get(planet, "Unknown planet.")
    
def calculate(numbers):
    # #A risky tool in production, but perfect for a demo!
    #print(number1)
    #print(number2)
    #a = number1["number1"] 
    #b = number2["number2"] 
    if isinstance(numbers, dict):
        a = numbers.get("number1", "")
        b = numbers.get("number2", "")
    else:
        raise ValueError('Type does not match please provide a dictionary like {"number1": 2, "number2":3}')


    #a = float(numbers["number1"])
    #b = float(numbers["number2"])
    return a + b

# Define a list of callable tools for the model
tools_schema = [
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
            "required": ["numbers"],
        },
    },
]

tools = {
    "get_planet_mass": get_planet_mass,
    "calculate": calculate
}