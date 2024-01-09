from pydantic import BaseModel

class plug(BaseModel):
    ip: str
    name: str
    retAdr: int
    state: int
        
    def __eq__(self, other):
        if isinstance(other, plug):
            return self.ip == other.ip
        elif isinstance(other, str):
            return self.ip == other

plugstates = {} # Dictionary of connected plugs
toggleclients = [] # List of plugs that have a toggle command pending