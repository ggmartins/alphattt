import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { WebsocketService } from './websocket.service';
import { SessionStatus } from '../components/sessionstatus.model';

@Component({
  selector: 'app-root',
  standalone: true,
  imports: [FormsModule],
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

  constructor(private websocketService: WebsocketService) {}

  ngOnInit(): void {
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
      this.messages.push(`Login error: ${result['error']}`);
      return;
    }

    this.sessions = result['data'];
  }

  recvMessage(message: string) {
    this.messages.push(message);
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
    this.websocketService.disconnect();
  }
}

