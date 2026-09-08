import json
import requests

# Common application types for cloud deployment
allowed_app_types = [
    "batch_computing",
    "api_deployment",
    "web_application",
    "database",
    "data_processing",
    "machine_learning",
    "deep_learning",
    "computer_vision",
    "natural_language_processing",
    "high_performance_computing",
    "stream_processing",
    "real_time_processing",
    "distributed_computing",
    "containerized_application",
    "microservice",
    "development_environment"
]


###
#Calls the LLM to parse the user_request
###
def extract_constraints_from_model(token, user_request):
    
    expected_json_structure = {
        "budget": "float or null",
        "deadline": "PostgreSQL INTERVAL string or null",
        "application_type": "string (must be from allowed list)",
        "resources": {
            "cpu_cores": "integer or null",
            "gpu": "string (e.g., '1x NVIDIA T4' or null)",
            "memory_gb": "integer or null",
            "storage_gb": "integer or null"
        }
    }

    system_prompt = f"""
    Extract deployment constraints from the user's request and return ONLY valid JSON matching this schema:
    {json.dumps(expected_json_structure, indent=2)}

    Rules:
    - budget: Extract the maximum budget as a float. If it cannot be determined or reasonably inferred, use null.
    - deadline: Extract or infer the execution deadline as a PostgreSQL INTERVAL string (e.g. "2 hours"). Otherwise use null.
    - application_type: Classify the request as one of {json.dumps(allowed_app_types)} or null. Never invent new values.
    - resources (Required Resources): 
        1. Infer the necessary computing resources based on the scale of the task and application type. Provide logical estimations.
        2. Fallback Minimums: If completely ambiguous, default to sensible minimums (e.g., cpu_cores: 2, memory_gb: 4, storage_gb: 20, gpu: 0) rather than null.

    Output only the JSON object. No markdown, no explanations, no code fences.
    """
    
    # Api request
    url = 'https://openrouter.ai/api/v1/chat/completions'
    headers = {
        'Authorization': f'Bearer {token}',
        'Content-Type': 'application/json'
    }
    
    data = {
      "model": "google/gemma-4-31b-it",
      "messages": [
        {
          "role": "system",
          "content": system_prompt
        },
        {
          "role": "user",
          "content": f"Extract the deployment constraints from this task description:\n\n{str(user_request)}"
        }
      ]
    }
    
    response = requests.post(url, headers=headers, json=data)
    return response.json()


###
#Checks if the llm data is formatted appropriately
###
def validate_extracted_constraints(json_data):
    """
    Validate the JSON returned by the LLM.
    Returns True if it passes, else returns False.
    """
    
    # 1. Parsing: Check if input is string or dict
    if isinstance(json_data, str):
        try:
            data = json.loads(json_data)
        except json.JSONDecodeError:
            print("Not JSON\n")
            return False
    elif isinstance(json_data, dict):
        data = json_data
    else:
        print("Not valid JSON\n")
        return False

    # makes sure data is a dictionary
    if not isinstance(data, dict):
        print("Parsed data is not a JSON object\n")
        print(data)
        return False


    # 2. Extract fields
    budget = data.get("budget")
    deadline = data.get("deadline")
    application_type = data.get("application_type")
    resources = data.get("resources")
    cpu = data.get("resources.cpu_cores")
    # 3. Validate root fields
    if budget is not None and type(budget) not in (float, int):
        print("budget not in format\n")
        return False

    if deadline is not None and not isinstance(deadline, str):
        print("deadline not in format\n")
        return False

    if application_type is not None and application_type not in allowed_app_types:
        print("app_type not in format\n")
        return False

    if not isinstance(resources, dict):
        print("resources not in format\n")
        return False
        
    #only possible after validate resources     
    gpu = data.get("resources.gpu")
    memory = data.get("resources.memory_gb")
    storage = data.get("resources.storage_gb")
    
    # 4. Validate resources sub-fields
    if cpu is not None and type(cpu) is not int:
        print("cpu_cores not in format\n")
        return False
        
    if memory is not None and type(memory) is not int:
        print("memory not in format\n")
        return False
        
    if storage is not None and type(storage) is not int:
        print("storage not in format\n")
        return False

    gpu = resources.get("gpu")
    if gpu is not None and not isinstance(gpu, str):
        print("gpu not in format\n")
        return False

    return True


