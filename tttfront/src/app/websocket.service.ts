import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class WebsocketService {
  private socket?: WebSocket;

  connect(
    onMessage: (message: string) => void,
    onOpen?: () => void,
    onClose?: () => void,
    onError?: (error: Event) => void
  ): void {
    this.socket = new WebSocket('ws://localhost:8000/ws');

    this.socket.onopen = () => {
      console.log('WebSocket connected');
      if (onOpen) {
        onOpen();
      }
    };

    this.socket.onmessage = (event) => {
      onMessage(event.data);
    };

    this.socket.onclose = () => {
      console.log('WebSocket closed');
      if (onClose) {
        onClose();
      }
    };

    this.socket.onerror = (error) => {
      console.error('WebSocket error', error);
      if (onError) {
        onError(error);
      }
    };
  }

  sendMessage(message: string): void {
    if (!this.socket || this.socket.readyState !== WebSocket.OPEN) {
      console.error('WebSocket is not connected');
      return;
    }

    this.socket.send(message);
  }

  disconnect(): void {
    this.socket?.close();
  }
}

/*import { Injectable } from '@angular/core';

@Injectable({
  providedIn: 'root'
})
export class WebsocketService {

  constructor() { }
}*/
