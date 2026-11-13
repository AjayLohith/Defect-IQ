# Manufacturing Defect-Traceability Solution

A clean, deterministic, containerized manufacturing defect-traceability platform. This solution traces quality defects from final inspection back through production orders, production lots, process steps, machines, and supplier material lots, and forward through containment actions, CAPAs, and verification audits.

---

## Architecture Overview

- **Monorepo Design**: Single repository encapsulating backend, frontend, synthetic data generator, data contracts, and Docker orchestration.
- **Backend**: Python 3.12, FastAPI, Pydantic, SQLAlchemy 2.0, PostgreSQL 16.
- **Frontend**: React JS (`.jsx`), Vite, responsive enterprise UI.
- **Generator**: Fully deterministic synthetic generator using fixed seed `20261022`, base epoch `2026-01-01T00:00:00Z`, and stable derived PRNG sub-seeds.
- **Auditing**: Append-only `StateEvent` logs with sequential integer counters (`event_sequence`) ensuring complete historical auditability.
- **Anomalies**: Five deliberate defect and traceability anomalies with segregated ground-truth labels (`ground_truth.csv`, `ground_truth.json`).
- **Zero-Host Runtimes**: Runs entirely inside Docker containers with an isolated PostgreSQL database.

---

## Directory Structure

```text
manufacturing-traceability/
  README.md
  docker-compose.yml
  .env.example
  .gitignore

  backend/
    Dockerfile
    requirements.txt
    app/
      main.py
      api/
      models/
      schemas/
      services/
      repositories/
      rules/
      validators/
      database/
    scripts/

  frontend/
    Dockerfile
    package.json
    src/
      pages/
      components/
      api/
      types/
      styles/

  generator/
    Dockerfile
    requirements.txt
    src/
      config.py
      ids.py
      master_data.py
      transactions.py
      outcomes.py
      anomalies.py
      exports.py
      manifest.py
      cli.py

  data_contract/
    schema/
    controlled_vocabularies/
    lifecycle_transitions/

  docs/
    data_dictionary.md
    relationship_model.md
    business_rules.md
    anomaly_catalog.md
    architecture.md
    implementation_log.md
    validation_guide.md
    docker_guide.md

  sql/
    schema.sql
    seed.sql
    traceability_queries.sql

  tests/
    unit/
    integration/
    contract/
    reproducibility/
    api/
    frontend/

  artifacts/
    csv/
    json/
    sql/
    ground_truth/
    reports/
    manifest/
```

---

## Quickstart (Docker Only)

### Prerequisites
- Docker Desktop with Docker Compose v2+ installed.

### 1. Environment Setup
```bash
cp .env.example .env
```

### 2. Start Application Stack
To launch the database, backend API, and web interface:
```bash
docker compose --profile app up --build
```
- Web Application: `http://localhost:8080`
- API Health Check: `http://localhost:8080/api/v1/health`

### 3. Generate Synthetic Data
To execute deterministic synthetic generation:
```bash
docker compose --profile tools run --rm generator generate --profile starter --seed 20261022
```

### 4. Safe Teardown
```bash
# Stop containers without deleting volume data
docker compose down

# To reset database volumes (destructive):
docker compose down -v
```

