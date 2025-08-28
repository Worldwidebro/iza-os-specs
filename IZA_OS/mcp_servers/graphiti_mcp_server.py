#!/usr/bin/env python3
"""
Graphiti MCP Server for IZA OS
Knowledge graph operations and business intelligence
"""

import asyncio
import json
import logging
from typing import Any, Dict, List, Optional
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
from datetime import datetime

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Graphiti MCP Server - IZA OS", version="1.0.0")

class GraphQuery(BaseModel):
    query: str
    parameters: Dict[str, Any] = {}
    business_context: Optional[str] = None

class GraphResponse(BaseModel):
    success: bool
    data: List[Dict[str, Any]]
    insights: List[str]
    revenue_opportunities: List[Dict[str, Any]]

class BusinessNode(BaseModel):
    business_id: str
    business_type: str
    revenue: float
    status: str
    connections: List[str]
    metrics: Dict[str, Any]

class BusinessConnection(BaseModel):
    source: str
    target: str
    relationship: str
    strength: float

# Simulated knowledge graph data
KNOWLEDGE_GRAPH = {
    "businesses": {
        "credit_repair_001": {
            "business_id": "credit_repair_001",
            "business_type": "credit_repair",
            "revenue": 1500.0,
            "status": "active",
            "connections": ["lead_gen_001", "payment_processor_001"],
            "metrics": {
                "customers": 45,
                "conversion_rate": 0.78,
                "avg_revenue_per_customer": 33.33
            }
        },
        "lead_gen_001": {
            "business_id": "lead_gen_001",
            "business_type": "lead_generation",
            "revenue": 2200.0,
            "status": "active",
            "connections": ["credit_repair_001", "saas_platform_001"],
            "metrics": {
                "leads_generated": 156,
                "qualification_rate": 0.65,
                "avg_lead_value": 14.10
            }
        },
        "saas_platform_001": {
            "business_id": "saas_platform_001",
            "business_type": "saas_platform",
            "revenue": 8500.0,
            "status": "active",
            "connections": ["lead_gen_001", "ecommerce_001"],
            "metrics": {
                "subscribers": 89,
                "churn_rate": 0.12,
                "avg_revenue_per_user": 95.51
            }
        }
    },
    "connections": [
        {
            "source": "credit_repair_001",
            "target": "lead_gen_001",
            "relationship": "feeds_leads",
            "strength": 0.85
        },
        {
            "source": "lead_gen_001",
            "target": "saas_platform_001",
            "relationship": "provides_qualified_leads",
            "strength": 0.72
        }
    ]
}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "server": "Graphiti", "version": "1.0.0"}

@app.post("/query", response_model=GraphResponse)
async def query_knowledge_graph(request: GraphQuery):
    """Query the knowledge graph"""
    try:
        logger.info(f"Processing graph query: {request.query}")
        
        # Process different types of queries
        if "revenue" in request.query.lower():
            data = await analyze_revenue_patterns()
            insights = await generate_revenue_insights()
            opportunities = await identify_revenue_opportunities()
        
        elif "connections" in request.query.lower():
            data = await analyze_business_connections()
            insights = await generate_connection_insights()
            opportunities = await identify_connection_opportunities()
        
        elif "performance" in request.query.lower():
            data = await analyze_business_performance()
            insights = await generate_performance_insights()
            opportunities = await identify_performance_opportunities()
        
        else:
            # General query
            data = await general_graph_query(request.query)
            insights = ["General business intelligence available"]
            opportunities = []
        
        return GraphResponse(
            success=True,
            data=data,
            insights=insights,
            revenue_opportunities=opportunities
        )
        
    except Exception as e:
        logger.error(f"Graph query error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/businesses")
async def get_all_businesses():
    """Get all businesses in the knowledge graph"""
    return {
        "success": True,
        "businesses": list(KNOWLEDGE_GRAPH["businesses"].values()),
        "total_count": len(KNOWLEDGE_GRAPH["businesses"]),
        "total_revenue": sum(b["revenue"] for b in KNOWLEDGE_GRAPH["businesses"].values())
    }

@app.get("/business/{business_id}")
async def get_business(business_id: str):
    """Get specific business details"""
    if business_id not in KNOWLEDGE_GRAPH["businesses"]:
        raise HTTPException(status_code=404, detail="Business not found")
    
    business = KNOWLEDGE_GRAPH["businesses"][business_id]
    
    # Find connections
    connections = [
        conn for conn in KNOWLEDGE_GRAPH["connections"]
        if conn["source"] == business_id or conn["target"] == business_id
    ]
    
    return {
        "success": True,
        "business": business,
        "connections": connections
    }

