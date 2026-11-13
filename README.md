# TraceFlow: Manufacturing Defect Traceability System

TraceFlow is a full-stack defect traceability system built for discrete manufacturing environments. It provides bidirectional traceability: tracing defective parts backwards from quality inspection to the exact production order, machine, process step, and raw material lots used, and forward to isolate the downstream blast radius across suspect inventory, issue containment actions, and manage corrective actions (CAPA) with mandatory verification.

---

## 1. What the Application Does

In discrete manufacturing, discovering a defective component at final inspection often requires answering two critical questions quickly:
1. **Upstream Root Cause**: Which supplier material lot, machine, and operator produced this defect?
2. **Downstream Blast Radius**: What other work orders and finished assemblies used that same suspect material lot or machine run, and what containment actions must be taken?

TraceFlow solves this by implementing:
- **Bidirectional Traceability**: Upstream tree-traversal from defect to supplier lots, and downstream graph-traversal from suspect lots to affected orders.
- **Bill of Materials (BOM) Reconciliation**: Compares planned component consumption against actual consumed material lots to detect shortages or unauthorized lot usage.
- **Strict Quality Governance (CAPA)**: Prevents premature closure of Corrective and Preventive Actions (CAPA) by enforcing at least one passed verification audit.
- **Append-Only Audit Trail**: Records all entity lifecycle transitions into an immutable `StateEvent` log with sequential integer ordering.
- **Automated Data Validation**: Verifies relational integrity, foreign-key consistency, and quantity balance rules against deterministically generated data.

---

## 2. Tech Stack

- **Backend**: Python 3.12, FastAPI (REST API), SQLAlchemy 2.0 (ORM), Pydantic 2 (Validation), Uvicorn (ASGI)
- **Database**: PostgreSQL 16
- **Frontend**: React 18, Vite, Plain CSS (Minimal, calm, responsive light theme)
- **Web Server & Reverse Proxy**: Nginx (Alpine)
- **Containerization**: Docker & Docker Compose
- **Testing**: Pytest, Requests / HTTPX

---

## 3. Engineering Approach

I approached this project by establishing data contracts and deterministic domain rules first before building the API and user interface:

1. **Deterministic Data Engine First**: Created a data generator driven by a fixed seed (`20261022`) and base epoch (`2026-01-01T00:00:00Z`). All entity IDs, timestamps, and quantities are deterministically generated so tests and exports are 100% reproducible across machines.
2. **Strict Ground-Truth Isolation**: Injected 5 specific manufacturing anomaly scenarios (e.g., non-existent lot, missing BOM consumption, premature CAPA closure). Authoritative ground-truth labels are stored separately in `artifacts/ground_truth/` and are never exposed to operational API routes or UI screens.
3. **Database-Level Integrity**: Enforced integrity at the PostgreSQL schema layer using foreign keys and typed `CHECK` constraints on `state_events` to ensure entity type and entity ID foreign keys strictly match.
4. **Focused Layered Architecture**: Separated concerns cleanly into router endpoints, business rules, repositories, database sessions, and validation engines.
5. **Calm, Functional UI**: Designed a minimal, high-contrast light theme without visual noise, animations, or marketing fluff, focusing purely on operational clarity for plant operators and quality engineers.

---

## 4. System Architecture & Flow

### Lifecycle Mindmap
```text
[External Supplier]
        │
        ▼
 [Material Lot]  (Batch code, received quantity, initial status)
        │
        ├─────────────────────────────┐
        ▼                             ▼
[BOM Consumption]             [Quality Inspection]
(Issued to Work Order)         (Gate check against tolerances)
        │                             │
        ▼                             ▼
[Production Order]  ◄───────  [Defect Discovered]
(Machine + Step routing)       (Code, severity, suspect lot/machine)
                                      │
                         ┌────────────┴────────────┐
                         ▼                         ▼
                [Containment Action]     [Corrective Action (CAPA)]
                (Quarantine, Stop Line)   (Root cause investigation)
                                                   │
                                                   ▼
                                        [Effectiveness Verification]
                                        (Audit proving resolution)
                                                   │
                                                   ▼
                                             [CAPA Closed]
```

### System Architecture
```text
┌────────────────────────────────────────────────────────┐
│               Frontend (React 18 + Nginx)              │
│  Dashboard | Defects | Traceability | BOM | CAPAs      │
└───────────────────────────┬────────────────────────────┘
                            │ Reverse Proxy (:8080/api)
                            ▼
┌────────────────────────────────────────────────────────┐
│               Backend (FastAPI + Uvicorn)              │
│  Routers ──► Services / Business Rules ──► Repositories│
└───────────────────────────┬────────────────────────────┘
                            │ SQLAlchemy 2.0 Connection
                            ▼
┌────────────────────────────────────────────────────────┐
│               Database (PostgreSQL 16)                 │
│  Relational Tables | Typed CHECK Constraints | Events  │
└────────────────────────────────────────────────────────┘
```

---

## 5. Docker Setup & Execution

Everything is containerized. Docker Compose sets up the database, automatically loads the schema and seed data, starts the backend, and serves the frontend.

### 1. Start the Application
From the project root:
```bash
docker compose up -d --build
```

