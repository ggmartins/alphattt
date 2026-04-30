from __future__ import annotations
from db.models import Players, Status, Sessions
from utils import singleton
from sqlmodel import Session, create_engine
#### DB API ####

@singleton
class DB:

    ### Singleton pattern
    def __init__(self, connection_string: str):
        self.engine = create_engine(connection_string)

    def get_session(self):
        return Session(self.engine)