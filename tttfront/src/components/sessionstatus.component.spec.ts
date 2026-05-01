import { ComponentFixture, TestBed } from '@angular/core/testing';
import { SessionStatusComponent } from './sessionstatus.component';
import { SessionStatus } from './sessionstatus.model';

describe('SessionStatusComponent', () => {
  let component: SessionStatusComponent;
  let fixture: ComponentFixture<SessionStatusComponent>;

  const mockSession: SessionStatus = {
    sessionId: 10,
    vsplayer: {
      playerId: 1,
      playerName: 'Alice',
    },
    timestamp: new Date('2026-04-30T12:00:00'),
    status: 'not_launched',
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

  it('should allow launch when status is not_launched', () => {
    expect(component.canLaunch).toBeTrue();
  });

  it('should emit session id when launch button is clicked', () => {
    spyOn(component.launchMatch, 'emit');

    component.onLaunchClick();

    expect(component.launchMatch.emit).toHaveBeenCalledWith(10);
  });

  it('should not emit launch event when match is ongoing', () => {
    spyOn(component.launchMatch, 'emit');

    component.session = {
      ...mockSession,
      status: 'ongoing',
    };

    component.onLaunchClick();

    expect(component.launchMatch.emit).not.toHaveBeenCalled();
  });

  it('should disable launch button when match is finished', () => {
    component.session = {
      ...mockSession,
      status: 'finished',
    };

    fixture.detectChanges();

    const button = fixture.nativeElement.querySelector(
      'button'
    ) as HTMLButtonElement;

    expect(button.disabled).toBeTrue();
  });
});
