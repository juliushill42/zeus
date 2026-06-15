import subprocess
import time
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(PROJECT_ROOT, "logs")
EXPERT_SCRIPTS = ["coc.py", "qe.py", "ce.py", "bme.py", "fe.py", "mte.py", "client.py"]

def spawn_node(script_name):
    script_path = os.path.join(PROJECT_ROOT, script_name)
    log_file_path = os.path.join(LOG_DIR, f"{script_name.replace('.py', '')}.log")
    try:
        log_fd = open(log_file_path, "a")
        return subprocess.Popen(
            [sys.executable, script_path],
            cwd=PROJECT_ROOT,
            stdout=log_fd,
            stderr=log_fd
        ), log_fd
    except Exception as e:
        print(f"Orchestrator failure on node {script_name}: {e}")
        return None, None

def main():
    print("======================================================================")
    print("      ZEUS RECURSIVE DISCOVERY STACK: HIGH-AVAILABILITY RUNTIME       ")
    print("======================================================================")
    
    active_runtime = {}
    file_descriptors = {}
    
    print("[SYSTEM] Deploying Central Core Integration Bus...")
    coc_proc, coc_fd = spawn_node("coc.py")
    if coc_proc:
        active_runtime["COC"] = coc_proc
        file_descriptors["COC"] = coc_fd
    time.sleep(3.0)
    
    for agent_script in EXPERT_SCRIPTS[1:]:
        alias = agent_script.replace('.py', '').upper()
        print(f"[SYSTEM] Spawning Isolated Component Layer -> {alias}")
        proc, fd = spawn_node(agent_script)
        if proc:
            active_runtime[alias] = proc
            file_descriptors[alias] = fd
        time.sleep(0.5)

    print("\n[SYSTEM] Multi-Agent Network Stack Online. Running heartbeat loop.\n")
    
    try:
        while True:
            time.sleep(2)
            for alias, process in list(active_runtime.items()):
                if process.poll() is not None:
                    print(f"[GRID ALERT] Node '{alias}' lost connection. Reviving component...")
                    try: file_descriptors[alias].close()
                    except Exception: pass
                    
                    if alias == "COC":
                        time.sleep(2.0)
                        
                    target_script = "coc.py" if alias == "COC" else f"{alias.lower()}.py"
                    revived_proc, revived_fd = spawn_node(target_script)
                    if revived_proc:
                        active_runtime[alias] = revived_proc
                        file_descriptors[alias] = revived_fd
    except KeyboardInterrupt:
        print("\n[SYSTEM] Shuting down cluster layers cleanly...")
    finally:
        for alias, process in active_runtime.items():
            if process and process.poll() is None:
                try: process.terminate()
                except Exception: pass
        for fd in file_descriptors.values():
            try: fd.close()
            except Exception: pass
        print("=== DE-ALLOCATION COMPLETE ===")

if __name__ == "__main__":
    main()
