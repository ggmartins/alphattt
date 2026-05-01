from __future__ import annotations
from db.models import Players, Status, Sessions
from utils import singleton
import json
from sqlalchemy import select, or_
from sqlmodel import Session, create_engine

#### DB API ####

class SessionStatus:
    _status_board : dict
    _session_vsplayer: str
    _session_id: int
    _session_status: str

    def __init__(self, vsplayer: str, session_id: int, session_status: str, board: dict):
        self._status_board = board
        self._session_vsplayer = vsplayer
        self._session_id = session_id
        self._session_status = session_status
    
    def to_dict(self) -> dict:
        return {
            'board': self._status_board,
            'vsplayer': self._session_vsplayer,
            'session_id': self._session_id,
            'status': self._session_status
        }


@singleton
class DB:

    ### Singleton pattern
    def __init__(self, connection_string: str):
        print("Initializing DB...")
        self.engine = create_engine(connection_string)

    def get_session(self):
        return Session(self.engine)

    # Get Sessions filtered by login userid
    def get_user_sessions(self, username: str) -> list[Sessions]:
        print(f"Looking for user sessions for: {username}")

        with Session(self.engine) as sessionsql:
            playerid = sessionsql.exec(
                    select(Players.PlayerID).where(Players.PlayerName == username)
                ).first()[0]
            statement = select(Sessions).where( or_(
                Sessions.Player1ID == playerid,
                Sessions.Player2ID == playerid,
            ))
            statement.compile(
                dialect=self.engine.dialect,
                compile_kwargs={"literal_binds": True}
            )
            sessions = sessionsql.exec(statement)

            results = []
            for session in sessions:
                print(f"Session found: {session[0]}")
                results.append(self.get_sessionstatus(playerid, session[0])
                                   .to_dict())

            result=json.dumps(results, indent=4)
            return result

    def get_sessionstatus(self, playerid: int, session: Sessions) -> SessionStatus:
        ss : SessionStatus

        vsplayer = session.Player1ID

        if session.Player1ID == playerid:
            vsplayer = session.Player2ID

        with Session(self.engine) as sessionsql:
            status = sessionsql.get(Status, session.StatusID)
            ss = SessionStatus(
                vsplayer,
                session.SessionID,
                session.IsFinished,
                status.Data
            )
            return ss
            


            
            

