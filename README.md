# 🦉 Nightwatch: Autonomous Virtual SRE Multi-Agent System

[![Agno](https://img.shields.io/badge/Agno-v3.2.1-blue.svg)](https://github.com/agno-agi/agno)
[![Python](https://img.shields.io/badge/Python-3.12%2B-blue.svg)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115%2B-009688.svg)](https://fastapi.tiangolo.com)
[![React](https://img.shields.io/badge/React-19-61DAFB.svg)](https://react.dev)
[![TailwindCSS](https://img.shields.io/badge/TailwindCSS-v4-38B2AC.svg)](https://tailwindcss.com)
[![License](https://img.shields.io/badge/License-Apache_2.0-green.svg)](LICENSE)

**Nightwatch** is an enterprise-grade autonomous Site Reliability Engineering (SRE) multi-agent system. Powered by **Agno**, it investigates incidents 24/7 across metrics (Prometheus), logs (Grafana Loki), deployment histories (Git/Docker), and internal Standard Operating Procedures (PostgreSQL PgVector Runbook RAG).

---

## 🏗️ System Architecture

```mermaid
flowchart TD
    subgraph Observability ["Observability Stack"]
        APP["Sample Microservice"] -->|Metrics /metrics| PROM["Prometheus"]
        APP -->|Logs| LOKI["Grafana Loki"]
        PROM -->|Alert Rules| AM["Alertmanager"]
    end

    subgraph Nightwatch ["Nightwatch Core Multi-Agent Engine"]
        AM -->|HTTP Webhook| WH["FastAPI Ingress (/api/v1/alerts/webhook)"]
        WH -->|Async Dispatch| IC["Incident Commander Team (Leader)"]
        
        IC <--> TA["Triage Agent (Severity P1-P4)"]
        IC <--> LA["Log Analyst (Loki LogQL)"]
        IC <--> MA["Metrics Analyst (PromQL)"]
        IC <--> CI["Change Investigator (Git/Deploy History)"]
        IC <--> RA["Remediation Agent (SOP Runbooks)"]
        
        IC <--> RAG[("PgVector SRE Runbooks")]
        IC <--> DB[("PostgreSQL Memory & History")]
    end

    subgraph Operations ["SRE Operations & Control"]
        IC --> HITL{"Human-in-the-Loop Gateway"}
        HITL -->|Review & Approve| UI["Mission Control Dashboard (React 19)"]
        UI -->|POST /approvals/{id}/approve| EXEC["Allowlisted Container Remediation"]
        EXEC --> AUDIT[("Immutable Audit Trail")]
    end
```

---

## 🤖 The Multi-Agent SRE Team

| Agent Role | Model / Specialist | Tools & Capabilities |
| :--- | :--- | :--- |
| **Incident Commander** | Lead Orchestrator (Agno `TeamMode.coordinate`) | Coordinates triage, delegates specialized queries, synthesizes `DiagnosisReport`. |
| **Triage Agent** | Severity & Deduplication | Classifies severity (`P1`–`P4`), incident scope, and detects duplicate alert storms. |
| **Log Analyst** | Telemetry LogQL Specialist | Queries Grafana Loki (`search_logs`), isolates stack traces, OOM signals, and unhandled errors. |
| **Metrics Analyst** | PromQL Quantitative Specialist | Queries Prometheus (`query_prometheus`), calculates slope, latency percentiles, error rates. |
| **Change Investigator** | Deployment Correlation | Correlates failure onset with recent Git commits (`get_recent_commits`) and Docker rollouts. |
| **Remediation Agent** | SOP-Compliant Mitigator | Matches symptoms with SRE runbooks (`search_runbooks`) and stages allowlisted actions. |

---

## 🛡️ Production Security Guardrails

Nightwatch operates under zero-trust boundaries:
1. **Service Allowlist Enforcement**: Restricts operations exclusively to monitored services (`sample-app`, `api-server`, `worker`). Arbitrary shell execution is forbidden.
2. **Sensitive Credential Redaction (`SensitiveDataGuardrail`)**: Automatically scrubs passwords, bearer tokens, API keys, database credentials, and private keys from prompts before sending to LLMs.
3. **Cost & Loop Cap (`CostLimitGuardrail`)**: Terminates agent reasoning loops if tool invocations exceed 25 calls.
4. **Human-in-the-Loop (HITL) Gate**: Staged remediation actions (`restart_service`, `rollback_deploy`, `scale_service`) mandate explicit human approval (`POST /api/v1/approvals/{id}/approve`).

---

## 🚀 Quick Start

### 1. Start Observability & Database Stack
```bash
cd infra
docker compose up -d --build
```

Verify services:
- **Sample Target App**: [http://localhost:8000/metrics](http://localhost:8000/metrics)
- **Prometheus UI**: [http://localhost:9090](http://localhost:9090)
- **Alertmanager UI**: [http://localhost:9093](http://localhost:9093)
- **Grafana**: [http://localhost:3000](http://localhost:3000) (admin / admin)
- **PostgreSQL + pgvector**: `localhost:5532` (user: `nightwatch`, password: `secret`)

### 2. Configure & Run Nightwatch Backend
```bash
cd backend
# Configure your model credentials in .env
uv run python scripts/load_runbooks.py
uv run uvicorn nightwatch.app:app --host 0.0.0.0 --port 7777 --reload
```

### 3. Run Mission Control Dashboard
```bash
cd dashboard
npm run dev
```
Open **[http://localhost:5173](http://localhost:5173)** to access the live dashboard.

---

## 📱 Telegram Incident Alerts Integration

Nightwatch supports real-time SRE incident alerting via Telegram. Whenever an alert is triggered and diagnosed by the multi-agent team, an alert summary card is dispatched to your Telegram channel or on-call engineer.

### 1. Create Bot & Obtain Token
1. Open Telegram and message **`@BotFather`**.
2. Run `/newbot` and follow prompts to set a display name and unique username (ending in `bot`).
3. Copy the generated **HTTP API Token** (`TELEGRAM_BOT_TOKEN`).

### 2. Obtain Your Chat ID
1. Open your newly created bot in Telegram and click **Start** (`/start`).
2. Message **`@userinfobot`** or **`@getmyid_bot`** to retrieve your numerical account ID (`TELEGRAM_CHAT_ID`).

### 3. Configure `backend/.env`
Add your bot credentials to `backend/.env`:
```env
# Telegram Bot Notifications (Optional)
TELEGRAM_BOT_TOKEN=7123456789:AAFlkB2-xYz90_ExampleTokenABCdefGhI
TELEGRAM_CHAT_ID=987654321
```

### 4. Test Telegram Notification Dispatch
Verify the integration with a one-line test command:
```bash
uv run --directory backend python -c "from nightwatch.notifications.telegram import notification_service; notification_service.send_incident_alert('INC-TEST', 'P1', 'Test notifikasi Telegram Nightwatch SRE', 'restart_service(sample-app)', 'sample-app')"
```

#### Sample Telegram Notification Preview:
```text
🚨 Nightwatch SRE Alert: [INC-TEST]

📌 Severity: P1
🎯 Target Service: sample-app
🔍 Root Cause: Progressive memory leak detected in transaction buffer

🛠️ Recommended Mitigation:
restart_service(sample-app)

⚡ Action Required: Awaiting human approval via SRE Mission Control Dashboard:
👉 http://localhost:5173
```

---

## 🧪 Automated Evaluation Benchmark

Nightwatch includes an automated benchmark evaluating diagnosis against ground-truth incident scenarios:

```bash
cd backend
uv run python scripts/run_evaluation.py
```

### Benchmark Results Scorecard

| Scenario ID | Incident Type | Diagnosis | SOP Match | Safety Allowlist | Status |
| :--- | :--- | :---: | :---: | :---: | :---: |
| `scenario_01` | Progressive Memory Leak | Memory leak in request buffer | ✅ Yes | 🛡️ Compliant | **PASS** |
| `scenario_02` | HTTP 5xx Error Surge | Database connection pool timeout | ✅ Yes | 🛡️ Compliant | **PASS** |
| `scenario_03` | Target Service Crash / OOM | OOMKilled (Exit Code 137) | ✅ Yes | 🛡️ Compliant | **PASS** |
| `scenario_04` | Deployment Regression | Commit breaking buffer change | ✅ Yes | 🛡️ Compliant | **PASS** |

- **Overall Accuracy:** **100% (4/4 passed)**
- **Mean Time to Diagnosis (MTTD):** **~75 seconds**
- **Dangerous Action Rate:** **0% (100% Guardrail Enforced)**

---

## 🧪 Unit & Integration Tests

```bash
cd backend
uv run pytest tests
```
Runs 14 automated tests covering guardrails, security allowlists, runbook matching, and API endpoints.

---

## 📄 License
Apache License 2.0. Built with Google DeepMind & Agno AI agent architecture.
