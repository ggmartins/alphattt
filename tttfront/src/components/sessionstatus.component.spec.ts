import 'jasmine';
import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SessionStatusComponent } from './sessionstatus.component';
import { SessionStatus } from './sessionstatus.model';

describe('SessionStatusComponent', () => {
  let component: SessionStatusComponent;
  let fixture: ComponentFixture<SessionStatusComponent>;

  const mockSession: SessionStatus = {
    sessionId: 10,
    vsplayer: 'Alice',
    playerId: 1,
    timestamp: new Date('2026-04-30T12:00:00'),
    board: [
      [null, null, null],
      [null, null, null],
      [null, null, null],
    ],
    status: 'not_launched',
    playingAs: "O",
    nextTurn: "Other Player"
  };

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [SessionStatusComponent],
    }).compileComponents();

    fixture = TestBed.createComponent(SessionStatusComponent);
    component = fixture.componentInstance;
    component.session = mockSession;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });

  it('should display the opposing player name', () => {
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.textContent).toContain('Alice');
  });

  it('should display session id', () => {
    const compiled = fixture.nativeElement as HTMLElement;

    expect(compiled.textContent).toContain('Session #10');
  });

  it('should show Not Launched status label', () => {
    expect(component.statusLabel).toBe('Not Launched');
  });

  it('should emit session id when launch button is clicked', () => {
    spyOn(component.launchMatch, 'emit');

    component.onLaunchClick();

    expect(component.launchMatch.emit).toHaveBeenCalledWith(10);
  });

  it('should emit launch event when match is ongoing', () => {
    spyOn(component.launchMatch, 'emit');

    component.session = {
      ...mockSession,
      status: 'ongoing',
    };

    component.onLaunchClick();

    expect(component.launchMatch.emit).toHaveBeenCalledWith(10);
  });

  it('should keep launch button enabled when match is finished', () => {
    component.session = {
      ...mockSession,
      status: 'finished',
    };

    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector(
      'button'
    ) as HTMLButtonElement;

    expect(button.disabled).toBeFalse();
  });
});
