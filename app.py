import socket
import subprocess
import time

import uvicorn


def is_ollama_running(host="localhost", port=11434) -> bool:
    try:
        with socket.create_connection((host, port), timeout=1):
            return True
    except OSError:
        return False


def start_ollama():
    print("Ollama is not running, starting...")
    try:
        subprocess.Popen(
            ["ollama", "serve"],
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
        )
    except FileNotFoundError:
        print(
            "ERROR: 'ollama' command not found. Make sure the Ollama application "
            "is installed and added to your PATH. "
            "(https://ollama.com)"
        )
        return

    for _ in range(30):
        if is_ollama_running():
            print("Ollama is ready.")
            return
        time.sleep(1)

    print("WARNING: Ollama did not start within 30 seconds, proceeding anyway.")


if __name__ == "__main__":
    if is_ollama_running():
        print("Ollama is already running.")
    else:
        start_ollama()

    uvicorn.run(
        "webhook:app",
        host="0.0.0.0",
        port=8002,
        reload=True
    )
