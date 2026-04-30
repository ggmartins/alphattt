DROP DATABASE IF EXISTS tttdb;
CREATE DATABASE tttdb;
USE tttdb;

CREATE TABLE Players (
    PlayerID INT PRIMARY KEY,
    PlayerName VARCHAR(100) NULL
);

CREATE TABLE Status (
    StatusID INT PRIMARY KEY,
    Data JSON,
    TS timestamp NOT NULL,
    SessionID INT NULL,
    MoveCount INT NOT NULL DEFAULT 0
);

CREATE TABLE Sessions (
    SessionID INT PRIMARY KEY,
    Player1ID INT NOT NULL,
    Player2ID INT NOT NULL,
    Multiplay BOOLEAN NOT NULL DEFAULT FALSE,
    NextTurn INT NOT NULL,
    BoardSize INT NOT NULL DEFAULT 3,
    StatusID INT NOT NULL,
    IsFinished BOOLEAN NULL,
 
    FOREIGN KEY (Player1ID) REFERENCES Players(PlayerID),
    FOREIGN KEY (Player2ID) REFERENCES Players(PlayerID),
    FOREIGN KEY (NextTurn) REFERENCES Players(PlayerID),
    FOREIGN KEY (StatusID) REFERENCES Status(StatusID)
);


