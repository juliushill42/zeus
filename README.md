# ⚡ ZEUS Automated Multi-Agent Engine

A local, self-healing AI multi-agent grid. 

ZEUS splits complex decision-making across specialized Python "Expert" nodes, all managed by a high-speed Golang orchestrator and a built-in web dashboard. It runs entirely locally—no cloud dependencies, no external message brokers, and no data leaks.

---

## 🛠️ How It Works

Instead of one AI guessing the answer, ZEUS acts like an assembly line:
1. **The Generator (QE):** Creates the raw data.
2. **The Math Core (CE):** Runs the heavy calculations.
3. **The Safety Gate (BME):** A hardcoded logic tripwire. If the math violates safety rules, the BME halts the system. It cannot go rogue.
4. **The Risk Assessor (FE):** Calculates market risk and yield.
5. **The Packager (MTE):** Formats the data and applies a cryptographic hash.

All of this is monitored by the **Golang Supervisor (`main.go`)**, which instantly restarts any Python node if it crashes and serves the live web dashboard.

---

## 🚀 Quick Start Guide

**Prerequisites:**
* Python 3.8+
* Go (Golang) installed

**1. Clone the Repository**
```bash
git clone [https://github.com/juliushill42/zeus.git](https://github.com/juliushill42/zeus.git)
cd zeus
