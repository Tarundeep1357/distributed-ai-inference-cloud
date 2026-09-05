# Distributed AI Inference Cloud

A small distributed inference system for Iris flower classification. The project exposes a FastAPI service for synchronous and queued predictions, uses Redis as the job broker and status store, and includes a browser-based console for submitting requests and monitoring workers.

## What is included

- FastAPI inference API in `backend/app/`
- A pre-trained scikit-learn `RandomForestClassifier` stored at `backend/models/iris_model.joblib`
- Redis-backed asynchronous job submission and status tracking
- Worker heartbeat registration with a 15-second Redis TTL
- A single-file browser console in `inference-console.html`
- A model-training script in `backend/train_model.py`

## Architecture

```text
Browser console
      |
      v
FastAPI API  ----->  Redis
   |                  |
   |-- /predict       |-- inference_jobs queue
   |-- /jobs/*        |-- job:<id> status keys
   |-- /workers       |-- worker:<id> heartbeat keys
                      ^
                      |
                 Inference worker(s)
```

Synchronous requests call the model directly through `POST /predict`. Asynchronous requests are placed on the `inference_jobs` Redis list; a worker consumes the job, updates its status, runs inference, and removes the completed job from its processing list.

## Requirements

- Python 3.10 or newer
- Redis running on `localhost:6379`
- A modern browser for the console

Python dependencies are pinned in [`backend/requirements.txt`](backend/requirements.txt).

## Setup

From the project root:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r backend\requirements.txt
```

Start Redis separately. For example, with Docker:

```powershell
docker run --name inference-redis -p 6379:6379 -d redis:7-alpine
```

The application currently uses a fixed Redis connection to `localhost` on port `6379`; there are no environment variables for Redis configuration yet.

## Run the API

Run these commands from the `backend` directory so the `app` package resolves correctly:

```powershell
Set-Location backend
uvicorn app.main:app --reload
```

The API is available at `http://localhost:8000`. FastAPI's interactive documentation is available at [`http://localhost:8000/docs`](http://localhost:8000/docs).

## Train or regenerate the model

The checked-in model is trained on scikit-learn's built-in Iris dataset. To regenerate it:

```powershell
Set-Location backend
python train_model.py
```

This creates or replaces `backend/models/iris_model.joblib` using a 100-tree `RandomForestClassifier` with `random_state=42`.

## Run a worker

From the `backend` directory, a worker is intended to be started with:

```powershell
python -m worker.worker
```

Each worker generates an eight-character identifier, publishes an `alive` heartbeat every 5 seconds, and processes jobs from Redis. The API reports workers whose heartbeat keys have not expired through `GET /workers`.

> **Current implementation note:** The worker code currently imports `get_prpcessing_queue`, while `backend/app/redis_client.py` defines `get_processing_queue`. The helper also references `worker_id` instead of its function argument. As a result, the worker requires that existing issue to be corrected before it can start successfully. This README documents the project without changing source code.

## API endpoints

### `GET /`

Returns a basic API message.

### `GET /health`

Returns the service health response:

```json
{"status":"healthy"}
```

### `POST /predict`

Runs inference immediately.

Request body:

```json
{
  "sepal_length": 5.1,
  "sepal_width": 3.5,
  "petal_length": 1.4,
  "petal_width": 0.2
}
```

Response:

```json
{"prediction":0}
```

The model returns the Iris class index `0`, `1`, or `2`:

| Index | Class |
|---:|---|
| 0 | Iris Setosa |
| 1 | Iris Versicolor |
| 2 | Iris Virginica |

### `POST /jobs/predict`

Queues a prediction for a worker and returns a generated job ID:

```json
{"job_id":"<uuid>","status":"queued"}
```

Job status is stored in Redis for up to one hour.

### `GET /jobs/{job_id}`

Returns the current job state. Possible states are `queued`, `processing`, `completed`, and `failed`.

Example completed response:

```json
{
  "job_id": "<uuid>",
  "status": "completed",
  "prediction": 0,
  "error": null
}
```

Unknown job IDs return HTTP `404`.

### `GET /workers`

Returns the number of active workers and their heartbeat information:

```json
{
  "count": 1,
  "workers": [
    {
      "worker_id": "a1b2c3d4",
      "status": "alive",
      "last_heartbeat": 1720000000.0
    }
  ]
}
```

## Use the web console

Open [`inference-console.html`](inference-console.html) in a browser while the API is running. The console:

- Connects to `http://localhost:8000` by default
- Checks `/health` periodically and displays API connectivity
- Supports sync (`POST /predict`) and async (`POST /jobs/predict`) modes
- Polls async jobs through `GET /jobs/{job_id}` for up to 60 seconds
- Refreshes the worker list through `/workers` every 4 seconds
- Maps prediction indexes to the three Iris class names

If the browser blocks requests from the local HTML file, serve the project directory with a simple static server or provide CORS support in the API configuration.

## Redis keys and queues

| Key or queue | Purpose |
|---|---|
| `inference_jobs` | Waiting inference jobs |
| `inference_processing:<worker_id>` | Jobs currently being processed by a worker |
| `job:<job_id>` | Job status, prediction, and error data; expires after 1 hour |
| `worker:<worker_id>` | Worker heartbeat data; expires after 15 seconds |

## Project layout

```text
.
├── backend
│   ├── app
│   │   ├── main.py          # FastAPI routes
│   │   ├── model_service.py # Loads the joblib model and predicts
│   │   ├── redis_client.py  # Redis connection and key helpers
│   │   └── schemas.py       # Pydantic request/response models
│   ├── models
│   │   └── iris_model.joblib
│   ├── train_model.py       # Iris model training script
│   ├── requirements.txt
│   └── worker
│       └── worker.py        # Heartbeat and queue consumer
├── inference-console.html   # Browser dashboard
└── README.md
```

## Current scope

This is an early version (`0.1.0`) intended to demonstrate distributed inference fundamentals: model serving, Redis queues, asynchronous job state, worker liveness, and a lightweight monitoring console. Authentication, configurable service settings, durable retry/recovery handling, automated tests, and production deployment configuration are not included yet.
