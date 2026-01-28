#!/usr/bin/env python3
import socket
import threading
import time
from dataclasses import dataclass
from typing import Dict, Optional

HOST = "0.0.0.0"
PORT = 9009
ENCODING = "utf-8"

@dataclass
class ClientInfo:
    name: str
    sock: socket.socket
    addr: tuple
    peer: Optional[str] = None
    alive: bool = True

class ChatServer:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.server_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server_sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.clients: Dict[str, ClientInfo] = {}
        self.lock = threading.Lock()

    def start(self):
        self.server_sock.bind((self.host, self.port))
        self.server_sock.listen()
        print(f"[server] listening on {self.host}:{self.port}")
        try:
            while True:
                client_sock, addr = self.server_sock.accept()
                threading.Thread(target=self.handle_client, args=(client_sock, addr), daemon=True).start()
        finally:
            self.server_sock.close()

    def send_line(self, sock: socket.socket, line: str):
        sock.sendall((line + "\n").encode(ENCODING))

    def handle_client(self, sock: socket.socket, addr):
        file = sock.makefile("r", encoding=ENCODING, newline="\n")
        name = None
        try:
            self.send_line(sock, "WELCOME send: HELLO <name>")
            line = file.readline()
            if not line:
                return
            line = line.strip()
            if not line.startswith("HELLO "):
                self.send_line(sock, "ERR expected HELLO <name>")
                return
            name = line.split(" ", 1)[1].strip()
            if not name:
                self.send_line(sock, "ERR empty name")
                return
            with self.lock:
                if name in self.clients:
                    self.send_line(sock, "ERR name already taken")
                    return
                self.clients[name] = ClientInfo(name=name, sock=sock, addr=addr)
            self.send_line(sock, f"OK HELLO {name}")
            self.send_line(sock, "INFO commands: LIST | CHAT <name> | MSG <text> | QUIT")

            while True:
                line = file.readline()
                if not line:
                    break
                line = line.strip()
                if not line:
                    continue
                if line == "LIST":
                    with self.lock:
                        users = ",".join(sorted(self.clients.keys()))
                    self.send_line(sock, f"USERS {users}")
                elif line.startswith("CHAT "):
                    target = line.split(" ", 1)[1].strip()
                    self.handle_chat_request(name, target)
                elif line.startswith("MSG "):
                    msg = line.split(" ", 1)[1]
                    self.forward_message(name, msg)
                elif line == "QUIT":
                    self.send_line(sock, "BYE")
                    break
                else:
                    self.send_line(sock, "ERR unknown command")
        except Exception as e:
            try:
                self.send_line(sock, f"ERR server exception: {e}")
            except Exception:
                pass
        finally:
            if name:
                self.disconnect(name)
            try:
                file.close()
            except Exception:
                pass
            try:
                sock.close()
            except Exception:
                pass

    def handle_chat_request(self, name: str, target: str):
        if not target or target == name:
            self.send_to(name, "ERR invalid target")
            return
        with self.lock:
            if name not in self.clients:
                return
            if target not in self.clients:
                self.send_to(name, "ERR target not online")
                return
            if self.clients[name].peer is not None:
                self.send_to(name, f"ERR already chatting with {self.clients[name].peer}")
                return
            if self.clients[target].peer is not None:
                self.send_to(name, f"ERR target busy with {self.clients[target].peer}")
                return
            self.clients[name].peer = target
            self.clients[target].peer = name
        self.send_to(name, f"CHAT_OK {target}")
        self.send_to(target, f"CHAT_OK {name}")

    def forward_message(self, name: str, msg: str):
        with self.lock:
            if name not in self.clients:
                return
            peer = self.clients[name].peer
        if not peer:
            self.send_to(name, "ERR no active chat. Use CHAT <name>")
            return
        self.send_to(peer, f"FROM {name} {msg}")

    def send_to(self, name: str, line: str):
        with self.lock:
            client = self.clients.get(name)
            if not client:
                return
            sock = client.sock
        try:
            self.send_line(sock, line)
        except Exception:
            self.disconnect(name)

    def disconnect(self, name: str):
        with self.lock:
            client = self.clients.pop(name, None)
            if not client:
                return
            peer = client.peer
            client.alive = False
            if peer and peer in self.clients:
                self.clients[peer].peer = None
        if peer:
            self.send_to(peer, f"INFO {name} disconnected")
        print(f"[server] {name} disconnected")

if __name__ == "__main__":
    import sys
    host = HOST
    port = PORT
    if len(sys.argv) >= 2:
        host = sys.argv[1]
    if len(sys.argv) >= 3:
        port = int(sys.argv[2])
    ChatServer(host, port).start()
