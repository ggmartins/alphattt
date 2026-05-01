import { ComponentFixture, TestBed } from '@angular/core/testing';
import { TicTacToeBoardComponent } from './tttboard.component';

describe('TicTacToeBoardComponent', () => {
  let component: TicTacToeBoardComponent;
  let fixture: ComponentFixture<TicTacToeBoardComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [TicTacToeBoardComponent]
    }).compileComponents();

    fixture = TestBed.createComponent(TicTacToeBoardComponent);
    component = fixture.componentInstance;

    component.sessionid = '1005';
    component.player = 'X';
    component.board = [
      ['X', 'O', 'X'],
      [null, 'O', null],
      [null, null, 'X']
    ];

    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should emit move when clicking an empty cell', () => {
    spyOn(component.move, 'emit');

    component.onCellClick(1, 0);

    expect(component.move.emit).toHaveBeenCalledWith({
      sessionid: '1005',
      player: 'X',
      row: 1,
      col: 0,
      board: [
        ['X', 'O', 'X'],
        ['X', 'O', null],
        [null, null, 'X']
      ]
    });
  });

  it('should not emit move when clicking occupied cell', () => {
    spyOn(component.move, 'emit');

    component.onCellClick(0, 0);

    expect(component.move.emit).not.toHaveBeenCalled();
  });

  it('should emit close event', () => {
    spyOn(component.close, 'emit');

    component.onClose();

    expect(component.close.emit).toHaveBeenCalled();
  });
});
