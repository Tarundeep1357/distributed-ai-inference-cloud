from fastapi import FastAPI

app= FastAPI(title= "Destributed AI Inference Cloud",
            version= "0.1.0")

@app.get("/")

def root():
    return {
        "message": "Distributed AI Inference Cloud API"
    }

@app.get("/health")

def health():
    return {
        "status": "healthy"
    }

