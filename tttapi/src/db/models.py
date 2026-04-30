from __future__ import annotations
from datetime import datetime
from typing import Optional, Any
from sqlalchemy import Column, JSON, TIMESTAMP, text
from sqlmodel import Field, SQLModel

#### Models ####

class Players(SQLModel, table=True):
    __tablename__ = "Players"
    PlayerID: int = Field(primary_key=True)
    PlayerName: Optional[str] = Field(default=None, max_length=100)

class Status(SQLModel, table=True):
    __tablename__ = "Status"
    StatusID: int = Field(primary_key=True)
    # MySQL JSON column
    Data: Optional[dict[str, Any]] = Field(
        default=None,
        sa_column=Column(JSON)
    )
    # MySQL TIMESTAMP NOT NULL
    TS: datetime = Field(
        sa_column=Column(
            TIMESTAMP,
            nullable=False,
            server_default=text("CURRENT_TIMESTAMP"),
        )
    )
    # In your SQL this is nullable
    SessionID: Optional[int] = Field(default=None, foreign_key="Sessions.SessionID")
    MoveCount: int = Field(default=0, nullable=False)

class Sessions(SQLModel, table=True):
    __tablename__ = "Sessions"
    SessionID: int = Field(primary_key=True)
    Player1ID: int = Field(foreign_key="Players.PlayerID", nullable=False)
    Player2ID: int = Field(foreign_key="Players.PlayerID", nullable=False)
    Multiplay: bool = Field(default=False, nullable=False)
    NextTurn: int = Field(foreign_key="Players.PlayerID", nullable=False)
    BoardSize: int = Field(default=3, nullable=False)
    StatusID: int = Field(foreign_key="Status.StatusID", nullable=False)
    IsFinished: Optional[bool] = Field(default=None)

