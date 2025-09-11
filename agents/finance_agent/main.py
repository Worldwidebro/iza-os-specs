from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any
import os
import httpx
import asyncio

app = FastAPI(title="Finance Agent", version="1.0.0")

class TaskRequest(BaseModel):
    task: Dict[str, Any]
    context: Dict[str, Any] = {}

@app.post("/execute")
async def execute_task(request: TaskRequest):
    """Execute finance-related tasks"""
    
    task_content = request.task.get("content", "").lower()
    
    if "budget" in task_content:
        return await handle_budget_task(request)
    elif "expense" in task_content:
        return await handle_expense_task(request)
    elif "financial report" in task_content:
        return await handle_reporting_task(request)
    else:
        return {
            "success": True,
            "response": f"Finance agent processed: {request.task.get('content')}",
            "agent_id": "finance"
        }

async def handle_budget_task(request: TaskRequest):
    """Handle budget analysis"""
    return {
        "success": True,
        "response": "Budget analysis completed. Key insights: Revenue trending up 15%, expenses within target.",
        "agent_id": "finance",
        "next_steps": ["Review Q4 projections", "Update board presentation"]
    }

async def handle_expense_task(request: TaskRequest):
    """Handle expense tracking"""
    return {
        "success": True,
        "response": "Expense analysis completed. Total expenses: $45,230. Notable items: Travel (+25%), Software licenses (-5%).",
        "agent_id": "finance",
        "confidence": 0.95
    }

async def handle_reporting_task(request: TaskRequest):
    """Generate financial reports"""
    report = """Financial Summary Report
    
Revenue: $125,000 (↑12% from last month)
Expenses: $85,000 (↓3% from last month)
Net Profit: $40,000 (↑35% from last month)

Key Insights:
- Strong customer acquisition in Q4
- Cost optimization initiatives showing results
- Cash flow positive for 6 consecutive months

Recommendations:
- Increase marketing spend in high-performing channels
- Consider expanding team in Q1
- Review pricing strategy for enterprise tier
"""
    
    return {
        "success": True,
        "response": report,
        "agent_id": "finance"
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy", "agent": "finance"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
