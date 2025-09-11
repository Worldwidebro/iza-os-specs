from fastapi import FastAPI
from pydantic import BaseModel
from typing import Dict, Any, List
import os
import subprocess
import json

app = FastAPI(title="Apple Notes MCP Server", version="1.0.0")

class SearchRequest(BaseModel):
    query: str
    limit: int = 10

class NoteRequest(BaseModel):
    note_name: str
    folder: str = None

@app.post("/execute")
async def execute_action(request: Dict[str, Any]):
    """Execute MCP action"""
    action = request.get("action")
    parameters = request.get("parameters", {})
    
    if action == "search_notes":
        return await search_notes(parameters.get("query", ""), parameters.get("limit", 10))
    elif action == "get_note_content":
        return await get_note_content(parameters.get("note_name"), parameters.get("folder"))
    elif action == "list_notes":
        return await list_notes(parameters.get("folder"), parameters.get("limit", 20))
    else:
        return {"error": f"Unknown action: {action}"}

async def search_notes(query: str, limit: int = 10):
    """Search notes by content"""
    try:
        # Mock search results
        results = [
            {"name": "Meeting Notes - Q4 Planning", "folder": "Work", "snippet": "Budget discussion and team planning"},
            {"name": "Project Ideas", "folder": "Ideas", "snippet": "AI automation for customer service"},
            {"name": "Shopping List", "folder": "Personal", "snippet": "Groceries and household items"}
        ]
        
        # Filter results based on query
        filtered = [r for r in results if query.lower() in r["snippet"].lower() or query.lower() in r["name"].lower()]
        
        return {"results": filtered[:limit], "total": len(filtered)}
    except Exception as e:
        return {"error": str(e)}

async def get_note_content(note_name: str, folder: str = None):
    """Get content of specific note"""
    try:
        # Mock note content
        mock_content = f"""Content of note: {note_name}
        
This is a sample note from Apple Notes. In a real implementation,
this would connect to the actual Apple Notes app and retrieve
the content of the specified note.

Folder: {folder or 'Notes'}
Last Modified: 2024-01-15 10:30:00
"""
        
        return {"content": mock_content, "note_name": note_name, "folder": folder}
    except Exception as e:
        return {"error": str(e)}

async def list_notes(folder: str = None, limit: int = 20):
    """List all notes in folder"""
    try:
        # Mock notes list
        notes = [
            {"name": "Meeting Notes - Q4 Planning", "folder": "Work", "created": "2024-01-10"},
            {"name": "Project Ideas", "folder": "Ideas", "created": "2024-01-08"},
            {"name": "Shopping List", "folder": "Personal", "created": "2024-01-12"},
            {"name": "Recipe - Pasta", "folder": "Personal", "created": "2024-01-05"},
            {"name": "Travel Plans", "folder": "Personal", "created": "2024-01-15"}
        ]
        
        if folder:
            notes = [n for n in notes if n["folder"] == folder]
        
        return {"notes": notes[:limit], "total": len(notes)}
    except Exception as e:
        return {"error": str(e)}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "service": "apple_notes_mcp"}

@app.get("/capabilities")
async def get_capabilities():
    return {
        "capabilities": ["search_notes", "get_note_content", "list_notes"],
        "description": "Apple Notes MCP Server for note access and search"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
