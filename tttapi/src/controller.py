import traceback
from utils import singleton
from db.db import DB
import json

@singleton
class Controller:

    _db : DB = None

    def __init__(self, db: DB):
        self._db = db
    
    async def command_login(self, message: str) -> dict | None:
        result = { 'command': 'login', 'error': False, 'error_message': None }
        print(f"Login command received: {message}.")

        data = ""
        try:
            data = self._db.get_user_sessions(message['username'])
        except Exception as e:
            print(f"Exception command_login: {e}")
            result['error'] = True
            result['error_message'] = str(e)

        result['result'] = { 'data': data }
        return result
    
    async def command_launch(self, message: str) -> dict | None:
        result = { 'command': 'launch', 'error': False, 'error_message': None }
        print(f"Launch command received: {message}.")
        return result
    
    async def command_move(self, message: str) -> dict | None:
        result = { 'command': 'move', 'error': False, 'error_message': None }
        try:
            ok, msg = self._db.move_user(message)
        except Exception as e:
            print(f"Exception command_move: {type(e).__name__}: {e}")
            traceback.print_exc()
            result['error'] = True
            result['error_message'] = str(e)
            return result

        if not ok:
            result['error'] = True
            result['error_message'] = msg

        return result

    async def handle_websocket_message(self, message: str) -> dict | None:
        commands = {
            'login': self.command_login,
            'launch': self.command_launch,
            'move': self.command_move
        }

        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print("Message received.")
            return

        command = commands.get(data.get("command"), lambda: "Invalid command")

        print(f"Calling function: [{data.get('command')}]")
        
        return await command(data)
