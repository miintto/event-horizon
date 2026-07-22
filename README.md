# Event Horizon

Event Horizon is a lightweight, self-hosted observability platform designed for modern homelabs and small-scale infrastructure.


## 구조

```sh
horizon-api/      # API Server
horizon-web/      # Web Dashboad
horizon-agent/    # Agent
```

## Horizon API

API server

```sh
# Install dependencies
$> cd horizon-api
$> python -m venv .venv
$> uv sync
```

```sh
# Run server
$> uv run uvicorn app.main:app --port 8000
```

## Horizon Web

Web dashboard that provide real-time metrics

```sh
$> cd horizon-web
$> npm install
```

```sh
$> npm run dev
```

## Horizon Agent

Lightweight agents

```sh
# Build
$> cd horizon-agent
$> cargo build --release

# Run
$> ./target/release/horizon-agent config.toml
```
