import socket
import json
import threading
import time
from modules.quantum_logic import QuantumCoordinator

class CenterOfCommand:
    def __init__(self, host='127.0.0.1', port=5000):
        self.host = host
        self.port = port
        self.clients = {}
        self.lock = threading.Lock()
        self.matrix = {
            'QE_READY': False,
            'CE_ACTIVE': False,
            'BME_VALIDATION': False,
            'FE_DATA_RECEIVED': False,
            'MTE_TRANSFORMATION_COMPLETE': False
        }
        self.coordinator = QuantumCoordinator()
        self.coordinator.entangle_experts(list(self.matrix.keys()))

    def start(self):
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server.bind((self.host, self.port))
        server.listen(15)
        print(f"[COC] Server active on {self.host}:{self.port}")
        
        threading.Thread(target=self._lifecycle_loop, daemon=True).start()

        while True:
            try:
                conn, addr = server.accept()
                threading.Thread(target=self._client_handler, args=(conn,), daemon=True).start()
            except KeyboardInterrupt:
                break

    def _client_handler(self, conn):
        buffer = ""
        client_name = "UNKNOWN"
        try:
            while True:
                data = conn.recv(4096).decode('utf-8')
                if not data:
                    break
                buffer += data
                while "\n" in buffer:
                    line, buffer = buffer.split("\n", 1)
                    if line:
                        msg = json.loads(line)
                        sender = msg["sender"]
                        target = msg["target"]
                        mtype = msg["message_type"]
                        payload = msg["payload"]
                        
                        if mtype == "HANDSHAKE":
                            client_name = sender
                            with self.lock:
                                self.clients[client_name] = conn
                            print(f"[COC] Registered: {client_name}")
                            continue
                        
                        if mtype == "STATE_UPDATE":
                            with self.lock:
                                for k, v in payload.items():
                                    if k in self.matrix:
                                        self.matrix[k] = v
                        
                        target_conn = None
                        all_conns = []
                        with self.lock:
                            if target in self.clients:
                                target_conn = self.clients[target]
                            elif target == "ALL":
                                all_conns = [c for c_name, c in self.clients.items() if c_name != sender]
                        
                        raw_msg = (json.dumps(msg) + "\n").encode('utf-8')
                        if target_conn:
                            try: target_conn.sendall(raw_msg)
                            except Exception: pass
                        elif all_conns:
                            for c_conn in all_conns:
                                try: c_conn.sendall(raw_msg)
                                except Exception: pass
        except Exception:
            pass
        finally:
            with self.lock:
                if client_name in self.clients:
                    del self.clients[client_name]
            try: conn.close()
            except Exception: pass
            print(f"[COC] Unregistered: {client_name}")

    def _lifecycle_loop(self):
        while True:
            time.sleep(3)
            with self.lock:
                current_matrix = dict(self.matrix)
                has_qe = "QE" in self.clients
                
            print(f"[COC] Matrix State: {current_matrix}")
            
            if all(current_matrix.values()):
                print("[COC] Convergence achieved. Collapsing state.")
                unified_state = self.coordinator.collapse_state()
                print(f"[COC] Result Resolved: {unified_state}")
                
                with self.lock:
                    for key in current_matrix.keys():
                        if self.matrix[key] == current_matrix[key]:
                            self.matrix[key] = False
                            
                self.broadcast("CYCLE_RESET", {"status": "RESET"})
            
            if not any(current_matrix.values()) and has_qe:
                self.send_direct("QE", "TRIGGER_CYCLE", {})

    def broadcast(self, mtype, payload):
        msg = {"sender": "COC", "target": "ALL", "message_type": mtype, "payload": payload, "timestamp": time.time()}
        raw = (json.dumps(msg) + "\n").encode('utf-8')
        with self.lock:
            active_conns = list(self.clients.values())
        for conn in active_conns:
            try: conn.sendall(raw)
            except Exception: pass

    def send_direct(self, target, mtype, payload):
        msg = {"sender": "COC", "target": target, "message_type": mtype, "payload": payload, "timestamp": time.time()}
        raw = (json.dumps(msg) + "\n").encode('utf-8')
        target_conn = None
        with self.lock:
            if target in self.clients:
                target_conn = self.clients[target]
        if target_conn:
            try: target_conn.sendall(raw)
            except Exception: pass

if __name__ == "__main__":
    coc = CenterOfCommand()
    coc.start()
