import argparse
import sys
import httpx

BASE_URL = "http://localhost:8000"


def inject_fault(scenario: str):
    print(f"\n[!] Triggering fault injection scenario: {scenario} ...")

    endpoints = {
        "scenario_01_memory_leak": "/fault/memory-leak",
        "scenario_02_error_spike": "/fault/error-spike",
        "scenario_03_latency_spike": "/fault/latency-spike",
        "reset": "/fault/reset",
    }

    endpoint = endpoints.get(scenario)
    if not endpoint:
        print(f"Unknown scenario '{scenario}'. Available options: {list(endpoints.keys())}")
        sys.exit(1)

    url = f"{BASE_URL}{endpoint}"
    try:
        with httpx.Client(timeout=5.0) as client:
            resp = client.post(url)
            resp.raise_for_status()
            print(f"[OK] Response ({resp.status_code}): {resp.json()}")
            print("[INFO] Check Prometheus at http://localhost:9090/alerts to see the alert firing in ~5-10 seconds.")
    except httpx.ConnectError:
        print(f"[ERROR] Could not connect to sample-app at {BASE_URL}. Ensure the container is running.")
        sys.exit(1)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Nightwatch SRE Fault Injector CLI")
    parser.add_argument(
        "--scenario",
        default="scenario_01_memory_leak",
        choices=["scenario_01_memory_leak", "scenario_02_error_spike", "scenario_03_latency_spike", "reset"],
        help="Failure scenario to trigger",
    )
    args = parser.parse_args()
    inject_fault(args.scenario)