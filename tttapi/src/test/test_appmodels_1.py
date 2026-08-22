from apimodels import LoginRequest, LogoutRequest, validate_message

def test_valid_login_message_from_mapping() -> None:
    request, error = validate_message(
        {"command": "login", "username": "player.one"},
        LoginRequest,
    )

    assert error is None
    assert request is not None
    assert request.command == "login"
    assert request.username == "player.one"


def test_valid_login_message_from_json() -> None:
    request, error = validate_message(
        '{"command":"login","username":"player.two"}',
        LoginRequest,
    )

    assert error is None
    assert request is not None
    assert request.username == "player.two"


def test_login_requires_username() -> None:
    request, error = validate_message({"command": "login"}, LoginRequest)

    assert request is None
    assert error is not None
    assert error["command"] == "login"
    assert error["error"] is True
    assert "username" in error["message"]


def test_login_rejects_unexpected_fields() -> None:
    request, error = validate_message(
        {
            "command": "login",
            "username": "player.one",
            "admin": True,
        },
        LoginRequest,
    )

    assert request is None
    assert error is not None
    assert error["error"] is True
    assert "admin" in error["message"]

def test_valid_logout_message_from_mapping() -> None:
    request, error = validate_message({"command": "logout"}, LogoutRequest)

    assert error is None
    assert request is not None
    assert request.command == "logout"


def test_valid_logout_message_from_json() -> None:
    request, error = validate_message('{"command":"logout"}', LogoutRequest)

    assert error is None
    assert request is not None
    assert request.command == "logout"


def test_logout_rejects_wrong_command() -> None:
    request, error = validate_message({"command": "login"}, LogoutRequest)

    assert request is None
    assert error is not None
    assert error["command"] == "login"
    assert error["error"] is True


def test_logout_rejects_unexpected_fields() -> None:
    request, error = validate_message(
        {"command": "logout", "username": "player.one"},
        LogoutRequest,
    )

    assert request is None
    assert error is not None
    assert error["error"] is True
    assert "username" in error["message"]