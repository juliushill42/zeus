package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"net"
	"net/http"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"sync"
	"syscall"
	"time"
)

// We removed "client.py" because Go is now the client and the web server.
var scripts = []string{"coc.py", "qe.py", "ce.py", "bme.py", "fe.py", "mte.py"}
var processes = make(map[string]*exec.Cmd)

// Thread-safe storage for the web dashboard to read
var latestTelemetry interface{}
var telemetryLock sync.RWMutex

func main() {
	fmt.Println("======================================================")
	fmt.Println("   ⚡ ZEUS ORCHESTRATOR & NATIVE UI (GOLANG ENGINE)   ")
	fmt.Println("======================================================")

	cwd, _ := os.Getwd()
	logDir := filepath.Join(cwd, "logs")
	os.MkdirAll(logDir, os.ModePerm)

	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-sigs
		fmt.Println("\n[SYSTEM] Shutting down Python grid cleanly...")
		for _, cmd := range processes {
			if cmd != nil && cmd.Process != nil {
				cmd.Process.Kill()
			}
		}
		os.Exit(0)
	}()

	// 1. Boot Python Node Grid
	launchNode("coc.py", logDir)
	time.Sleep(3 * time.Second) 

	for i := 1; i < len(scripts); i++ {
		launchNode(scripts[i], logDir)
		time.Sleep(500 * time.Millisecond)
	}

	// 2. Go connects to the ZEUS Python network
	go connectToZMB()

	// 3. Go boots the modern Web UI
	http.HandleFunc("/api/data", handleData)
	http.HandleFunc("/", handleUI)
	
	fmt.Println("\n[SYSTEM] Multi-Agent Stack Online.")
	fmt.Println("[SYSTEM] GUI live at: http://localhost:8080")
	fmt.Println("[SYSTEM] Press Ctrl+C to terminate the grid.")

	http.ListenAndServe(":8080", nil)
}

