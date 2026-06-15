package main

import (
	"fmt"
	"os"
	"os/exec"
	"os/signal"
	"path/filepath"
	"syscall"
	"time"
)

// The exact sequence of the ZEUS Python nodes
var scripts = []string{"coc.py", "qe.py", "ce.py", "bme.py", "fe.py", "mte.py", "client.py"}
var processes = make(map[string]*exec.Cmd)

func main() {
	fmt.Println("======================================================")
	fmt.Println("      ZEUS GOLANG ORCHESTRATOR (COMPILED WRAPPER)     ")
	fmt.Println("======================================================")

	// Ensure the logs directory exists
	cwd, _ := os.Getwd()
	logDir := filepath.Join(cwd, "logs")
	os.MkdirAll(logDir, os.ModePerm)

	// Listen for Ctrl+C to cleanly kill all Python background processes
	sigs := make(chan os.Signal, 1)
	signal.Notify(sigs, syscall.SIGINT, syscall.SIGTERM)

	go func() {
		<-sigs
		fmt.Println("\n[GO SUPERVISOR] Shutting down all Python nodes safely...")
		for _, cmd := range processes {
			if cmd != nil && cmd.Process != nil {
				cmd.Process.Kill()
			}
		}
		os.Exit(0)
	}()

	// 1. Launch the Center of Command (COC) First
	launchNode("coc.py", logDir)
	time.Sleep(3 * time.Second) // Give the socket time to bind

	// 2. Launch the remaining expert nodes
	for i := 1; i < len(scripts); i++ {
		launchNode(scripts[i], logDir)
		time.Sleep(500 * time.Millisecond)
	}

	fmt.Println("\n[GO SUPERVISOR] Multi-Agent Stack Online.")
	fmt.Println("[GO SUPERVISOR] Open your browser to: http://localhost:8080")
	fmt.Println("[GO SUPERVISOR] Press Ctrl+C to exit.")

	// Keep the Go wrapper running infinitely
	select {}
}

// launchNode runs a Python script in an isolated Goroutine and restarts it if it crashes
func launchNode(script string, logDir string) {
	go func() {
		for {
			logPath := filepath.Join(logDir, script+".log")
			logFile, err := os.OpenFile(logPath, os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0666)
			if err != nil {
				fmt.Printf("[GO SUPERVISOR ERROR] Cannot open log for %s\n", script)
				return
			}

			fmt.Printf("[GO SUPERVISOR] Spawning Node -> %s\n", script)
			
			// Invoke the Python interpreter
			cmd := exec.Command("python3", script)
			cmd.Stdout = logFile
			cmd.Stderr = logFile
			
			processes[script] = cmd
			
			// cmd.Run() blocks until the Python script crashes or exits
			cmd.Run()
			logFile.Close()
			
			fmt.Printf("[GRID ALERT] Node '%s' crashed. Golang reviving...\n", script)
			
			// Patch C: Port Backoff for the COC broker
			if script == "coc.py" {
				time.Sleep(2 * time.Second)
			} else {
				time.Sleep(1 * time.Second)
			}
		}
	}()
}