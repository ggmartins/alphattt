import { isPlatformBrowser } from '@angular/common';
import { Component, Inject, OnDestroy, OnInit, PLATFORM_ID } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { WebsocketService } from './websocket.service';
import { SessionStatusComponent } from '../components/sessionstatus.component';
import { MatchStatus, SessionStatus } from '../components/sessionstatus.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule, SessionStatusComponent],
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
      });
    }
  }

  onLaunchMatch(sessionId: number): void {
    this.websocketService.sendMessage(
      JSON.stringify({ command: 'launch', session_id: sessionId })
    );
  }

  private toSessionStatus(data: Record<string, any>): SessionStatus {
    console.log(`LASTMOVE: ${data['last_move']}`)
    return {
      sessionId: Number(data['sessionId'] ?? data['session_id']),
      vsplayer: data['vsplayer'],
      timestamp: data['last_move'],
      status: this.toMatchStatus(data['status']),
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
    const data = JSON.parse(message);

    switch (data['command']) {
      case 'login':
        this.messages.push(`Login result: ${data['result']}`);
        this.command_login(data['result']);
        break;
      case 'invite':
        this.messages.push(`Invite result: ${data['result']}`);
        break;
      default:
        console.log(`Message: ${message}`);
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
