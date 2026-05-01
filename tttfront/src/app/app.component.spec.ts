import { TestBed } from '@angular/core/testing';
import { AppComponent } from './app.component';
import { WebsocketService } from './websocket.service';

describe('AppComponent', () => {
  const websocketServiceSpy = jasmine.createSpyObj<WebsocketService>(
    'WebsocketService',
    ['connect', 'disconnect', 'sendMessage']
  );

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [AppComponent],
      providers: [
        { provide: WebsocketService, useValue: websocketServiceSpy },
      ],
    }).compileComponents();
  });

  it('should create the app', () => {
    const fixture = TestBed.createComponent(AppComponent);
    const app = fixture.componentInstance;
    expect(app).toBeTruthy();
  });

  it('should render title', () => {
    const fixture = TestBed.createComponent(AppComponent);
    fixture.detectChanges();
    const compiled = fixture.nativeElement as HTMLElement;
    expect(compiled.querySelector('h1')?.textContent).toContain('Alpha Tic Tac Toe');
  });
});
