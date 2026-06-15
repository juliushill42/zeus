import time
import random
from modules.zeus_net import ZeusNode
from modules.quantum_sim import QuantumSimulator

class QuantumExpert(ZeusNode):
    def __init__(self):
        super().__init__("QE")
        self.simulator = QuantumSimulator()

    def on_message_received(self, msg):
        if msg["message_type"] in ["TRIGGER_CYCLE", "CYCLE_RESET"]:
            print("[QE] Computing allocation vectors...")
            raw_dataset = [random.uniform(10.0, 500.0) for _ in range(5)]
            qubits = self.simulator.encode_data(raw_dataset)
            optimized_qubits = self.simulator.apply_optimization_gate(qubits)
            metrics = self.simulator.measure_output()
            
            self.send_message("COC", "STATE_UPDATE", {"QE_READY": True})
            self.send_message("CE", "OPTIMIZE_REQUEST", {
                "quantum_vector": optimized_qubits,
                "metrics": metrics
            })

if __name__ == "__main__":
    node = QuantumExpert()
    while True:
        if not node.running:
            node.connect_to_bus()
        time.sleep(2)
