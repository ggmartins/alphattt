export type MatchStatus = 'finished' | 'ongoing' | 'not_launched';

export interface PlayerInfo {
  playerId: number;
  playerName: string;
}

export interface SessionStatus {
  sessionId: number;
  vsplayer: PlayerInfo;
  timestamp: Date;
  status: MatchStatus;
}