from datetime import datetime
from typing import Annotated, Any, Literal, Mapping, TypeVar

from pydantic import (
    BaseModel,
    ConfigDict,
    StringConstraints,
    ValidationError,
)

class APIModel(BaseModel):
    model_config = ConfigDict(
        extra="forbid",  # Reject undeclared fields
        strict=True,     # Avoid automatic type coercion
        frozen=True,     # Prevent modification after validation
    )

Username = Annotated[
    str,
    StringConstraints(
        strip_whitespace=True,
        min_length=3,
        max_length=64,
        pattern=r"^[a-zA-Z0-9_.@-]+$",
    ),
]

class LoginRequest(APIModel):
    command: Literal["login"] = "login"
    username: Username

class SessionResponse(APIModel):
    session_id: int
    timestamp: datetime
    move_count: int
    status: Literal["ongoing", "finished"]

class LoginResult(APIModel):
    data: list[SessionResponse]

class LogoutRequest(APIModel):
    command: Literal["logout"] = "logout"

class LoginSuccess(APIModel):
    command: Literal["login"] = "login"
    error: Literal[False] = False
    message: str
    result: LoginResult

class LoginFailure(APIModel):
    command: Literal["login"] = "login"
    error: Literal[True] = True
    message: str

LoginResponse = LoginSuccess | LoginFailure

RequestModel = TypeVar("RequestModel", bound=APIModel)
Message = str | Mapping[str, Any]


def validate_message(
    message: Message,
    model: type[RequestModel],
) -> tuple[RequestModel | None, dict[str, Any] | None]:
    """Validate a WebSocket message against any API request model."""
    try:
        if isinstance(message, str):
            request = model.model_validate_json(message)
        else:
            request = model.model_validate(message)
    except ValidationError as error:
        command = message.get("command", "unknown") if not isinstance(message, str) else "unknown"
        return None, {
            "command": command,
            "error": True,
            "message": f"Validation error: {error}",
        }

    return request, None
