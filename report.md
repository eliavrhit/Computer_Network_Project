# TCP/IP Encapsulation + Private Chat Project

## Part 1 — CSV + Jupyter + Wireshark

### CSV creation
- File: `group661305-6_chat_input.csv`
- Format (as required by the notebook validator):
  - `app_protocol, src_port, dst_port, message, timestamp`
- How it was created: manually written messages that simulate a private chat flow.

### Encapsulation explanation (summary)
- Application data is the `message` field.
- Transport layer builds TCP headers (src/dst ports, flags).
- Network layer builds IPv4 header (src/dst IP, TTL, checksum).
- Link layer would wrap IP into frames (not explicitly built in the notebook).

### Notebook run
- Notebook: `raw_tcp_ip_notebook_fallback_annotated-v1.ipynb`
- CSV path set to `./group661305-6_chat_input.csv`.
- Output cells show:
  - CSV loaded and validated
  - Raw IP/TCP headers
  - Hex dump of packets

### Wireshark capture (Part 1)
- Interface: loopback (`lo0` on macOS)
- Filter used: `ip.addr == 127.0.0.1 && tcp`
- Payload example observed: `test message ...` (from the CSV)
- Attach screenshots (Part 1):
  - Packet list with filter applied
  - Packet details showing IP/TCP header fields
  - Packet bytes showing the payload text

## Part 2 — Private TCP Chat Application

### Goal
Private 1-to-1 chat between two clients. A third client must not receive those messages.
Server can handle at least 5 concurrent clients.

### Architecture
- `chat_server.py`: TCP server, accepts clients, routes messages only to a paired peer.
- `chat_client.py`: CLI client, connects, registers name, sends commands.

### Data structure summary
- `clients: Dict[name, ClientInfo]`
  - Holds socket, address, and `peer` (current chat partner).
- When `CHAT <name>` succeeds, both clients get `peer` set to each other.
- Messages are forwarded only to the active `peer`.

### Edge cases handled
- Duplicate names rejected.
- Chat request to offline or busy client rejected.
- Sending `MSG` without an active chat returns an error.
- Unexpected disconnect clears the peer link and notifies the other side.

### How to run
1) Start server:
   ```bash
   python3 chat_server.py 0.0.0.0 9009
   ```
2) Start at least 5 clients in separate terminals:
   ```bash
   python3 chat_client.py 127.0.0.1 9009 alice
   python3 chat_client.py 127.0.0.1 9009 bob
   python3 chat_client.py 127.0.0.1 9009 carol
   python3 chat_client.py 127.0.0.1 9009 dave
   python3 chat_client.py 127.0.0.1 9009 erin
   ```
3) Example commands in client:
   ```
   LIST
   CHAT bob
   MSG hi bob
   QUIT
   ```

### Wireshark capture (Part 2)
- Interface: loopback (`lo0` on macOS)
- Filter used: `tcp.port == 9009`
- Capture steps:
  - Start capture
  - Run server + clients
  - Exchange private messages
  - Stop capture and save `.pcap`
- Payload example observed: `hi bob` (private message)
- Attach screenshots (Part 2):
  - TCP handshake (SYN/SYN-ACK/ACK)
  - Packet details showing IP/TCP header fields
  - Packet bytes showing the payload text

## AI usage
- If applicable, list prompts and goals here.

## Files submitted
- `group661305-6_chat_input.csv`
- `raw_tcp_ip_notebook_fallback_annotated-v1.ipynb`
- `part1_capture.pcap`
- `chat_server.py`, `chat_client.py`
- `part2_capture.pcap`
- `report.md`
- Screenshots (add filenames):
  - Part 1 packet list: download-3.png
  - Part 1 packet details: part1-1.png && part1-2.png
  - Part 1 payload: part1_test_message.png
  - Part 2 handshake: part_2_handshake.png
  - Part 2 packet details: hi_bob_tcp_ip.png
  - Part 2 payload: part2_hi_bob_message.png
