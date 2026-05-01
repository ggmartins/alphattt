export type MatchStatus = 'finished' | 'ongoing' | 'not_launched';

export interface SessionStatus {
  sessionId: number;
  vsplayer: String;
  playerId: number;
  timestamp: Date;
  board: [ [null, null, null], [null, null, null], [null, null, null] ];
  playingAs: 'X' | 'O';
  status: MatchStatus;
}