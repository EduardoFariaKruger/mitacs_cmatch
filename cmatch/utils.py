import re
from termcolor import colored
from decimal import Decimal

###
#Recursive json printer
###
def json_printer(json: dict, color, indent=""):
    if isinstance(json, dict):
        for key, value in json.items():
            if not isinstance(value, dict):
                if isinstance(value, Decimal):
                    print(colored(f"{indent}{key}", f"{color}") + f": {value:.3f}")
                else:
                    print(colored(f"{indent}{key}", f"{color}") + f": {value}")                    
            else:
                print(colored(f"{indent}{key}:", f"{color}"))
                json_printer(value, color, indent + "\t")
        
###
#Converts the formated deadline to the corresponding number of hours
###
def deadline_to_hours(deadline_str: str):
    if not deadline_str:
        return 0.0

    deadline_str = str(deadline_str).strip().lower()
    total_hours = 0.0

    conversions = {
        'month': 720,
        'week': 168,
        'day': 24,
        'hour': 1,
        'minute': 1 / 60
    }

    for unit, multiplier in conversions.items():
        pattern = rf'(\d+(?:\.\d+)?)\s*{unit}s?'
        match = re.search(pattern, deadline_str)
        
        if match:
            value = float(match.group(1))
            total_hours += value * multiplier

    return total_hours

###
#Checks the user decision and converts to the appropriate database camp
###
def distance_or_cost(decision: str) -> str:
    if decision == 'latency':
        return "distance_km"
    elif decision == 'price':
        return "spots.on_demand_price"
