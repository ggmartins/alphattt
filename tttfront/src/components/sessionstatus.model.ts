export type MatchStatus = 'finished' | 'ongoing' | 'not_launched';

export interface SessionStatus {
  sessionId: number;
  vsplayer: String;
  timestamp: Date;
  status: MatchStatus;
}