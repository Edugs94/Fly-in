from pydantic import BaseModel
from src.schemas.hubs import Hub, StartHub, EndHub
from src.schemas.connection import Connection


class SimulationMap(BaseModel):
    '''Map class with map file settings'''
    nb_drones: int

    start_hub: StartHub | None
    end_hub: EndHub | None

    hubs: dict[str, Hub]
    connections: list[Connection]
