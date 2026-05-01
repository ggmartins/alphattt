import { Component, EventEmitter, Input, Output } from '@angular/core';
import { CommonModule, DatePipe, NgClass } from '@angular/common';
import { SessionStatus } from './sessionstatus.model';

@Component({
  selector: 'app-sessionstatus',
  standalone: true,
  imports: [CommonModule, DatePipe, NgClass],
  templateUrl: './sessionstatus.component.html',
  styleUrl: './sessionstatus.component.css',
})
export class SessionStatusComponent {
  @Input() session: SessionStatus = {
    sessionId: 1,
    vsplayer: {
      playerId: 1,
      playerName: 'Player 1',
    },
    timestamp: new Date(),
    status: 'not_launched',
  };

  @Output() launchMatch = new EventEmitter<number>();

  get statusLabel(): string {
    switch (this.session.status) {
      case 'finished':
        return 'Finished';
      case 'ongoing':
        return 'Ongoing';
      case 'not_launched':
        return 'Not Launched';
      default:
        return 'Unknown';
    }
  }

  get canLaunch(): boolean {
    return this.session.status === 'not_launched';
  }

  onLaunchClick(): void {
    if (!this.canLaunch) {
      return;
    }

    this.launchMatch.emit(this.session.sessionId);
  }
}