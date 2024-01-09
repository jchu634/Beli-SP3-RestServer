from fastapi import APIRouter, Request
from fastapi.responses import ORJSONResponse
from fastapi.encoders import jsonable_encoder
import collections
import config
import logging
import traceback

plug_router = APIRouter(tags=["plugs"])
plug = collections.namedtuple("plug", "ip name retAdr state")


@plug_router.get("/plugs", responses={200:{"description":"Success"}, 404: {"description": "Not found"}})
def get_plugs():
    """
        Returns a list of all plugs and their states.
    """

    try:
        plugs = config.plugstates.items()
        return ORJSONResponse(content=jsonable_encoder(plugs), status_code=200)
    except Exception as e:
        logging.error(f"Plug Fetch Error:")
        logging.error(f"{traceback.format_exc()}")
        return ORJSONResponse(content=jsonable_encoder({"error":"Plugs not found"}), status_code=404)

@plug_router.get("/plug", responses={200:{"description":"Success"}, 404: {"description": "Not found"}})
def get_plug(plug_ip:str):
    """
        Returns the state of a specific plug.
    """
    try:
        plug = config.plugstates[plug_ip]
        return ORJSONResponse(content=jsonable_encoder(plug), status_code=200)
    except Exception as e:
        logging.error(f"Plug Fetch Error:")
        logging.error(f"{traceback.format_exc()}")
        return ORJSONResponse(content=jsonable_encoder({"error":"Plug not found"}), status_code=404)


@plug_router.get("/toggle_plug", responses={200:{"description":"Success"}, 404:{"description":"Plug not found"}, 503: {"description": "Server error"}})
def toggle_plug(plug_ip: str, plug_retAdr: int):
    """
        Toggles a specific plug.
    """
    try:
        if plug_ip in config.plugstates:
            config.toggleclients.append((plug_ip, plug_retAdr))
            return ORJSONResponse(content=jsonable_encoder({"message":"Toggle command sent"}), status_code=200)
        else:
            return ORJSONResponse(content=jsonable_encoder({"error":"Plug not found"}), status_code=404)

            
        
    except Exception as e:
        logging.error(f"Toggle Plug Error")
        logging.error(f"{traceback.format_exc()}")
        return ORJSONResponse(content=jsonable_encoder({"error":"Toggle Failed"}), status_code=503)