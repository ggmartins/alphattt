import { Component, OnDestroy, OnInit } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { WebsocketService } from './websocket.service';

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
  sessions: string[] = [];
  messages: string[] = [];
  connected = false;

  constructor(private websocketService: WebsocketService) {}

  ngOnInit(): void {
    this.websocketService.connect(
      (message: string) => {
        this.messages.push(message);
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


/*
import { Component } from '@angular/core';
import { RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-root',
  imports: [RouterOutlet],
  templateUrl: './app.component.html',
  styleUrl: './app.component.css'
})
export class AppComponent {
  title = 'tttfront';
}
*/