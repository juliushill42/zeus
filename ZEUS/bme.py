import time
from modules.zeus_net import ZeusNode

class BooleanMasterExpert(ZeusNode):
    def __init__(self):
        super().__init__("BME")
        self.rules = {
            "DATA_INTEGRITY": lambda payload: len(payload) > 0,
            "COHERENCE_BOUNDS": lambda score: score > 0.70,
            "CRITICAL_SAFETY": lambda state: state == "GREEN"
        }

    def on_message_received(self, msg):
        if msg["message_type"] == "VALIDATE_REQUEST":
            p = msg["payload"]
            print("[BME] Performing logic verification checks...")
            
            pass_1 = self.rules["DATA_INTEGRITY"](p["raw_matrix"])
            pass_2 = self.rules["COHERENCE_BOUNDS"](p["coherence_score"])
            pass_3 = self.rules["CRITICAL_SAFETY"](p["safety_rating"])
            
            system_cleared = pass_1 and pass_2 and pass_3
            assert_token = "DECISION_VALID_EXECUTE" if system_cleared else "DECISION_INVALID_HALT"
            
            self.send_message("COC", "STATE_UPDATE", {"BME_VALIDATION": True})
            self.send_message("FE", "RISK_CHECK", {
                "assert_token": assert_token,
                "confidence_score": p["coherence_score"],
                "base_index": p["norm_index"]
            })

if __name__ == "__main__":
    node = BooleanMasterExpert()
    while True:
        if not node.running:
            node.connect_to_bus()
        time.sleep(2)
