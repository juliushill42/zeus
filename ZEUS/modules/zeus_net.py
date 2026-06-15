import socket
import json
import threading
import time

class ZeusNode:
    def __init__(self, node_name, host='127.0.0.1', port=5000):
        self.node_name = node_name
        self.host = host
        self.port = port
        self.sock = None
        self.running = False
        self._listener_thread = None

    def connect_to_bus(self):
        self.running = False
        if self.sock:
            try:
                self.sock.close()
            except Exception:
                pass
        
        try:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.sock.connect((self.host, self.port))
            self.running = True
            self.send_message("COC", "HANDSHAKE", {"status": "READY"})
            self._listener_thread = threading.Thread(target=self._listen_loop, daemon=True)
            self._listener_thread.start()
            print(f"[{self.node_name}] Connection successful.")
            return True
        except Exception as e:
            print(f"[{self.node_name}] Connection failed - {e}")
            self.running = False
            return False

    def send_message(self, target, msg_type, payload):
        if not self.running or not self.sock:
            return
        message = {
            "sender": self.node_name,
            "target": target,
            "message_type": msg_type,
            "payload": payload,
            "timestamp": time.time()
        }
        try:
            raw_data = (json.dumps(message) + "\n").encode('utf-8')
            self.sock.sendall(raw_data)
        except Exception:
            self.running = False

    def _listen_loop(self):
        raw_buffer = bytearray()
        while self.running:
            try:
                data = self.sock.recv(4096)
                if not data:
                    self.running = False
                    break
                raw_buffer.extend(data)
                
                while b"\n" in raw_buffer:
                    line_bytes, raw_buffer = raw_buffer.split(b"\n", 1)
                    if line_bytes:
                        msg = json.loads(line_bytes.decode('utf-8'))
                        self.on_message_received(msg)
            except Exception:
                self.running = False
                break
        self.running = False
        print(f"[{self.node_name}] Disconnected.")

    def on_message_received(self, msg):
        pass
