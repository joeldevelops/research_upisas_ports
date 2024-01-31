import os
import requests
from fastapi import APIRouter
from fastapi.responses import JSONResponse
from genson import SchemaBuilder
from models.configuration import Configuration, default_configuration


router = APIRouter()

ews_url = os.environ.get("EWS_URL")


@router.put("")
def execute(configuration:Configuration):
    endpoint_url = f"{ews_url}/set_config"
    response = requests.post(endpoint_url, json={"config": configuration.config})

    if response.status_code == 200:
        return JSONResponse(status_code=response.status_code, content={"message": "Successfully executed adaptation."})
    else:
        return JSONResponse(status_code=response.status_code, content={"message": "Failed to execute adaptation."})

@router.get("_schema")
def execute_schema(): 
    sb = SchemaBuilder()
    sb.add_object(default_configuration.model_dump(mode='json'))
    return sb.to_schema()
