import time
from modules.zeus_net import ZeusNode

class ClientInterface(ZeusNode):
    def __init__(self):
        super().__init__("CLIENT")

    def on_message_received(self, msg):
        if msg["message_type"] == "DISPLAY_REQUEST":
            p = msg["payload"]
            om = p["operational_metrics"]
            
            print("\n" + "=" * 60)
            print("         ZEUS LIVE PRODUCTION NETWORK TELEMETRY PANEL")
            print("=" * 60)
            print(f" - Verification Key       : {p['uuid_token']}")
            print(f" - Logic Authorization    : {om['gate_authorization']}")
            print(f" - Account Risk Profile   : {om['risk_profile']} (Variance Bounds: {om['volatility_index']:.5f})")
            print(f" - System Projected Yield : {om['economic_yield_projection']:.9f}")
            print(f" - Quantum Allocation Sign: {p['quantum_signature']['entanglement_map']}")
            print("-" * 60 + "\n", flush=True)

if __name__ == "__main__":
    node = ClientInterface()
    while True:
        if not node.running:
            node.connect_to_bus()
        time.sleep(2)
