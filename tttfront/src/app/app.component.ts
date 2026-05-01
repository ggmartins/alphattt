import { CommonModule, isPlatformBrowser } from '@angular/common';
import { Component, Inject, OnDestroy, OnInit, PLATFORM_ID } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { WebsocketService } from './websocket.service';
import { SessionStatusComponent } from '../components/sessionstatus.component';
import { MatchStatus, SessionStatus } from '../components/sessionstatus.model';

import {
  TicTacToeBoardComponent,
  TicTacToeBoard,
  TicTacToeMoveEvent
} from '../components/tttboard.component';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [CommonModule, FormsModule, SessionStatusComponent, TicTacToeBoardComponent],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})

export class AppComponent implements OnInit, OnDestroy {
  login = '';
  message = '';
  player2 = '';
  sessions: SessionStatus[] = [];
  messages: string[] = [];
  connected = false;
  showBoard = false;

  board: TicTacToeBoard = [
    [null, null, null],
    [null, null, null],
    [null, null, null]
  ];
  playingAs: 'X' | 'O' = 'X';
  playerId = 0;
  sessionid = '0';

  constructor(
    private websocketService: WebsocketService,
    @Inject(PLATFORM_ID) private platformId: object
  ) {}

  ngOnInit(): void {
    if (!isPlatformBrowser(this.platformId)) {
      return;
    }

    this.websocketService.connect(
      (message: string) => {
        this.recvMessage(message);
      },
      () => {
        this.connected = true;
      },
      () => {
        this.connected = false;
      },
      () => {
        this.connected = false;
      }
    );
  }

  launchBoard(): void {
    this.showBoard = true;
  }

  closeBoard(): void {
    this.showBoard = false;
  }

  onMove(event: TicTacToeMoveEvent): void {
    console.log('Move clicked:', event);
    //this.board[event.row][event.col] = this.playingAs;
    //console.log('Updated board:', this.board);
    this.websocketService.sendMessage(
      JSON.stringify({
        command: 'move',
        session_id: event.sessionid,
        player: event.player,
        player_id: this.playerId,
        row: event.row,
        col: event.col,
        board: event.board
      })
    );
  }
  command_login(result: Record<string, any>) {
    if (result['error']) {
      this.messages.push(`Login error: ${result['error_message']}`);
      return;
    }

    if (result['data']) {
      (result['data'] as any[]).forEach(element => {
        const session = this.toSessionStatus(element);
        console.log('Adding session:', session);
        this.sessions.push(session);
        if (this.playerId == 0) {
          this.playerId = session.playerId;
        }
      });
    }
  }

  onLaunchMatch(sessionId: number): void {
    this.websocketService.sendMessage(
      JSON.stringify({ command: 'launch', session_id: sessionId })
    );
    console.log(`Launching match for session: ${sessionId}`)

    const session = this.sessions.find(s => s.sessionId === sessionId);
    if (session) {
      this.sessionid = String(session.sessionId);
      const sessionBoard = (session.board as any).board;
      this.board = sessionBoard;
      this.playingAs = session.playingAs;
      this.playerId = session.playerId;
      console.log(`Playing as: ${this.playingAs}`)
    }

    this.launchBoard();
  }

  private toSessionStatus(data: Record<string, any>): SessionStatus {
    return {
      sessionId: Number(data['sessionId'] ?? data['session_id']),
      vsplayer: data['vsplayer'],
      playerId: Number(data['player_id']),
      timestamp: data['last_move'],
      board: data['board'] ?? [[null, null, null], [null, null, null], [null, null, null]],
      status: this.toMatchStatus(data['status']),
      playingAs: data['playing_as']
    };
  }

  private toMatchStatus(status: unknown): MatchStatus {
    if (status === true) {
      return 'finished';
    }

    if (status === 'finished' || status === 'ongoing' || status === 'not_launched') {
      return status;
    }

    return 'not_launched';
  }

  recvMessage(message: string) {
    this.messages.push(message);
    console.log(`Received message: [${message}]`);

    try {
        const data = JSON.parse(message);
        switch (data['command']) {
            case 'login':
              this.messages.push(`Login result: ${data['result']}`);
              this.command_login(data['result']);
              break;
            case 'invite':
              this.messages.push(`Invite result: ${data['result']}`);
              break;
            case 'move':
              this.messages.push(`Move result: ${data['result']}`);
              if (data['error']) {
                alert(`Move error: ${data['error_message']}`);
              }
              break;
            case 'launch':
              this.messages.push(`Launch received.`);
              break;
            default:
              console.log(`Message: ${message}`);
              return;
        }  
    }
    catch(e)
    {
        console.log(`recvMessage: Error parsing message: ${e}`);
        return;
    }
  }

  sendMessage(): void {
    const trimmed = this.message.trim();

    if (!trimmed) {
      return;
    }

    this.websocketService.sendMessage(trimmed);
    this.message = '';
  }

  sendLogin(): void {
    const trimmed = this.login.trim();

    if (!trimmed) {
      return;
    }

    this.websocketService.sendMessage(`{ "command": "login", "username": "${trimmed}" }`);
  }

  sendInvite(): void {
    const trimmed = this.player2.trim();

    if (!trimmed) {
      return;
    }

    this.websocketService.sendMessage(`{ "command": "invite", "username": "${trimmed}" }`);
  }

  ngOnDestroy(): void {
    if (isPlatformBrowser(this.platformId)) {
      this.websocketService.disconnect();
    }
  }
}
