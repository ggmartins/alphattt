import logging
from datetime import datetime
from typing import Annotated, Literal

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

def validate_login_message(message: str) -> tuple[bool, LoginResponse]:
    """
    Validate the login message and return a tuple of (is_valid, response).
    If the message is valid, is_valid will be True and response will be a LoginSuccess object.
    If the message is invalid, is_valid will be False and response will be a LoginFailure object with an error message. 

    Returns:
        tuple[bool, LoginResponse]: A tuple containing a boolean indicating if the message is valid
        and a LoginResponse object (either LoginSuccess or LoginFailure).
    """
    try:
        if isinstance(message, str):
            request = LoginRequest.model_validate_json(message)
        else:
            request = LoginRequest.model_validate(message)

    except ValidationError as ve:
        return False, LoginFailure(
            command="login",
            error=True,
            message=f"(Validation error, {ve})"
        ).model_dump(mode="json")
    
    return True, LoginSuccess(
        command="login",
        error=False,
        message="Login Request validated.",
        result=LoginResult(data=[])
    ).model_dump(mode="json")


def validate_logout_message(message: str) -> tuple[bool, LogoutRequest | dict]:
    """
    Validate the logout message and return a tuple of (is_valid, response).
    If the message is valid, is_valid will be True and response will be a LogoutRequest object.
    If the message is invalid, is_valid will be False and response will be a dict with an error message. 

    Returns:
        tuple[bool, LogoutRequest | dict]: A tuple containing a boolean indicating if the message is valid
        and a LogoutRequest object or a dict with an error message.
    """
    try:
        if isinstance(message, str):
            request = LogoutRequest.model_validate_json(message)
        else:
            request = LogoutRequest.model_validate(message)

    except ValidationError as ve:
        return False, {
            "command": "logout",
            "error": True,
            "message": f"(Validation error, {ve})"
        }
    
    return True, request