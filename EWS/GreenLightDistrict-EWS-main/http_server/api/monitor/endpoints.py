import os
import requests
import json
from fastapi import APIRouter, Depends
from genson import SchemaBuilder
from fastapi.responses import JSONResponse

router = APIRouter()

ews_url = os.environ.get("EWS_URL")

@router.get("")
def monitor():
    endpoint_url = f"{ews_url}/get_perception"
    response = requests.get(endpoint_url)

    if response.status_code == 200:
        perception = response.json()[0]
        return JSONResponse(status_code=response.status_code, content=perception)
    else:
        return JSONResponse(status_code=response.status_code, content={"message: Request failed."})


@router.get("_schema")
def monitor_schema(response: dict = Depends(monitor)):  
    sb = SchemaBuilder()
    sb.add_object(json.loads(response.body))
    return sb.to_schema()
