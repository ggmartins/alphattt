USE tttdb;


SET FOREIGN_KEY_CHECKS = 0;
TRUNCATE TABLE Players;
TRUNCATE TABLE Status;
TRUNCATE TABLE Sessions;
SET FOREIGN_KEY_CHECKS = 1;
-- -------------------------
-- Players
-- -------------------------
INSERT INTO Players (PlayerID, PlayerName) VALUES
(1, 'Alice'),
(2, 'Bob'),
(3, 'Carlos'),
(4, 'Diana'),
(5, 'Ethan'),
(6, 'Fernanda'),
(7, 'George'),
(8, 'Hannah');

-- -------------------------
-- Status
-- -------------------------
INSERT INTO Status (StatusID, Data, TS, SessionID, MoveCount) VALUES
(
    1,
    JSON_OBJECT(
        'board', JSON_ARRAY(
            JSON_ARRAY('X', 'O', 'X'),
            JSON_ARRAY(NULL, 'O', NULL),
            JSON_ARRAY(NULL, NULL, 'X')
        ),
        'winner', NULL,
        'lastMove', JSON_OBJECT('playerId', 1, 'row', 0, 'col', 2)
    ),
    '2026-04-30 10:00:00',
    1001,
    5
),
(
    2,
    JSON_OBJECT(
        'board', JSON_ARRAY(
            JSON_ARRAY('X', 'X', 'X'),
            JSON_ARRAY('O', 'O', NULL),
            JSON_ARRAY(NULL, NULL, NULL)
        ),
        'winner', 3,
        'lastMove', JSON_OBJECT('playerId', 3, 'row', 0, 'col', 2)
    ),
    '2026-04-30 10:15:00',
    1002,
    5
),
(
    3,
    JSON_OBJECT(
        'board', JSON_ARRAY(
            JSON_ARRAY('O', 'X', 'O'),
            JSON_ARRAY('X', 'O', 'X'),
            JSON_ARRAY('X', 'O', 'X')
        ),
        'winner', NULL,
        'result', 'draw',
        'lastMove', JSON_OBJECT('playerId', 6, 'row', 2, 'col', 2)
    ),
    '2026-04-30 10:30:00',
    1003,
    9
),
(
    4,
    JSON_OBJECT(
        'board', JSON_ARRAY(
            JSON_ARRAY('X', NULL, NULL),
            JSON_ARRAY(NULL, 'O', NULL),
            JSON_ARRAY(NULL, NULL, NULL)
        ),
        'winner', NULL,
        'lastMove', JSON_OBJECT('playerId', 8, 'row', 1, 'col', 1)
    ),
    '2026-04-30 11:00:00',
    1004,
    2
),
(
    5,
    JSON_OBJECT(
        'boardSize', 4,
        'board', JSON_ARRAY(
            JSON_ARRAY('X', 'O', NULL, NULL),
            JSON_ARRAY(NULL, 'X', NULL, NULL),
            JSON_ARRAY(NULL, NULL, 'O', NULL),
            JSON_ARRAY(NULL, NULL, NULL, NULL)
        ),
        'winner', NULL,
        'lastMove', JSON_OBJECT('playerId', 2, 'row', 2, 'col', 2)
    ),
    '2026-04-30 11:30:00',
    1005,
    4
);

-- -------------------------
-- Sessions
-- -------------------------
INSERT INTO Sessions (
    SessionID,
    Player1ID,
    Player2ID,
    Multiplay,
    NextTurn,
    BoardSize,
    StatusID,
    IsFinished
) VALUES
(
    1001,
    1,
    2,
    TRUE,
    2,
    3,
    1,
    FALSE
),
(
    1002,
    3,
    4,
    TRUE,
    4,
    3,
    2,
    TRUE
),
(
    1003,
    5,
    6,
    TRUE,
    5,
    3,
    3,
    TRUE
),
(
    1004,
    7,
    8,
    TRUE,
    7,
    3,
    4,
    FALSE
),
(
    1005,
    1,
    2,
    FALSE,
    1,
    4,
    5,
    FALSE
);

