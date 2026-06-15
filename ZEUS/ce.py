import time
import math
from modules.zeus_net import ZeusNode

class ComputationalExpert(ZeusNode):
    def __init__(self):
        super().__init__("CE")
        self.cores = 8

    def on_message_received(self, msg):
        if msg["message_type"] == "OPTIMIZE_REQUEST":
            print("[CE] Calculating magnitude matrices...")
            vector = msg["payload"]["quantum_vector"]
            sq_sum = sum(x**2 for x in vector)
            calculated_norm = math.sqrt(sq_sum) / float(self.cores)
            
            self.send_message("COC", "STATE_UPDATE", {"CE_ACTIVE": True})
            self.send_message("BME", "VALIDATE_REQUEST", {
                "norm_index": calculated_norm,
                "coherence_score": msg["payload"]["metrics"]["probability"],
                "safety_rating": "GREEN",
                "raw_matrix": vector
            })

if __name__ == "__main__":
    node = ComputationalExpert()
    while True:
        if not node.running:
            node.connect_to_bus()
        time.sleep(2)
