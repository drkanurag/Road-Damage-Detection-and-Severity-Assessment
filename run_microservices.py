"""
Multi-Process Microservices Cluster Orchestrator.
Launches all 5 independent RoadVision AI microservices on their dedicated ports:
  - Detection Service     -> http://127.0.0.1:8001
  - Severity Service      -> http://127.0.0.1:8002
  - Visualization Service -> http://127.0.0.1:8003
  - Reporting Service     -> http://127.0.0.1:8004
  - API Gateway & Web UI  -> http://127.0.0.1:8000
"""

import os
import signal
import subprocess
import sys
import time
from typing import List, Tuple

from services.common.config import (
    DETECTION_PORT,
    GATEWAY_PORT,
    REPORTING_PORT,
    SEVERITY_PORT,
    VISUALIZATION_PORT,
)

SERVICES: List[Tuple[str, str, int]] = [
    ("detection-service", "services.detection_service.app:app", DETECTION_PORT),
    ("severity-service", "services.severity_service.app:app", SEVERITY_PORT),
    ("visualization-service", "services.visualization_service.app:app", VISUALIZATION_PORT),
    ("reporting-service", "services.reporting_service.app:app", REPORTING_PORT),
    ("api-gateway", "services.api_gateway.app:app", GATEWAY_PORT),
]


def main() -> None:
    print("=" * 74)
    print("  ROADVISION AI - DISTRIBUTED MICROSERVICES CLUSTER LAUNCHER")
    print("=" * 74)

    env = os.environ.copy()
    env["ROADVISION_MS_MODE"] = "distributed"

    processes: List[Tuple[str, subprocess.Popen]] = []

    try:
        for name, app_target, port in SERVICES:
            cmd = [
                sys.executable,
                "-m",
                "uvicorn",
                app_target,
                "--host",
                "127.0.0.1",
                "--port",
                str(port),
                "--log-level",
                "warning",
            ]
            proc = subprocess.Popen(cmd, env=env)
            processes.append((name, proc))
            print(f"  [+] Started {name:<24} -> http://127.0.0.1:{port} (PID: {proc.pid})")
            time.sleep(0.3)

        print("-" * 74)
        print(f"  [WEB] Unified Web UI & Gateway : http://127.0.0.1:{GATEWAY_PORT}")
        print(f"  [API] Service Topology Status  : http://127.0.0.1:{GATEWAY_PORT}/api/services/status")
        print("  Press Ctrl+C to stop all microservices gracefully.")
        print("=" * 74)

        while True:
            time.sleep(1.0)
            for name, proc in processes:
                if proc.poll() is not None:
                    print(f"[!] Microservice '{name}' exited with code {proc.returncode}")
                    raise KeyboardInterrupt

    except KeyboardInterrupt:
        print("\n[*] Shutting down microservices cluster...")
    finally:
        for name, proc in processes:
            if proc.poll() is None:
                proc.terminate()
        for name, proc in processes:
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                proc.kill()
        print("[+] All microservices stopped cleanly.")


if __name__ == "__main__":
    main()
