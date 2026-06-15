import time
import random
from modules.zeus_net import ZeusNode

class FinancialExpert(ZeusNode):
    def __init__(self):
        super().__init__("FE")

    def on_message_received(self, msg):
        if msg["message_type"] == "RISK_CHECK":
            print("[FE] Executing risk valuation curves...")
            p = msg["payload"]
            variance_factor = random.uniform(0.05, 0.32)
            computed_risk = "LOW" if variance_factor < 0.45 else "CRITICAL"
            adjusted_index = p["base_index"] * (1.0 + variance_factor)
            
            self.send_message("COC", "STATE_UPDATE", {"FE_DATA_RECEIVED": True})
            self.send_message("MTE", "TRANSFORM_REQUEST", {
                "gate_authorization": p["assert_token"],
                "risk_profile": computed_risk,
                "volatility_index": variance_factor,
                "economic_yield_projection": adjusted_index
            })

if __name__ == "__main__":
    node = FinancialExpert()
    while True:
        if not node.running:
            node.connect_to_bus()
        time.sleep(2)
