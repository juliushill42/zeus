import random

class QuantumSimulator:
    def __init__(self, num_qubits=12):
        self.num_qubits = num_qubits

    def encode_data(self, data):
        total = sum(data) if sum(data) > 0 else 1.0
        return [float(x) / total for x in data]

    def apply_optimization_gate(self, qubits):
        if not qubits:
            return qubits
        max_val = max(qubits)
        idx = qubits.index(max_val)
        qubits[idx] = min(1.0, max_val * 1.35)
        return qubits

    def measure_output(self):
        return {'probability': random.uniform(0.78, 0.99)}
