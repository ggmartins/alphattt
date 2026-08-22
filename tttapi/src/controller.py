import sys
import traceback
import logging
from utils import singleton
from db.db import DB
from apimodels import validate_login_message, validate_logout_message
import json

logging.basicConfig(
    level=logging.INFO,
    stream=sys.stdout,
    format=(
        "%(asctime)s %(levelname)s %(name)s "
        "event=%(event)s %(message)s"
    ),
)

logger = logging.getLogger(__name__)

@singleton
class Controller:

    _db : DB = None

    def __init__(self, db: DB):
        self._db = db
    
    async def command_login(self, message: dict) -> dict | None:
        result = { 'command': 'login', 'error': False, 'message': None }

        is_valid, validated_message = validate_login_message(message)
        if not is_valid:
            logger.warning(
                "Login request rejected: %s",
                validated_message.get("message", "validation failed"),
                extra={"event": "login_validation_failed"},
            )
            return validated_message

        try:
            ok, resultdata = self._db.get_user_sessions(message['username'])
            if not ok:
                validated_message['error'] = True
                validated_message['message'] = f"No sessions found for user {message['username']}."
            else:
                validated_message['message'] = f"User {message['username']} logged in successfully."
                validated_message['result'] = { 'data': resultdata }
        except Exception as e:
            logger.error(
                "ERROR: Exception command_login: %s",
                f"{type(e).__name__}: {e}",
                extra={"event": "login_exception"},
            )
            traceback.print_exc()
            validated_message['error'] = True
            validated_message['message'] = str(e)

        return validated_message

    async def command_launch(self, message: dict) -> dict | None:
        result = { 'command': 'launch', 'error': False, 'message': None }
        print(f"Launch command received: {str(message)}.")
        return result
    
    async def command_move(self, message: dict) -> dict | None:
        result = { 'command': 'move', 'error': False, 'message': None }
        try:
            ok, msg, data = self._db.move_user(message)
        except Exception as e:
            print(f"Exception command_move: {type(e).__name__}: {e}")
            traceback.print_exc()
            result['error'] = True
            result['message'] = str(e)
            return result

        if not ok:
            result['error'] = True
            result['message'] = msg

        result['result'] = { 'data': data }
        return result
    
    async def command_logout(self, message: dict) -> dict | None:
        result = { 'command': 'logout', 'error': False, 'message': 'Goodbye' }

        is_valid, validated_message = validate_logout_message(message)
        if not is_valid:
            logger.warning(
                "Logout request rejected: %s",
                validated_message.get("message", "validation failed"),
                extra={"event": "logout_validation_failed"},
            )
            return validated_message
        logger.info(f"Logout command received: %s.", str(message), extra={"event": "logout_command_received"})
        return result

    async def handle_websocket_message(self, message: str, source_ip: str,
                                                           source_port: int) -> tuple[dict | None, bool]:
        commands = {
            'login': self.command_login,
            'logout': self.command_logout,
            'launch': self.command_launch,
            'move': self.command_move
        }

        try:
            data = json.loads(message)
        except json.JSONDecodeError:
            logger.warning(
                "Invalid JSON message received from %s:%s: %s",
                source_ip,
                source_port,
                message,
                extra={"event": "websocket_invalid_json"},
            )
            return

        command = commands.get(data.get("command"), lambda: "Invalid command")

        logger.info(f"Calling function: [%s] from %s:%s", data.get('command'),
                    source_ip, source_port,
                    extra={"event": "websocket_command_call"})
        
        if data.get("command") == "logout":
            return await command(data), True 
        
        return await command(data), False
