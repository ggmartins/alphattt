from __future__ import annotations
from datetime import datetime
from db.models import Players, Status, Sessions
from utils import singleton
import json
from sqlalchemy import func, select, or_
from sqlmodel import Session, create_engine

#### DB API ####

class SessionStatus:
    _status_board : dict
    _session_vsplayer: str
    _player_id: int
    _session_id: int
    _session_status: str
    _status_date: str
    _playing_as: str
    _next_turn: str

    def __init__(self, vsplayer: str, player_id: int, session_id: int,
                 session_status: str,
                 board: dict,
                 status_date: str,
                 playing_as: str,
                 next_turn: str):
        self._status_board = board
        self._session_vsplayer = vsplayer
        self._player_id = player_id
        self._session_id = session_id
        self._session_status = session_status
        self._status_date = status_date
        self._playing_as = playing_as
        self._next_turn = next_turn

    def to_dict(self) -> dict:
        return {
            'board': self._status_board,
            'vsplayer': self._session_vsplayer,
            'player_id': self._player_id,
            'session_id': self._session_id,
            'status': self._session_status,
            'last_move': self._status_date,
            'playing_as': self._playing_as,
            'next_turn': self._next_turn
        }

@singleton
class DB:

    ### Singleton pattern
    def __init__(self, connection_string: str):
        print("Initializing DB...")
        self.engine = create_engine(connection_string)

    def get_session(self):
        return Session(self.engine)
    
    def validate_move(self, data, next_turn: str,
                                        player_id: int,
                                        col:int, row: int) -> tuple[bool, str | None, int]:
        print(
            f"Validating move: {data}, Next turn: {next_turn}, Player ID: {player_id}, Column: {col}, Row: {row}"
        )
        if next_turn != player_id:
            print("Not your turn.")
            return False, "Not your turn.", -1

        if data['board'][row][col] is not None:
            print("Position already occupied.")
            return False, "Position already occupied.", -1
        
        for i in range(len(data['board'])):
            if data['board'][i][0]=='X' and data['board'][i][1]=='X' and data['board'][i][2]=='X':
                return True, "Game Over", player_id
                
        for i in range(len(data['board'])):
            if data['board'][i][0]=='O' and data['board'][i][1]=='O' and data['board'][i][2]=='O':
                return True, "Game Over", player_id     

        for i in range(len(data['board'])):
            if data['board'][0][i]=='X' and data['board'][1][i]=='X' and data['board'][2][i]=='X':
                return True, "Game Over", player_id  

        for i in range(len(data['board'])):
            if data['board'][0][i]=='O' and data['board'][1][i]=='O' and data['board'][2][i]=='O':
                return True, "Game Over", player_id  

        if data['board'][0][0]=='X' and data['board'][1][1]=='X' and data['board'][2][2]=='X':
                return True, "Game Over", player_id 

        if data['board'][0][0]=='O' and data['board'][1][1]=='O' and data['board'][2][2]=='O':
                return True, "Game Over", player_id 


        return True, None, -1

    def move_user(self, message: dict) -> tuple[bool, str | None, dict | None]:
        print(f"Moving user: {message}")

        with Session(self.engine) as sessionsql:
            statement = select(Sessions).where(Sessions.SessionID == message['session_id'])
            row = sessionsql.exec(statement).first()
            session = row[0] if row else None

            if not session:
                print(f"Session {message['session_id']} not found.")
                return False, f"Session {message['session_id']} not found.", None

            # Update status
            print(f">>>Updating status for session: {session.SessionID}")
            status = sessionsql.get(Status, session.StatusID)
            if not status:
                print(f"Status {session.StatusID} not found.")
                return False, f"Status {session.StatusID} not found.", None

            ok, msg, winner = self.validate_move(
                data=status.Data,
                next_turn=session.NextTurn,
                player_id=message['player_id'],
                col=message['col'],
                row=message['row']
            )

            if not ok:
                print(f"Move validation failed: {msg}")
                return ok, msg, None
            
            print(f"OLD DATA: {status.Data['board']}")
            player_as = "X" if session.Player1ID == message['player_id'] else "O"
            move_count = status.MoveCount + 1
            board = [row[:] for row in status.Data['board']]
            board[message['row']][message['col']] = player_as
            print(f"NEW DATA: {board}")

            max_status_id_row = sessionsql.exec(select(func.max(Status.StatusID))).first()
            max_status_id = max_status_id_row[0] if max_status_id_row else 0
            new_status_id = (max_status_id or 0) + 1
            new_status_data = {
                **status.Data,
                'board': board,
                'lastMove': {
                    'playerId': message['player_id'],
                    'row': message['row'],
                    'col': message['col']
                },
                'winner': winner if winner != -1 else status.Data.get('winner')
            }
            new_status = Status(
                StatusID=new_status_id,
                Data=new_status_data,
                MoveCount=move_count,
                SessionID=session.SessionID,
                TS=datetime.now()
            )
            sessionsql.add(new_status)
            sessionsql.flush()

            # Update session
            session.NextTurn = session.Player2ID if session.NextTurn == session.Player1ID else session.Player1ID
            session.StatusID = new_status.StatusID
            sessionsql.add(session)
            sessionsql.commit()

        return True, None, new_status_data


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
                results.append(self.get_sessionstatus(playerid, username, session[0])
                                   .to_dict())

            return results

    def get_sessionstatus(self, playerid: int, username: str, session: Sessions) -> SessionStatus:
        ss : SessionStatus

        with Session(self.engine) as sessionsql:
            playing_as = "X" if session.Player1ID == playerid else "O"
            opponent_as = "O" if session.Player1ID == playerid else "X"
            opponentid = session.Player2ID if session.Player1ID == playerid else session.Player1ID
            player_id = session.Player1ID if session.Player1ID == playerid else session.Player2ID
            vsplayer = sessionsql.exec(select(Players.PlayerName).where(Players.PlayerID == opponentid)).first()[0]
            next_turn = f"{username}:{playing_as}"
            if session.NextTurn != playerid:
                next_turn = f"{vsplayer}:{opponent_as}"

            status = sessionsql.get(Status, session.StatusID)
            ss = SessionStatus(
                vsplayer,
                player_id,
                session.SessionID,
                session.IsFinished,
                status.Data,
                str(status.TS),
                playing_as,
                next_turn
            )
            return ss
            


            
            
