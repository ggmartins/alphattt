import { CommonModule } from '@angular/common';
import { Component, EventEmitter, Input, Output } from '@angular/core';

export type TicTacToeCell = 'X' | 'O' | null;
export type TicTacToeBoard = TicTacToeCell[][];

export interface TicTacToeMoveEvent {
  sessionid: string;
  player: 'X' | 'O';
  row: number;
  col: number;
  board: TicTacToeBoard;
}

@Component({
  selector: 'app-tic-tac-toe-board',
  standalone: true,
  imports: [CommonModule],
  templateUrl: './tttboard.component.html',
  styleUrls: ['./tttboard.component.css']
})
export class TicTacToeBoardComponent {
  @Input() board: TicTacToeBoard = [
    [null, null, null],
    [null, null, null],
    [null, null, null]
  ];

  @Input() player: 'X' | 'O' = 'X';

  @Input() sessionid = '';

  @Input() turn: 'X' | 'O' = 'X';

  /**
   * When true, the board launches over the entire browser screen.
   */
  @Input() fullscreen = false;

  /**
   * Optional: block all clicks if the game is finished.
   */
  @Input() disabled = false;

  @Output() move = new EventEmitter<TicTacToeMoveEvent>();

  @Output() close = new EventEmitter<void>();

  onCellClick(row: number, col: number): void {
    if (this.disabled) {
      return;
    }

    if (!this.board?.[row]) {
      return;
    }

    const currentValue = this.board[row][col];

    /**
     * Only allow playing on empty cells.
     * Since this component is configured with player="X",
     * every valid local move becomes X.
     */
    if (currentValue !== null) {
      return;
    }

    const nextBoard = this.cloneBoard(this.board);
    nextBoard[row][col] = this.player;

    this.move.emit({
      sessionid: this.sessionid,
      player: this.player,
      row,
      col,
      board: nextBoard
    });
  }

  onClose(): void {
    this.close.emit();
  }

  trackByRow(index: number): number {
    return index;
  }

  trackByCol(index: number): number {
    return index;
  }

  private cloneBoard(board: TicTacToeBoard): TicTacToeBoard {
    return board.map(row => [...row]);
  }
}
