import logging

import azure.functions as func
from azure.functions import FunctionApp

import requests
from requests.exceptions import Timeout

import jsonschema
from jsonschema import validate


# Internal API endpoint
INTERNAL_API_URL = "https://fdc-report-api.swca.com/api/FDCreport"
#INTERNAL_API_URL = "https://fdc-gis-api.swca.com/api/webhook_router"

# Define the function and route
app = FunctionApp()

@app.function_name(name="WebHookGateway")
@app.route(route="WebHookGateway", methods=["POST"])
def main(req: func.HttpRequest) -> func.HttpResponse:
    
    logging.info('Python HTTP trigger function processed a request.')

    # Get the response and parse it
    try:
        req_body = req.get_json()
    except ValueError:
        return func.HttpResponse(
            "Invalid JSON",
            status_code=400
        )
    
    # Verify the message (Add your verification logic here)
    if not verify_message(req_body):
        return func.HttpResponse(
            "Invalid message",
            status_code=400
        )
    
    # Call internal API
    try:
        logging.info(f"Calling internal API with message: {req_body}")
        response = requests.post(INTERNAL_API_URL, json=req_body, timeout=60, verify=False)
        response.raise_for_status()
    except Timeout:
        logging.error("Internal API request timed out")
        return func.HttpResponse(
            "Internal report API request timed out",
            status_code=500
        )
    except requests.RequestException as e:
        logging.error(f"Internal API request failed: {e}")
        return func.HttpResponse(
            "Internal report API request failed with error: " + str(e),
            status_code=500
        )
    
    # Return the response from the internal API
    return func.HttpResponse(
        "Success",
        status_code=200
    )

# Verify the message against the JSON schema
def verify_message(message) -> bool:
    try:
        validate(instance=message, schema=schema)
        return True
    except jsonschema.exceptions.ValidationError as e:
        print(e.message)
        return False
    
# Define the JSON schema
schema = {
    "type": "array",
    "items": {
        "type": "object",
        "properties": {
            "name": {"type": "string"},
            "layerId": {"type": "integer"},
            "orgId": {"type": "string"},
            "serviceName": {"type": "string"},
            "lastUpdatedTime": {"type": "integer"},
            "changesUrl": {"type": "string", "format": "uri"},
            "events": {
                "type": "array",
                "items": {"type": "string", "enum": ["FeaturesCreated"]}
            }
        },
        "required": ["name", "layerId", "orgId", "serviceName", "lastUpdatedTime", "changesUrl", "events"],
        "additionalProperties": False
    },
    "minItems": 1
}

