# Distributed AI Inference Cloud

A distributed machine learning inference system built with FastAPI, Redis, and Python.

The project is designed to evolve from a simple ML inference API into a fault-tolerant distributed inference platform where multiple workers can process machine learning jobs asynchronously.

---

## 🚀 Project Overview

In a traditional ML API, a client sends a request and the server immediately runs model inference:

Client → API → ML Model → Response

This approach becomes difficult to scale when many inference requests arrive simultaneously.

This project introduces an asynchronous job-processing architecture:

Client
↓
FastAPI
↓
Redis Job Queue
↓
Inference Worker
↓
ML Model
↓
Job Result

The system also tracks workers using heartbeats and uses Redis processing queues to keep track of jobs currently being processed.

---

## 🎯 Current Goals

The project aims to provide:

- Asynchronous ML inference
- Redis-based job queues
- Multiple inference workers
- Worker health monitoring
- Worker heartbeats
- In-flight job tracking
- Fault recovery
- Retry mechanisms
- Job scheduling
- Model management
- API authentication
- Containerized deployment
- Monitoring and observability
- Cloud deployment

Some of these features are planned and are not implemented yet.

---

# 🏗️ Current Architecture

```text
                         Client
                           │
                           ▼
                    ┌─────────────┐
                    │   FastAPI   │
                    └──────┬──────┘
                           │
                           ▼
                  ┌─────────────────┐
                  │  Redis Waiting  │
                  │      Queue      │
                  └────────┬────────┘
                           │
                         BLMOVE
                           │
              ┌────────────┴────────────┐
              ▼                         ▼
     Processing Queue A        Processing Queue B
              │                         │
              ▼                         ▼
          Worker A                  Worker B
              │                         │
              └────────────┬────────────┘
                           ▼
                      ML Model
