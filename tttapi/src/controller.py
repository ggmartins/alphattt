import sys
import traceback
import logging
from utils import singleton
from db.db import DB
from apimodels import LoginRequest, LogoutRequest, validate_message
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
        request, validation_error = validate_message(message, LoginRequest)
        if validation_error:
            logger.warning(
                "Login request rejected: %s",
                validation_error.get("message", "validation failed"),
                extra={"event": "login_validation_failed"},
            )
            return validation_error

        assert request is not None

        try:
            ok, resultdata = self._db.get_user_sessions(request.username)
            if not ok:
                return {
                    'command': 'login',
                    'error': True,
                    'message': f"No sessions found for user {request.username}.",
                }

            return {
                'command': 'login',
                'error': False,
                'message': f"User {request.username} logged in successfully.",
                'result': {'data': resultdata},
            }
        except Exception as e:
            logger.error(
                "ERROR: Exception command_login: %s",
                f"{type(e).__name__}: {e}",
                extra={"event": "login_exception"},
            )
            traceback.print_exc()
            return {
                'command': 'login',
                'error': True,
                'message': str(e),
            }

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
        request, validation_error = validate_message(message, LogoutRequest)
        if validation_error:
            logger.warning(
                "Logout request rejected: %s",
                validation_error.get("message", "validation failed"),
                extra={"event": "logout_validation_failed"},
            )
            return validation_error

        assert request is not None
        logger.info(f"Logout command received: %s.", str(message), extra={"event": "logout_command_received"})
        return { 'command': request.command, 'error': False, 'message': 'Goodbye' }

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
