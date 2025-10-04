from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List
import numpy as np

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["POST"],
    allow_headers=["*"],
)

class TelemetryRequest(BaseModel):
    regions: List[str]
    threshold_ms: int

telemetry_data = {
    "emea": [
        {"latency": 150, "uptime": 99.9},
        {"latency": 160, "uptime": 99.7},
        {"latency": 170, "uptime": 99.8},
    ],
    "apac": [
        {"latency": 140, "uptime": 99.85},
        {"latency": 155, "uptime": 99.75},
        {"latency": 165, "uptime": 99.65},
    ],
}

@app.post("/")
async def check_latency(req: TelemetryRequest):
    result = {}
    for region in req.regions:
        records = telemetry_data.get(region, [])
        latencies = [r["latency"] for r in records]
        uptimes = [r["uptime"] for r in records]
        avg_latency = np.mean(latencies) if latencies else None
        p95_latency = np.percentile(latencies, 95) if latencies else None
        avg_uptime = np.mean(uptimes) if uptimes else None
        breaches = sum(l > req.threshold_ms for l in latencies)
        result[region] = {
            "avg_latency": avg_latency,
            "p95_latency": p95_latency,
            "avg_uptime": avg_uptime,
            "breaches": breaches,
        }
    return result
