#!/usr/bin/env python3
import socket
import threading
import sys

ENCODING = "utf-8"

class ChatClient:
    def __init__(self, host: str, port: int, name: str):
        self.host = host
        self.port = port
        self.name = name
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = True

    def start(self):
        self.sock.connect((self.host, self.port))
        self.reader = self.sock.makefile("r", encoding=ENCODING, newline="\n")
        threading.Thread(target=self.listen_loop, daemon=True).start()
        self.send_line(f"HELLO {self.name}")
        self.input_loop()

    def send_line(self, line: str):
        self.sock.sendall((line + "\n").encode(ENCODING))

    def listen_loop(self):
        try:
            while self.running:
                line = self.reader.readline()
                if not line:
                    print("[client] server disconnected")
                    break
                print(line.strip())
        finally:
            self.running = False

    def input_loop(self):
        try:
            while self.running:
                try:
                    line = input()
                except EOFError:
                    line = "QUIT"
                if not line:
                    continue
                if line.lower() == "/quit":
                    line = "QUIT"
                self.send_line(line)
                if line == "QUIT":
                    break
        finally:
            self.running = False
            try:
                self.sock.close()
            except Exception:
                pass

if __name__ == "__main__":
    if len(sys.argv) < 4:
        print("usage: python3 chat_client.py <host> <port> <name>")
        sys.exit(1)
    host = sys.argv[1]
    port = int(sys.argv[2])
    name = sys.argv[3]
    ChatClient(host, port, name).start()
