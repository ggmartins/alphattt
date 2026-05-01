from utils import singleton
from db.db import DB
import json

@singleton
class Controller:

    _db : DB = None

    def __init__(self, db: DB):
        self._db = db
    
    async def command_login(self, message: str) :
        print(f"Login command received: {message}. DB")
        result = self._db.get_user_sessions(message['username'])
        return result

    async def handle_websocket_message(self, message: str):
        commands = {
            'login': self.command_login,
        }

        # Use pydantic to enforce schema

        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            print("Message received.")
            return

        command = commands.get(data.get("command"), lambda: "Invalid command")

        print(f"Calling function: [{data.get('command')}]")
        
        return await command(data)

