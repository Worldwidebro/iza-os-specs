from fastapi import FastAPI, Request, HTTPException
import logging
import httpx
import os
from typing import Dict

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Iza OS - AI Orchestrator",
    description="Central intelligence for orchestrating business and software agents.",
    version="1.0.0"
)

# Activepieces API URL from environment variable
ACTIVEPIECES_API_URL = os.getenv("ACTIVEPIECES_API_URL", "http://activepieces:80/api/v1")
# Activepieces API Key (if required, from .env)
ACTIVEPIECES_API_KEY = os.getenv("ACTIVEPIECES_API_KEY")

 
@app.get("/")
def read_root():
    return {"message": "Iza OS AI Orchestrator is running."}

 
@app.post("/execute")
async def execute_task(request: Request):
    data = await request.json()
    content = data.get("content")
    logger.info(f"Received task for execution: {content}")
    
    # This is where Claude's intelligence would go to analyze the task
    # and decide which Activepieces flow/piece to trigger.
    # For now, we'll mock a direct call to an Activepieces flow.
    
    # Example: Trigger a mock Activepieces flow for financial analysis
    if "financial performance" in content.lower():
        # In a real scenario, you'd have a flow_id for financial analysis
        # You would get this flow_id from Activepieces UI after creating a flow
        flow_id = os.getenv("ACTIVEPIECES_FINANCE_FLOW_ID", "your_financial_analysis_flow_id")
        payload = {"task_description": content, "context": data.get("context", {})}
        try:
            response = await trigger_activepieces_flow(flow_id, payload)
            return {
                "status": "activepieces_flow_triggered",
                "task": content,
                "activepieces_response": response
            }
        except HTTPException as e:
            raise e
    else:
        return {
            "status": "task_received",
            "task": content,
            "result": "Placeholder result: Task received, but no specific Activepieces flow triggered yet."
        }

 
@app.post("/mcp_execute")  # New endpoint for direct MCP execution via Activepieces
async def mcp_execute(request: Request):
    data = await request.json()
    flow_id = data.get("flow_id")
    payload = data.get("payload")
    
    if not flow_id or not payload:
        raise HTTPException(status_code=400, detail="flow_id and payload are required.")
    
    logger.info(f"Executing MCP action via Activepieces flow: {flow_id} with payload: {payload}")
    try:
        response = await trigger_activepieces_flow(flow_id, payload)
        return {
            "status": "mcp_action_executed",
            "flow_id": flow_id,
            "activepieces_response": response
        }
    except HTTPException as e:
        raise e

async def trigger_activepieces_flow(flow_id: str, payload: Dict):
    headers = {"Content-Type": "application/json"}
    if ACTIVEPIECES_API_KEY:
        headers["Authorization"] = f"Bearer {ACTIVEPIECES_API_KEY}"  # Activepieces might use a different auth header
    
    async with httpx.AsyncClient() as client:
        try:
            # Activepieces flow trigger URL might be different, this is a common pattern
            response = await client.post(f"{ACTIVEPIECES_API_URL}/flows/{flow_id}/trigger", json=payload, headers=headers, timeout=30.0)
            response.raise_for_status()  # Raise an exception for 4xx or 5xx responses
            return response.json()
        except httpx.RequestError as exc:
            logger.error(f"An error occurred while requesting {exc.request.url!r}: {exc}")
            raise HTTPException(status_code=500, detail=f"Activepieces request failed: {exc}")
        except httpx.HTTPStatusError as exc:
            logger.error(f"Error response {exc.response.status_code} while requesting {exc.request.url!r}: {exc.response.text}")
            raise HTTPException(status_code=exc.response.status_code, detail=f"Activepieces API error: {exc.response.text}")

 
 
@app.post("/voice")
async def process_voice_command(request: Request):
    await request.json()
    logger.info("Received voice command for processing.")
    # Placeholder for transcription and Claude command parsing
    return {
        "status": "voice_command_received",
        "transcription": "Analyze our Q4 financial performance and suggest optimizations.",
        "response": "Placeholder: Analyzing financials now. I will provide a report shortly."
    }

 
 
@app.post("/agents/create")
async def create_agent(request: Request):
    data = await request.json()
    domain = data.get("domain")
    requirements = data.get("requirements")
    logger.info(f"Received request to create a new agent in domain: {domain}")
    # Placeholder for Auto-Agent Factory logic
    return {
        "status": "agent_creation_request_received",
        "domain": domain,
        "agent_id": "agent_12345",
        "message": f"A new {domain} agent is being generated and deployed.",
        "requirements": requirements,
    }


 
@app.get("/system/status")
def get_system_status():
    logger.info("System status requested.")
    # Placeholder for system health and monitoring data
    return {
        "status": "all_systems_operational",
        "timestamp": "2025-09-10T10:00:00Z",
        "active_agents": 5,
        "cpu_load": "15%",
        "memory_usage": "2.5GB / 16GB"
    }

 
@app.post("/transfer_file")
async def transfer_file(request: Request):
    data = await request.json()
    source = data.get("source")
    destination = data.get("destination")
    logger.info(f"Received request to transfer file from {source} to {destination}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://filesync:8000/transfer", json={"source": source, "destination": destination})
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"FileSync request failed: {exc}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"FileSync API error: {exc.response.text}")

 
@app.post("/create_polyglot")
async def create_polyglot(request: Request):
    data = await request.json()
    image_path = data.get("image_path")
    video_path = data.get("video_path")
    output_path = data.get("output_path")
    logger.info(f"Received request to create polyglot from {image_path} and {video_path}")
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("http://beheader:8000/create_polyglot", json={"image_path": image_path, "video_path": video_path, "output_path": output_path})
            response.raise_for_status()
            return response.json()
    except httpx.RequestError as exc:
        raise HTTPException(status_code=500, detail=f"Beheader request failed: {exc}")
    except httpx.HTTPStatusError as exc:
        raise HTTPException(status_code=exc.response.status_code, detail=f"Beheader API error: {exc.response.text}")

 
@app.get("/system/health")
def get_system_health():
    # For Prometheus scraping
    return {"status": "ok"}
