from fastapi import FastAPI
from typing import Dict, Any

app = FastAPI(title="FileSync Service", version="1.0.0")

@app.post("/transfer")
async def transfer_file(request: Dict[str, Any]):
    """Simulate file transfer"""
    source = request.get("source")
    destination = request.get("destination")
    
    return {"status": "transfer_initiated", "source": source, "destination": destination, "message": "File transfer simulated"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "filesync"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)