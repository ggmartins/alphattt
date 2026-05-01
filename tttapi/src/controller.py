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
            print(f"Excaption command_login: {e}")
            result['error'] = True
            result['error_message'] = str(e)

        result['result'] = { 'data': data }
        return result
    
    async def command_launch(self, message: str) -> dict | None:
        result = { 'command': 'launch', 'error': False, 'error_message': None }
        print(f"Launch command received: {message}.")
        return 

    async def handle_websocket_message(self, message: str) -> dict | None:
        commands = {
            'login': self.command_login,
            'launch': self.command_launch
        }

        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print("Message received.")
            return

        command = commands.get(data.get("command"), lambda: "Invalid command")

        print(f"Calling function: [{data.get('command')}]")
        
        return await command(data)

