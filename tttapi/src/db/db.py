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
    _status_date: str

    def __init__(self, vsplayer: str, session_id: int, session_status: str, board: dict, status_date: str):
        self._status_board = board
        self._session_vsplayer = vsplayer
        self._session_id = session_id
        self._session_status = session_status
        self._status_date = status_date

    def to_dict(self) -> dict:
        return {
            'board': self._status_board,
            'vsplayer': self._session_vsplayer,
            'session_id': self._session_id,
            'status': self._session_status,
            'last_move': self._status_date
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
                )
            if playerid:
                playerid = playerid.first()[0]
            else:
                raise ValueError(f"Player {username} not found.")

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

            return results

    def get_sessionstatus(self, playerid: int, session: Sessions) -> SessionStatus:
        ss : SessionStatus

        with Session(self.engine) as sessionsql:
            opponentid = session.Player2ID if session.Player1ID == playerid else session.Player1ID
            vsplayer = sessionsql.exec(select(Players.PlayerName).where(Players.PlayerID == opponentid)).first()[0]
            status = sessionsql.get(Status, session.StatusID)
            ss = SessionStatus(
                vsplayer,
                session.SessionID,
                session.IsFinished,
                status.Data,
                str(status.TS)
            )
            return ss
            


            
            

