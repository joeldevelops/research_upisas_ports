import os
import requests
import json
from fastapi import APIRouter, Depends
from fastapi.responses import JSONResponse
from genson import SchemaBuilder
from typing import List
from models.configuration import Configuration

router = APIRouter()

ews_url = os.environ.get("EWS_URL")

@router.get("", response_model=List[Configuration])
def adaptation_options():
    endpoint_url = f"{ews_url}/get_all_configs"
    response = requests.get(endpoint_url)

    if response.status_code == 200:
        configs = response.json()["configs"]
        # Assign IDs to each configuration starting from 0
        configs_with_ids = [{"id": idx, "config": config} for idx, config in enumerate(configs)]
        return JSONResponse(status_code=response.status_code, content={"configs": configs_with_ids})
    else:
        return JSONResponse(status_code=response.status_code, content={"message: Request failed."})

@router.get("_schema")
def adaptation_options_schema(response: dict = Depends(adaptation_options)):  
    sb = SchemaBuilder()
    sb.add_object(json.loads(response.body))
    return sb.to_schema()