### 2. Access Points
- **Web Application**: [http://localhost:8080](http://localhost:8080)
- **Interactive Swagger API Docs**: [http://localhost:8000/docs](http://localhost:8000/docs)
- **API Health Check**: [http://localhost:8000/api/v1/health](http://localhost:8000/api/v1/health)

### 3. Stop the Application
```bash
docker compose down
```

---

## 6. Testing & Validation

### Run the Full Test Suite
Executes unit, contract, integration, lifecycle, and API endpoint tests:
```bash
docker compose run --rm test
```

### Run Data Validation Engine
Executes all 11 baseline integrity rules and verifies detection of the 5 deliberate anomalies:
```bash
docker compose run --rm validator
```

### Run Frontend Smoke Tests
Verifies critical user workflows (dashboard metrics, upstream trace, downstream blast radius, BOM reconciliation, and CAPA rejection):
```bash
docker compose run --rm --entrypoint "python /app/tests/smoke_frontend.py" test
```

### Run PostgreSQL Traceability Queries
Runs canonical SQL queries directly against the database:
```bash
docker compose run --rm --entrypoint "psql -h db -U traceflow_user -d traceflow_db -f /app/sql/traceability_queries.sql" db-loader
```

---

## 7. Key Features & How to Evaluate Them

### 1. Interactive Swagger UI (`http://localhost:8000/docs`)
You can test the backend directly from the Swagger interactive interface:
- **`GET /api/v1/health`**: Returns engine status and active seed (`20261022`).
- **`GET /api/v1/dashboard/metrics`**: Computes scrap rates, defect distributions, and top high-risk machines.
- **`GET /api/v1/traceability/upstream/{defect_id}`**: Test with `DEF-2026-000001` to view root-cause material lots and machine steps.
- **`GET /api/v1/traceability/downstream/{material_lot_id}`**: Test with `LOT-2026-000001` to view all affected production orders.
- **`POST /api/v1/capas/{capa_id}/close`**: Try closing `CAPA-2026-000005`. The API will reject this with **HTTP 422** (`ERR_CAPA_VERIFICATION_REQUIRED`) because no passed verification exists.

### 2. Operational Frontend (`http://localhost:8080`)
- **Dashboard**: High-level KPIs, defect rate breakdowns, and machine drift indicators.
- **Defects & Containment**: Real-time defect log with action buttons to record lot quarantine or line stops.
- **Traceability Workbench**: Clean, linear upstream genealogy paths and downstream blast-radius cards.
- **Production & BOM**: Work orders with side-by-side BOM requirement vs. actual consumption comparisons.
- **Material Lots**: Lot inventory with quarantine status and supplier details.
- **Corrective Actions (CAPA)**: Workflow tracker showing verification audit status before allowing closure.
- **System Integrity**: View checksum manifests and run the automated data integrity engine.

---

## 8. Business Rules Enforced

- **Mandatory CAPA Verification**: A corrective action cannot transition to `CLOSED` without at least one verification record with result `PASSED`. Attempting to close it prematurely triggers an HTTP 422 error.
- **Append-Only Audit Trail**: Every status change writes an immutable `StateEvent` row with an incremented sequence number. Current state is derived from events, never mutated in place.
- **Quantity Reconciliation**:
  - `inspected_quantity = accepted_quantity + rejected_quantity`
  - `rejected_quantity = reworked_quantity + scrapped_quantity + quarantined_quantity`
  - `received_quantity = available_quantity + consumed_quantity + rejected_quantity + quarantined_quantity`
- **StateEvent Foreign Key Integrity**: A database `CHECK` constraint guarantees that each event references exactly one entity type and ID.
- **Ground Truth Isolation**: Ground-truth anomaly labels are kept in `artifacts/ground_truth/` and are strictly excluded from operational tables and user interfaces.

---

## 9. Project Structure

```text
manufacturing-traceability/
├── backend/          # FastAPI application, database sessions, models, and business rules
├── frontend/         # React 18 JSX frontend, shared components, and Nginx reverse proxy
├── generator/        # Deterministic dataset generation engine and data validator
├── data_contract/    # JSON schema definitions, vocabulary enums, and transition tables
├── docs/             # Technical specifications, data dictionary, rules, and anomaly catalog
├── sql/              # PostgreSQL schema, full seed dataset, and traceability SQL queries
├── tests/            # Automated test suite (unit, contract, integration, api, smoke)
├── artifacts/        # Generated data exports (CSV, JSON, SQL, ground truth, manifests)
├── docker-compose.yml# Container orchestration for app, database, and test runners
├── pytest.ini        # Pytest test configuration
├── run_backend.ps1   # PowerShell helper script for direct local execution
└── README.md         # Project documentation
```

---

## 10. Known Limitations

- **Synthetic Data**: All orders, material lots, and serial numbers are generated for demonstration and testing.
- **Demo Role Selector**: The role switcher in the header is a simulated interface control for demonstrating persona views (Plant Operator, Quality Engineer, Production Planner, IT Admin).
- **Single-Tenant Setup**: Intended for local evaluation without external OAuth2/LDAP infrastructure.

---

## 11. Reproducibility Statement

Data generation in TraceFlow is fully deterministic. Given the master seed `20261022` and base epoch `2026-01-01T00:00:00Z`, the generator produces identical row counts, timestamps, relational keys, and SHA-256 checksums across independent runs and operating systems. All timestamps are calculated from deterministic offsets without using system wall-clock time.
