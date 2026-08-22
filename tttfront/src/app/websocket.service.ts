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
    if (this.socket?.readyState === WebSocket.OPEN) {
      onOpen?.();
      return;
    }

    if (this.socket?.readyState === WebSocket.CONNECTING) {
      if (onOpen) {
        this.socket.addEventListener('open', onOpen, { once: true });
      }
      return;
    }

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

  isConnected(): boolean {
    return this.socket?.readyState === WebSocket.OPEN;
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
