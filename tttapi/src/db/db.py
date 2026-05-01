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

    def __init__(self, vsplayer: str, player_id: int, session_id: int,
                 session_status: str,
                 board: dict,
                 status_date: str,
                 playing_as: str):
        self._status_board = board
        self._session_vsplayer = vsplayer
        self._player_id = player_id
        self._session_id = session_id
        self._session_status = session_status
        self._status_date = status_date
        self._playing_as = playing_as

    def to_dict(self) -> dict:
        return {
            'board': self._status_board,
            'vsplayer': self._session_vsplayer,
            'player_id': self._player_id,
            'session_id': self._session_id,
            'status': self._session_status,
            'last_move': self._status_date,
            'playing_as': self._playing_as
        }


@singleton
class DB:

    ### Singleton pattern
    def __init__(self, connection_string: str):
        print("Initializing DB...")
        self.engine = create_engine(connection_string)

    def get_session(self):
        return Session(self.engine)
    
    def validate_move(self, data: list, next_turn: str,
                                        player_id: int,
                                        col:int, row: int) -> tuple[bool, str]:
        print(
            f"Validating move: {data}, Next turn: {next_turn}, Player ID: {player_id}, Column: {col}, Row: {row}"
        )
        if next_turn != player_id:
            print("Not your turn.")
            return False, "Not your turn."

        return True, ""

    def move_user(self, message: dict) -> bool:
        print(f"Moving user: {message}")

        with Session(self.engine) as sessionsql:
            statement = select(Sessions).where(Sessions.SessionID == message['session_id'])
            session = sessionsql.exec(statement).first()[0]
            if not session:
                print(f"Session {message['session_id']} not found.")
                return False

            # Update status
            print(f">>>Updating status for session: {session.SessionID}")
            status = sessionsql.get(Status, session.StatusID)
            #status.Data = json.loads(message['board'])

            (ok, msg) = self.validate_move(
                data=status.Data,
                next_turn=session.NextTurn,
                player_id=message['player_id'],
                col=message['col'],
                row=message['row']
            )
            if not ok:
                print(f"Move validation failed: {msg}")
                return ok, msg
            status.MoveCount += 1
            sessionsql.add(status)
            sessionsql.commit()

            # Update session
            session.NextTurn = session.Player2ID if session.NextTurn == session.Player1ID else session.Player1ID
            sessionsql.add(session)
            sessionsql.commit()

        return True


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
            player_id = session.Player1ID if session.Player1ID == playerid else session.Player2ID
            vsplayer = sessionsql.exec(select(Players.PlayerName).where(Players.PlayerID == opponentid)).first()[0]
            status = sessionsql.get(Status, session.StatusID)
            ss = SessionStatus(
                vsplayer,
                player_id,
                session.SessionID,
                session.IsFinished,
                status.Data,
                str(status.TS),
                "X" if session.Player1ID == playerid else "O"
            )
            return ss
            


            
            

