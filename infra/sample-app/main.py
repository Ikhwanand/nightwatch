import logging
import os 
import sys
import time 
from typing import List 
from fastapi import FastAPI, HTTPException, Response, status
from prometheus_client import CONTENT_TYPE_LATEST, Counter, Gauge, Histogram, generate_latest

# Configure structured logging for Loki
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] [api-server] %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger("sample-app")

app = FastAPI(title="Sample Target API Server", version="1.0.0")

# Prometheus Metrics Definitions
REQUEST_COUNT = Counter(
    "sample_app_requests_total",
    "Total HTTP requests handled by the sample app",
    ["method", "endpoint", "status"],
)
REQUEST_LATENCY = Histogram(
    "sample_app_request_latency_seconds",
    "Latency of HTTP requests in seconds",
    ["endpoint"],
)
MEMORY_USAGE = Gauge(
    "sample_app_memory_usage_percent",
    "Simulated container memory consumption percentage",
)

# Simulated in-memory state
memory_leak_buffer: List[bytes] = []
current_memory_percent: float = 35.0 # Normal baseline (35%)
error_rate_active: bool = False 
latency_delay: float = 0.0

MEMORY_USAGE.set(current_memory_percent)


@app.get("/health", status_code=status.HTTP_200_OK)
async def health():
    """Service health check."""
    return {"status": "healthy", "service": "api-server"}


@app.get("/metrics")
async def metrics():
    """Prometheus scrape endpoint."""
    MEMORY_USAGE.set(current_memory_percent)
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/api/v1/checkout")
async def checkout():
    """Simulated business checkout transaction."""
    start_time = time.time()
    endpoint = "/api/v1/checkout"
    
    # Simulated slow response
    if latency_delay > 0:
        time.sleep(latency_delay)
    
    # Simulated error spike
    if error_rate_active:
        REQUEST_COUNT.labels(method="GET", endpoint=endpoint, status="500").inc()
        logger.error("Connection pool exhausted! Failed to acquire database connection for transaction.")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Database connection pool timeout.",
        )
    
    duration = time.time() - start_time
    REQUEST_LATENCY.labels(endpoint=endpoint).observe(duration)
    REQUEST_COUNT.labels(method="GET", endpoint=endpoint, status="200").inc()
    logger.info("Checkout transaction processed successfully.")
    return {"status": "success", "order_id": os.urandom(4).hex()}


# ============================================================================
# FAULT INJECTION ENDPOINTS (For Testing Nightwatch AI Detection)
# ============================================================================


@app.post("/fault/memory-leak")
async def trigger_memory_leak():
    """Simulate rapid memory leak by allocating chunks of RAM and raising metric."""
    global current_memory_percent
    current_memory_percent = 94.5 # Exceeds the 90% alert threshold
    MEMORY_USAGE.set(current_memory_percent)
    
    # Allocate real memory chunk in RAM
    for _ in range(5):
        memory_leak_buffer.append(b"X" * 10_000_000) # ~50MB
    
    logger.warning("CRITICAL: Container memory threshold breached! Memory usage at 94.5%.")
    logger.error("OutOfMemory warning: Buffer allocation failed in thread worker pool.")
    return {"status": "fault_injected", "memory_percent": current_memory_percent}


@app.post("/fault/error-spike")
async def trigger_error_spike():
    """Simulate sudden spike in HTTP 500 errors."""
    global error_rate_active
    error_rate_active = True 
    logger.error("Internal service failure: Downstream payment gateway unreachable.")
    return {"status": "error_spike_enabled"}

@app.post("/fault/latency-spike")
async def trigger_latency_spike():
    """Simulate database latency degradation"""
    global latency_delay
    latency_delay = 3.5 # 3.5 seconds sleep
    logger.warning("Performance alert: High query execution time (>3000ms).")
    return {"status": "latency_spike_enabled", "delay_seconds": latency_delay}


@app.post("/fault/reset")
async def reset_faults():
    """Reset application back to normal healthy baseline."""
    global current_memory_percent, error_rate_active, latency_delay, memory_leak_buffer
    memory_leak_buffer.clear()
    current_memory_percent = 35.0
    error_rate_active = False 
    latency_delay = 0.0
    MEMORY_USAGE.set(current_memory_percent)
    
    logger.info("System state restored to healthy baseline.")
    return {"status": "reset_complete"}