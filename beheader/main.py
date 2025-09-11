from fastapi import FastAPI
from typing import Dict, Any
import subprocess

app = FastAPI(title="Beheader Service", version="1.0.0")

@app.post("/create_polyglot")
async def create_polyglot(request: Dict[str, Any]):
    """Simulate polyglot creation using beheader CLI"""
    image_path = request.get("image_path")
    video_path = request.get("video_path")
    output_path = request.get("output_path", "output.mp4")
    
    # This is a mock call to the beheader CLI
    # In a real scenario, you'd need to ensure beheader is installed and its dependencies are met
    command = ["echo", "Simulating beheader command:", "bun", "run", "beheader.js", output_path, image_path, video_path]
    
    try:
        result = subprocess.run(command, capture_output=True, text=True, check=True)
        return {"status": "polyglot_created", "output": result.stdout, "error": result.stderr}
    except subprocess.CalledProcessError as e:
        return {"status": "error", "message": f"Beheader command failed: {e.stderr}"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "beheader"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)