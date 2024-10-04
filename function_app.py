import azure.functions as func
import logging
import json
import requests
from requests.exceptions import Timeout

app = func.FunctionApp(http_auth_level=func.AuthLevel.ANOYMOUS)

# Internal API endpoint
INTERNAL_API_URL = "https://spotbot.swca.com/"

@app.route(route="http_trigger")
def http_trigger(req: func.HttpRequest) -> func.HttpResponse:

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
        response = requests.post(INTERNAL_API_URL, json=req_body, timeout=5)
        response.raise_for_status()
    except Timeout:
        logging.error("Internal API request timed out")
        return func.HttpResponse(
            "Internal API request timed out",
            status_code=500
        )
    except requests.RequestException as e:
        logging.error(f"Internal API request failed: {e}")
        return func.HttpResponse(
            "Internal API request failed",
            status_code=500
        )

    # Return the response from the internal API
    return func.HttpResponse(
        "Success",
        status_code=200
    )

def verify_message(message):
    # Add your message verification logic here
    # For example, check if certain keys exist
    return True