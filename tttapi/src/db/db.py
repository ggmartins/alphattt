from __future__ import annotations
import sys
import logging
from datetime import datetime
from db.models import Players, Status, Sessions
from utils import singleton
import json
from sqlalchemy import func, select, or_
from sqlmodel import Session, create_engine

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format=(
        "%(asctime)s %(levelname)s %(name)s "
        "event=%(event)s %(message)s"
    ),
)

logger = logging.getLogger(__name__)

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
        logger.info("Initializing DB...", extra={"event": "db_init"})
        self.engine = create_engine(connection_string)

    def get_session(self):
        return Session(self.engine)
    
    def validate_move(self, data, next_turn: str,
                                        player_id: int,
                                        col:int, row: int) -> tuple[bool, str | None, int]:
        logger.info(
            "Validating move: %s, Next turn: %s, Player ID: %s, Column: %s, Row: %s",
            data,
            next_turn,
            player_id,
            col,
            row,
            extra={"event": "move_validation"}
        )

        if data['board'][row][col] is not None:
            logger.debug("Position already occupied.", extra={"event": "move_position_occupied"})
            return False, "Position already occupied.", -1

        if next_turn != player_id:
            logger.debug("Not your turn.", extra={"event": "move_not_your_turn"})
            return False, "Not your turn.", -1

        return True, None, -1

    def determine_winner(self, board: list) -> str | None:
        winning_lines = [
            *board, #rows
            *zip(*board), #columns
            [board[0][0], board[1][1], board[2][2]], #diagonal 1
            [board[0][2], board[1][1], board[2][0]], #diagonal 2
        ]

        #check all the lines for a winner and return first element
        for line in winning_lines:
            if line[0] is not None and line[0] == line[1] == line[2]:
                return line[0]

        return None

    def get_session_and_players(self, session_id: int) -> tuple[bool, str | None, dict | None]:
        with Session(self.engine) as sessionsql:

            statement = select(Sessions).where(Sessions.SessionID == session_id)
            row = sessionsql.exec(statement).first()
            session = row[0] if row else None

            if not session:
                print(f"Session {session_id} not found.")
                return False, f"Session {session_id} not found.", None

            player1id_result = sessionsql.exec(
                    select(Players.PlayerName).where(Players.PlayerID == session.Player1ID)
                )
            player1id = player1id_result.one_or_none()
            if player1id is None:
                print(f"Player 1 with ID {session.Player1ID} not found.")
                return False, f"Player 1 with ID {session.Player1ID} not found.", None
            player1id = player1id[0] if player1id else None
            player2id_result = sessionsql.exec(
                    select(Players.PlayerName).where(Players.PlayerID == session.Player2ID)
                )
            player2id = player2id_result.one_or_none()
            player2id = player2id[0] if player2id else None
            if player2id is None:
                print(f"Player 2 with ID {session.Player2ID} not found.")
                return False, f"Player 2 with ID {session.Player2ID} not found.", None

            status = sessionsql.get(Status, session.StatusID)
            if not status:
                print(f"Status {session.StatusID} not found.")
                return False, f"Status {session.StatusID} not found.", None
            max_status_id_row = sessionsql.exec(select(func.max(Status.StatusID))).first()
            max_status_id = max_status_id_row[0] if max_status_id_row else 0
            new_status_id = (max_status_id or 0) + 1

            return True, None, {
                'session': session,
                'player1': player1id,
                'player2': player2id,
                'status': status,
                'new_status_id': new_status_id
            }

    def update_session(self, session_data: dict, move_count: int, next_turn: str,
                                                                  board: list,
                                                                  winner: int,
                                                                  player_id: int,
                                                                  row: str,
                                                                  col: str) -> tuple[bool, str | None, dict | None]:
        with Session(self.engine) as sessionsql:
            new_status_data = {
                **session_data['status'].Data,
                'board': board,
                'lastMove': {
                    'playerId': player_id,
                    'row': row,
                    'col': col
                },
                'next_turn': next_turn,
                'winner': winner if winner != -1 else session_data['status'].Data.get('winner')
            }
            new_status = Status(
                StatusID=session_data['new_status_id'],
                Data=new_status_data,
                MoveCount=move_count,
                SessionID=session_data['session'].SessionID,
                TS=datetime.now()
            )
            sessionsql.add(new_status)
            sessionsql.flush()

            # Update session
            session_data['session'].NextTurn = session_data['session'].Player2ID if session_data['session'].NextTurn == session_data['session'].Player1ID else session_data['session'].Player1ID
            session_data['session'].StatusID = new_status.StatusID
            sessionsql.add(session_data['session'])
            sessionsql.commit()
            return True, None, new_status_data

    def move_user(self, message: dict) -> tuple[bool, str | None, dict | None]:
        logger.info(f"Moving user: {str(message)}", extra={"event": "move_user"})

        ok, msg, session_data = self.get_session_and_players(message['session_id'])
        if not ok:
            return ok, msg, None

        ok, msg, winner = self.validate_move(
            data=session_data['status'].Data,
            next_turn=session_data['session'].NextTurn,
            player_id=message['player_id'],
            col=message['col'],
            row=message['row']
        )

        if not ok:
            logger.warning(f"Move validation failed: %s", msg, extra={"event": "move_validation_failed"})
            return ok, msg, None

        logger.info(f"OLD DATA: {session_data['status'].Data['board']}", extra={"event": "move_user"})
        player_as = "X" if session_data['session'].Player1ID == message['player_id'] else "O"
        opponent_as = "O" if session_data['session'].Player1ID == message['player_id'] else "X"
        move_count = session_data['status'].MoveCount + 1
        next_turn = session_data['player2'] + ":" + opponent_as \
            if session_data['session'].NextTurn == session_data['session'].Player1ID else session_data['player1'] + ":" + player_as
        board = [row[:] for row in session_data['status'].Data['board']]
        board[message['row']][message['col']] = player_as
        logger.info(f"NEW DATA: {board}", extra={"event": "move_user"})

        winner_mark = self.determine_winner(board)
        if winner_mark == "X":
            winner = session_data['session'].Player1ID
        elif winner_mark == "O":
            winner = session_data['session'].Player2ID

        if winner != -1:
            logger.info(f"Game Over: Player {winner} wins.", extra={"event": "game_over"})
            session_data['session'].IsFinished = True

        ok, msg, new_status_data = self.update_session(session_data, move_count,
                                                    next_turn,
                                                    board,
                                                    winner,
                                                    player_id=message['player_id'],
                                                    row=message['row'],
                                                    col=message['col'])

        if not ok:
            logger.warning(f"Move validation failed: {msg}")
            return ok, msg, None

        return True, None, new_status_data


    # Get Sessions filtered by login userid
    def get_user_sessions(self, username: str) -> tuple[bool, list[Sessions]]:
        logger.info(f"Looking for user sessions for: {username}", extra={"event": "get_user_sessions"})

        with Session(self.engine) as sessionsql:
            playerid_result = sessionsql.exec(
                    select(Players.PlayerID).
                        where(Players.PlayerName == username)
                )
            
            if playerid_result:
                playerid = playerid_result.scalars().one_or_none()
            else:
                raise ValueError(f"Player {username} not found.")

            logger.info(f"Player ID for {username}: {playerid}", extra={"event": "get_user_sessions"})

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
                results.append(self.get_sessionstatus(playerid, username, session[0])
                                   .to_dict())

            return (True,results) if len(results) > 0 else (False, results)

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
            


            
            