// -----------------------------------------------------------------------------
// GRID SUPERVISOR
// -----------------------------------------------------------------------------
func launchNode(script string, logDir string) {
	go func() {
		for {
			logPath := filepath.Join(logDir, script+".log")
			logFile, err := os.OpenFile(logPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
			if err != nil {
				return
			}

			fmt.Printf("[DEPLOY] Spawning Node -> %s\n", script)
			cmd := exec.Command("python3", script)
			cmd.Stdout = logFile
			cmd.Stderr = logFile
			processes[script] = cmd
			
			cmd.Run()
			logFile.Close()
			
			fmt.Printf("[ALERT] Node '%s' dropped. Auto-recovering...\n", script)
			if script == "coc.py" {
				time.Sleep(2 * time.Second)
			} else {
				time.Sleep(1 * time.Second)
			}
		}
	}()
}

// -----------------------------------------------------------------------------
// GO NATIVE TCP CLIENT (Replaces client.py)
// -----------------------------------------------------------------------------
func connectToZMB() {
	for {
		conn, err := net.Dial("tcp", "127.0.0.1:5000")
		if err != nil {
			time.Sleep(2 * time.Second)
			continue
		}

		// Register Go with the Python Center of Command
		handshake := `{"sender": "CLIENT", "target": "COC", "message_type": "HANDSHAKE", "payload": {"status": "READY"}, "timestamp": 0}` + "\n"
		conn.Write([]byte(handshake))

		scanner := bufio.NewScanner(conn)
		for scanner.Scan() {
			line := scanner.Text()
			var msg map[string]interface{}
			if err := json.Unmarshal([]byte(line), &msg); err == nil {
				if msg["message_type"] == "DISPLAY_REQUEST" {
					telemetryLock.Lock()
					latestTelemetry = msg["payload"]
					telemetryLock.Unlock()
				}
			}
		}
		conn.Close()
		time.Sleep(2 * time.Second) // Reconnect if the broker crashes
	}
}

// -----------------------------------------------------------------------------
// MODERN WEB DASHBOARD
// -----------------------------------------------------------------------------
func handleData(w http.ResponseWriter, r *http.Request) {
	telemetryLock.RLock()
	defer telemetryLock.RUnlock()
	
	w.Header().Set("Content-Type", "application/json")
	if latestTelemetry == nil {
		w.Write([]byte(`{}`))
		return
	}
	json.NewEncoder(w).Encode(latestTelemetry)
}

func handleUI(w http.ResponseWriter, r *http.Request) {
	w.Header().Set("Content-Type", "text/html")
	html := `
	<!DOCTYPE html>
	<html lang="en">
	<head>
		<meta charset="UTF-8">
		<meta name="viewport" content="width=device-width, initial-scale=1.0">
		<title>ZEUS // Grid Command</title>
		<style>
			:root {
				--bg-dark: #0d0f12;
				--panel-bg: rgba(255, 255, 255, 0.03);
				--border: rgba(255, 255, 255, 0.08);
				--text-main: #e2e8f0;
				--text-muted: #64748b;
				--neon-green: #10b981;
				--neon-red: #ef4444;
				--accent: #3b82f6;
			}
			body {
				background-color: var(--bg-dark);
				color: var(--text-main);
				font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto, Helvetica, Arial, sans-serif;
				display: flex;
				justify-content: center;
				align-items: center;
				height: 100vh;
				margin: 0;
			}
			.dashboard {
				background: var(--panel-bg);
				backdrop-filter: blur(16px);
				-webkit-backdrop-filter: blur(16px);
				border: 1px solid var(--border);
				border-radius: 16px;
				padding: 40px;
				width: 480px;
				box-shadow: 0 25px 50px -12px rgba(0, 0, 0, 0.5);
			}
			.header {
				display: flex;
				justify-content: space-between;
				align-items: center;
				border-bottom: 1px solid var(--border);
				padding-bottom: 20px;
				margin-bottom: 30px;
			}
			.header h1 { margin: 0; font-size: 1.5rem; font-weight: 600; letter-spacing: -0.025em; }
			.pulse { width: 10px; height: 10px; background-color: var(--neon-green); border-radius: 50%; box-shadow: 0 0 10px var(--neon-green); animation: pulse 2s infinite; }
			@keyframes pulse { 0% { opacity: 1; } 50% { opacity: 0.4; } 100% { opacity: 1; } }
			
			.metric-grid { display: flex; flex-direction: column; gap: 24px; }
			.metric-box { display: flex; flex-direction: column; gap: 8px; }
			.label { font-size: 0.75rem; text-transform: uppercase; letter-spacing: 0.1em; color: var(--text-muted); font-weight: 600; }
			
			.value-container { background: rgba(0,0,0,0.3); border: 1px solid var(--border); padding: 16px; border-radius: 8px; font-family: ui-monospace, SFMono-Regular, Menlo, Monaco, Consolas, monospace; font-size: 1.1rem; }
			
			.status-badge { display: inline-flex; padding: 6px 12px; border-radius: 4px; font-weight: 700; font-size: 0.9rem; }
			.status-exec { background: rgba(16, 185, 129, 0.1); color: var(--neon-green); border: 1px solid rgba(16, 185, 129, 0.2); }
			.status-halt { background: rgba(239, 68, 68, 0.1); color: var(--neon-red); border: 1px solid rgba(239, 68, 68, 0.2); }
			.status-wait { background: rgba(100, 116, 139, 0.1); color: var(--text-muted); border: 1px solid rgba(100, 116, 139, 0.2); }
		</style>
	</head>
	<body>
		<div class="dashboard">
			<div class="header">
				<h1>ZEUS GRID // TELEMETRY</h1>
				<div class="pulse" title="Grid Online"></div>
			</div>
			
			<div class="metric-grid">
				<div class="metric-box">
					<span class="label">Logic Authorization</span>
					<div id="auth-box" class="status-badge status-wait">AWAITING CYCLE</div>
				</div>
				
				<div class="metric-box">
					<span class="label">System Projected Yield</span>
					<div class="value-container" id="yield">0.000000000</div>
				</div>

				<div class="metric-box">
					<span class="label">Account Risk Profile</span>
					<div class="value-container" style="color: var(--text-muted);" id="risk">ANALYZING...</div>
				</div>

				<div class="metric-box">
					<span class="label">Cryptographic Receipt ID</span>
					<div class="value-container" style="font-size: 0.85rem; color: var(--accent);" id="uuid">AWAITING_HASH</div>
				</div>
			</div>
		</div>

		<script>
			setInterval(async () => {
				try {
					const res = await fetch('/api/data');
					const data = await res.json();
					
					if(data && Object.keys(data).length > 0) {
						document.getElementById('uuid').innerText = data.uuid_token;
						
						const auth = data.operational_metrics.gate_authorization;
						const authBox = document.getElementById('auth-box');
						if(auth.includes('EXECUTE')) {
							authBox.innerText = 'APPROVED (EXECUTE_TOKEN)';
							authBox.className = 'status-badge status-exec';
						} else {
							authBox.innerText = 'BLOCKED (HALT_TOKEN)';
							authBox.className = 'status-badge status-halt';
						}
						
						const yieldVal = data.operational_metrics.economic_yield_projection;
						document.getElementById('yield').innerText = yieldVal.toFixed(9);
						
						const risk = data.operational_metrics.risk_profile;
						const vol = data.operational_metrics.volatility_index.toFixed(4);
						document.getElementById('risk').innerText = risk + ' (Volatility: ' + vol + ')';
					}
				} catch (e) {
					console.error("Telemetry link lost.");
				}
			}, 1000);
		</script>
	</body>
	</html>
	`
	w.Write([]byte(html))
}
