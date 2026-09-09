#!/usr/bin/env python3
from .llm_interactions import (
    extract_constraints_from_model,
    validate_extracted_constraints
)
from .utils import (
    deadline_to_hours,
    json_printer,
    distance_or_cost    
)
import os
from dotenv import dotenv_values
import json
import os
import sys
from termcolor import colored
import psycopg2
from psycopg2 import extras
from dateutil.relativedelta import relativedelta
import argparse
import geocoder


#env variables
CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(CURRENT_DIR)
ENV_PATH = os.path.join(PROJECT_ROOT, ".env")
config = dotenv_values(ENV_PATH)
API_KEY = config.get('API_KEY')


if not API_KEY:
    print(f"Error: API_KEY not founf.\n")
    sys.exit(1)


def main():

    #get user coordinates using IP address
    g = geocoder.ip('me')
    coordinates = g.latlng

    none_list = []
    user_inputs = []

    mock_input = str("2 days, batch, 500 dollars")

    ############
    #User Layer#
    ############
    
    #gets the user natural language input
    user_inputs.append(str(input("Type your request: ")))
    #user_inputs.append(mock_input)


    #chat_response = """{
    #    "budget": 20000.0,
    #    "deadline": "1 week",
    #    "application_type": "batch_computing",
    #    "resources": {
    #        "cpu_cores": 20,
    #        "gpu": null,
    #        "memory_gb": 400,
    #        "storage_gb": 20
    #    },
    #    "preference": "latency"
    #}"""

    #calls the llm
    chat_response = extract_constraints_from_model(API_KEY, user_inputs)['choices'][0]['message']['content']

    #validates the extracted constraints
    if validate_extracted_constraints(chat_response):
        print("validated\n")
    else:
        print(f"Validation failed, please try again\n")
        return "error"


    ##################
    #Validation layer#
    ##################
    #checks for missing information
    for key, value in json.loads(chat_response).items():
        if value is None:
            none_list.append(key) 


    #Calls the llm until there is no missing information
    while len(none_list) > 0:
        print("Could you please specify more about these topics? \n")
        for key in none_list:
            print(colored(f"{key}", "blue"))

        #calls the llm again
        user_inputs.append(str(input("Type your request: ")))        
        chat_response = extract_constraints_from_model(API_KEY, user_inputs)['choices'][0]['message']['content']

        #validates the output
        if validate_extracted_constraints(chat_response):
            print("validated\n")
        else:
            print(f"Validation failed, please try again\n")
            return "error"

        #checks again if there is something missing
        none_list = []
        for key, value in json.loads(chat_response).items():
            if value is None:
                none_list.append(key)      
        
    parsed_json = json.loads(chat_response)

    #Asks for the user preference, cost or latency
    while True:
        print(colored("What is your preference? ", "cyan"))
        print(colored("[0] Lower Latency", "blue"))
        print(colored("[1] Lower price", "blue"))
        user_priority = str(input()).lower()
        #user_priority = str("y").lower()

        if user_priority.lower() in ['0']:
            parsed_json['preference'] = 'latency'
            print("Lower latency then!")
            break
        elif user_priority.lower() in ['1']:
            parsed_json['preference'] = 'price'
            print("Lower price then!")
            break


    #Asks for the user approval before the database layer
    while True:
        #os.system("clear")
        print(f"User inputs:")
        for counter, item in enumerate(user_inputs):
            print(f"input {counter+1}: \n\t{item}")
        print("\n")

        print(f"The parsed constraints are: \n")
        json_printer(parsed_json, "cyan")
        print(f"\ndo you wish to continue? (y or n)\n")


        user_confirmation = str(input()[:1]).lower()
        #user_confirmation = str("y").lower()

        if user_confirmation.lower() in ['yes', 'y']:
            break
        elif user_confirmation.lower() in ['no', 'n']:
            print("Okay then!\n")
            return "aborted"


    user_constraints = parsed_json

    ################
    #Database Layer#
    ################
    try:
        conn = psycopg2.connect("host=localhost dbname=postgres user=postgres password=123mudar")
        cur = conn.cursor(cursor_factory=extras.DictCursor)

        hours = float(deadline_to_hours(user_constraints['deadline']))
        budget_per_hour = float(float(user_constraints['budget']) / float(deadline_to_hours(user_constraints['deadline'])))


        result = []
        query_count = int(0)
        while len(result) == 0:
            sql_command = f"""
            WITH priced_instances AS (
            SELECT
                        instances.cloud_service_provider,
                        instances.instance_type,
                        CASE
                    	  WHEN instances.storage_size = 0 THEN (({float(user_constraints['resources']['storage_gb'])} / 720.0 * {hours} * ebs_price_relation.price_per_gb_per_month::numeric) + spots.on_demand_price::numeric)
    				      WHEN instances.storage_size is NULL THEN (({float(user_constraints['resources']['storage_gb'])} / 720.0 * {hours} * ebs_price_relation.price_per_gb_per_month::numeric) + spots.on_demand_price::numeric)
                          ELSE spots.on_demand_price::numeric
                        END AS calculated_price,
                        CASE
                    	  WHEN instances.storage_size = 0 THEN (({float(user_constraints['resources']['storage_gb'])} / 720.0 * {hours} * ebs_price_relation.price_per_gb_per_month::numeric))
    				      WHEN instances.storage_size is NULL THEN (({float(user_constraints['resources']['storage_gb'])} / 720.0 * {hours} * ebs_price_relation.price_per_gb_per_month::numeric))
                          ELSE 0.0
                        END AS storage_price,
                        spots.region,
                        spots.availability_zone,
                        instances.storage_size,
                        instances.memory_size,
                        ST_Distance(
                            ST_SetSRID(
                                ST_MakePoint(regions.lng, regions.lat),
                                4326
                            )::geography,
                            ST_SetSRID(
                                ST_MakePoint({user_lng}, {user_lat}),
                                4326
                            )::geography
                        ) / 1000 AS distance_km
                    FROM
                        spots JOIN instances
                        ON
                            instances.instance_type = spots.instance_type
                        JOIN regions ON
                            spots.region = regions.code
                        JOIN ebs_price_relation ON
                        		instances.cloud_service_provider = ebs_price_relation.cloud_service_provider
                    WHERE
                        instances.memory_size >= {user_constraints['resources']['memory_gb']} AND
                        instances.vcpu >= {user_constraints['resources']['cpu_cores']}
                    ORDER BY {distance_or_cost(user_constraints['preference'])} ASC
             )
             select * from priced_instances
                where calculated_price <= {budget_per_hour}
                LIMIT 1
             ;
            """
            print(sql_command)
            cur.execute(sql_command)
            query_count += 1
            budget_per_hour += 0.10
            result = cur.fetchall()
            conn.commit()
    except Exception as e:
        print(f"Error: {e}")
        print("Something unexpected happened, please try again!")
    finally:
        conn.close()


    ########
    #Result#
    ########
    if len(result) > 0:
        print(colored("The best result for your requirements are: ", "cyan"))
        if (query_count > 1):
            print(colored(f"""
No instance was found that satisfies your requirements within the specified budget.

An additional ${query_count * 0.10 * hours:.2f} would be required to meet your requirements.
            """, "cyan"))
            
        if (dict(result[0])['storage_size'] in (0, None) ):
            print(colored(f"""
The instance found doesn't have a fixed storage value
so network attached storage was selected
and that costs per hour: ${result[0]['storage_price']:.3f}
            """, "cyan"))
            
        json_printer(dict(result[0]), "blue")


            

    if result and result[0]:
        return dict(result[0])

    return {}