@app.get("/analytics/revenue")
async def get_revenue_analytics():
    """Get revenue analytics across all businesses"""
    businesses = KNOWLEDGE_GRAPH["businesses"]
    
    total_revenue = sum(b["revenue"] for b in businesses.values())
    avg_revenue = total_revenue / len(businesses) if businesses else 0
    
    revenue_by_type = {}
    for business in businesses.values():
        biz_type = business["business_type"]
        if biz_type not in revenue_by_type:
            revenue_by_type[biz_type] = []
        revenue_by_type[biz_type].append(business["revenue"])
    
    revenue_analysis = {
        biz_type: {
            "total": sum(revenues),
            "average": sum(revenues) / len(revenues),
            "count": len(revenues)
        }
        for biz_type, revenues in revenue_by_type.items()
    }
    
    return {
        "success": True,
        "total_revenue": total_revenue,
        "average_revenue": avg_revenue,
        "revenue_by_type": revenue_analysis,
        "business_count": len(businesses)
    }

async def analyze_revenue_patterns():
    """Analyze revenue patterns across businesses"""
    businesses = KNOWLEDGE_GRAPH["businesses"]
    
    patterns = []
    for business in businesses.values():
        patterns.append({
            "business_id": business["business_id"],
            "business_type": business["business_type"],
            "revenue": business["revenue"],
            "revenue_per_customer": business["metrics"].get("avg_revenue_per_customer", 0),
            "efficiency_score": calculate_efficiency_score(business)
        })
    
    return patterns

async def generate_revenue_insights():
    """Generate revenue insights"""
    return [
        "Credit repair businesses show consistent $1500/month revenue",
        "SaaS platforms generate highest revenue per business ($8500/month)",
        "Lead generation feeds other businesses effectively",
        "Cross-business connections increase overall revenue"
    ]

async def identify_revenue_opportunities():
    """Identify revenue opportunities"""
    return [
        {
            "opportunity": "Scale credit repair to 10 businesses",
            "potential_revenue": 15000.0,
            "effort": "medium",
            "timeline": "1 month"
        },
        {
            "opportunity": "Launch 5 SaaS platforms",
            "potential_revenue": 42500.0,
            "effort": "high",
            "timeline": "3 months"
        }
    ]

async def analyze_business_connections():
    """Analyze business connections"""
    return KNOWLEDGE_GRAPH["connections"]

async def generate_connection_insights():
    """Generate connection insights"""
    return [
        "Lead generation feeds credit repair effectively",
        "Strong connections between complementary businesses",
        "Network effect increases overall business value"
    ]

async def identify_connection_opportunities():
    """Identify connection opportunities"""
    return [
        {
            "opportunity": "Connect credit repair with payment processing",
            "potential_revenue": 5000.0,
            "effort": "low",
            "timeline": "2 weeks"
        }
    ]

async def analyze_business_performance():
    """Analyze business performance"""
    businesses = KNOWLEDGE_GRAPH["businesses"]
    
    performance = []
    for business in businesses.values():
        performance.append({
            "business_id": business["business_id"],
            "business_type": business["business_type"],
            "revenue": business["revenue"],
            "metrics": business["metrics"],
            "performance_score": calculate_performance_score(business)
        })
    
    return performance

async def generate_performance_insights():
    """Generate performance insights"""
    return [
        "Credit repair shows 78% conversion rate",
        "Lead generation qualifies 65% of leads",
        "SaaS platform has 12% churn rate (industry average)"
    ]

async def identify_performance_opportunities():
    """Identify performance opportunities"""
    return [
        {
            "opportunity": "Improve credit repair conversion to 85%",
            "potential_revenue": 3000.0,
            "effort": "medium",
            "timeline": "1 month"
        }
    ]

async def general_graph_query(query: str):
    """Handle general graph queries"""
    return [
        {
            "query": query,
            "result": "General business intelligence query processed",
            "available_data": list(KNOWLEDGE_GRAPH["businesses"].keys())
        }
    ]

def calculate_efficiency_score(business: Dict[str, Any]) -> float:
    """Calculate business efficiency score"""
    revenue = business["revenue"]
    customers = business["metrics"].get("customers", 1)
    
    if customers > 0:
        return revenue / customers
    return 0.0

def calculate_performance_score(business: Dict[str, Any]) -> float:
    """Calculate business performance score"""
    revenue = business["revenue"]
    metrics = business["metrics"]
    
    # Simple scoring algorithm
    score = revenue / 1000  # Base score from revenue
    
    if "conversion_rate" in metrics:
        score += metrics["conversion_rate"] * 10
    
    if "avg_revenue_per_customer" in metrics:
        score += metrics["avg_revenue_per_customer"] / 10
    
    return round(score, 2)

@app.get("/capabilities")
async def get_capabilities():
    """Get server capabilities"""
    return {
        "server": "Graphiti",
        "version": "1.0.0",
        "capabilities": [
            "knowledge_graph_queries",
            "business_intelligence",
            "revenue_analytics",
            "connection_analysis",
            "performance_metrics",
            "opportunity_identification"
        ],
        "supported_queries": [
            "revenue analysis",
            "business connections",
            "performance metrics",
            "general intelligence"
        ]
    }

if __name__ == "__main__":
    logger.info("🚀 Starting Graphiti MCP Server for IZA OS...")
    uvicorn.run(app, host="0.0.0.0", port=6333)
