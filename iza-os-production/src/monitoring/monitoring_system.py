#!/usr/bin/env python3
"""
IZA OS Monitoring & Analytics System
Production monitoring for all business models

This module provides:
- Health checks and monitoring
- Performance metrics
- Error tracking and alerting
- Business analytics
- Real-time dashboards
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import sqlite3
import uuid
import os
import psutil
import requests
from enum import Enum

class HealthStatus(Enum):
    HEALTHY = "healthy"
    WARNING = "warning"
    CRITICAL = "critical"
    DOWN = "down"

class AlertLevel(Enum):
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

@dataclass
class HealthCheck:
    """Health check data structure"""
    id: str
    service_name: str
    check_type: str
    status: HealthStatus
    response_time_ms: float
    error_message: Optional[str] = None
    timestamp: datetime = None

@dataclass
class PerformanceMetric:
    """Performance metric data structure"""
    id: str
    service_name: str
    metric_name: str
    value: float
    unit: str
    timestamp: datetime = None

@dataclass
class Alert:
    """Alert data structure"""
    id: str
    service_name: str
    alert_level: AlertLevel
    message: str
    resolved: bool = False
    created_at: datetime = None
    resolved_at: Optional[datetime] = None

class MonitoringSystem:
    """
    Comprehensive monitoring system for IZA OS business models
    
    Features:
    - Health checks and uptime monitoring
    - Performance metrics collection
    - Error tracking and alerting
    - Business analytics and reporting
    - Real-time dashboard data
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.db_path = Path("monitoring.db")
        
        # Initialize database
        self._init_database()
        
        # Service configurations
        self.services = {
            "resume-builder": {"port": 8001, "health_endpoint": "/health"},
            "print-on-demand": {"port": 8002, "health_endpoint": "/health"},
            "seo-service": {"port": 8003, "health_endpoint": "/health"},
            "fitness-coach": {"port": 8004, "health_endpoint": "/health"},
            "youtube-factory": {"port": 8005, "health_endpoint": "/health"}
        }
        
        # Alert thresholds
        self.thresholds = {
            "response_time_ms": 1000,
            "cpu_percent": 80,
            "memory_percent": 85,
            "disk_percent": 90,
            "error_rate_percent": 5
        }
        
        # Metrics
        self.metrics = {
            "total_health_checks": 0,
            "failed_health_checks": 0,
            "active_alerts": 0,
            "services_up": 0,
            "services_down": 0
        }
    
    def _init_database(self):
        """Initialize SQLite database for monitoring"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Health checks table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS health_checks (
                    id TEXT PRIMARY KEY,
                    service_name TEXT,
                    check_type TEXT,
                    status TEXT,
                    response_time_ms REAL,
                    error_message TEXT,
                    timestamp TIMESTAMP
                )
            """)
            
            # Performance metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS performance_metrics (
                    id TEXT PRIMARY KEY,
                    service_name TEXT,
                    metric_name TEXT,
                    value REAL,
                    unit TEXT,
                    timestamp TIMESTAMP
                )
            """)
            
            # Alerts table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS alerts (
                    id TEXT PRIMARY KEY,
                    service_name TEXT,
                    alert_level TEXT,
                    message TEXT,
                    resolved BOOLEAN DEFAULT FALSE,
                    created_at TIMESTAMP,
                    resolved_at TIMESTAMP
                )
            """)
            
            # Business metrics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS business_metrics (
                    id TEXT PRIMARY KEY,
                    business_model TEXT,
                    metric_name TEXT,
                    metric_value REAL,
                    timestamp TIMESTAMP
                )
            """)
            
            conn.commit()
    
    async def run_health_checks(self) -> List[HealthCheck]:
        """
        Run health checks for all services
        
        Agent-S Task: health_monitor_agent
        """
        self.logger.info("Running health checks for all services...")
        
        health_checks = []
        
        for service_name, config in self.services.items():
            try:
                health_check = await self._check_service_health(service_name, config)
                health_checks.append(health_check)
                
                # Store health check
                await self._store_health_check(health_check)
                
                # Check for alerts
                await self._check_health_alerts(health_check)
                
            except Exception as e:
                self.logger.error(f"Error checking health for {service_name}: {e}")
                
                # Create failed health check
                failed_check = HealthCheck(
                    id=str(uuid.uuid4()),
                    service_name=service_name,
                    check_type="http",
                    status=HealthStatus.DOWN,
                    response_time_ms=0.0,
                    error_message=str(e),
                    timestamp=datetime.now()
                )
                health_checks.append(failed_check)
                await self._store_health_check(failed_check)
        
        # Update metrics
        self.metrics["total_health_checks"] += len(health_checks)
        self.metrics["failed_health_checks"] += len([h for h in health_checks if h.status != HealthStatus.HEALTHY])
        self.metrics["services_up"] = len([h for h in health_checks if h.status == HealthStatus.HEALTHY])
        self.metrics["services_down"] = len([h for h in health_checks if h.status == HealthStatus.DOWN])
        
        self.logger.info(f"Health checks completed: {len(health_checks)} checks")
        return health_checks
    
    async def _check_service_health(self, service_name: str, config: Dict[str, Any]) -> HealthCheck:
        """Check health of a specific service"""
        start_time = datetime.now()
        
        try:
            # Check HTTP endpoint
            url = f"http://localhost:{config['port']}{config['health_endpoint']}"
            response = requests.get(url, timeout=5)
            
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            
            if response.status_code == 200:
                status = HealthStatus.HEALTHY
                error_message = None
            else:
                status = HealthStatus.WARNING
                error_message = f"HTTP {response.status_code}"
            
        except requests.exceptions.Timeout:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            status = HealthStatus.CRITICAL
            error_message = "Request timeout"
            
        except requests.exceptions.ConnectionError:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            status = HealthStatus.DOWN
            error_message = "Connection refused"
            
        except Exception as e:
            response_time = (datetime.now() - start_time).total_seconds() * 1000
            status = HealthStatus.CRITICAL
            error_message = str(e)
        
        return HealthCheck(
            id=str(uuid.uuid4()),
            service_name=service_name,
            check_type="http",
            status=status,
            response_time_ms=response_time,
            error_message=error_message,
            timestamp=datetime.now()
        )
    
    async def collect_performance_metrics(self) -> List[PerformanceMetric]:
        """
        Collect performance metrics for all services
        
        Agent-S Task: performance_monitor_agent
        """
        self.logger.info("Collecting performance metrics...")
        
        metrics = []
        
        # System metrics
        system_metrics = await self._collect_system_metrics()
        metrics.extend(system_metrics)
        
        # Service-specific metrics
        for service_name in self.services.keys():
            service_metrics = await self._collect_service_metrics(service_name)
            metrics.extend(service_metrics)
        
        # Store metrics
        for metric in metrics:
            await self._store_performance_metric(metric)
        
        self.logger.info(f"Performance metrics collected: {len(metrics)} metrics")
        return metrics
    
    async def _collect_system_metrics(self) -> List[PerformanceMetric]:
        """Collect system-level performance metrics"""
        metrics = []
        timestamp = datetime.now()
        
        # CPU usage
        cpu_percent = psutil.cpu_percent(interval=1)
        metrics.append(PerformanceMetric(
            id=str(uuid.uuid4()),
            service_name="system",
            metric_name="cpu_usage",
            value=cpu_percent,
            unit="percent",
            timestamp=timestamp
        ))
        
        # Memory usage
        memory = psutil.virtual_memory()
        metrics.append(PerformanceMetric(
            id=str(uuid.uuid4()),
            service_name="system",
            metric_name="memory_usage",
            value=memory.percent,
            unit="percent",
            timestamp=timestamp
        ))
        
        # Disk usage
        disk = psutil.disk_usage('/')
        metrics.append(PerformanceMetric(
            id=str(uuid.uuid4()),
            service_name="system",
            metric_name="disk_usage",
            value=(disk.used / disk.total) * 100,
            unit="percent",
            timestamp=timestamp
        ))
        
        return metrics
    
    async def _collect_service_metrics(self, service_name: str) -> List[PerformanceMetric]:
        """Collect service-specific performance metrics"""
        metrics = []
        timestamp = datetime.now()
        
        try:
            # Get service metrics endpoint
            config = self.services[service_name]
            url = f"http://localhost:{config['port']}/metrics"
            
            response = requests.get(url, timeout=5)
            if response.status_code == 200:
                service_metrics = response.json()
                
                for metric_name, value in service_metrics.items():
                    metrics.append(PerformanceMetric(
                        id=str(uuid.uuid4()),
                        service_name=service_name,
                        metric_name=metric_name,
                        value=value,
                        unit="count",
                        timestamp=timestamp
                    ))
            
        except Exception as e:
            self.logger.error(f"Error collecting metrics for {service_name}: {e}")
        
        return metrics
    
    async def _check_health_alerts(self, health_check: HealthCheck):
        """Check if health check results trigger alerts"""
        alerts = []
        
        # Response time alert
        if health_check.response_time_ms > self.thresholds["response_time_ms"]:
            alerts.append(Alert(
                id=str(uuid.uuid4()),
                service_name=health_check.service_name,
                alert_level=AlertLevel.WARNING,
                message=f"High response time: {health_check.response_time_ms:.2f}ms",
                created_at=datetime.now()
            ))
        
        # Service down alert
        if health_check.status == HealthStatus.DOWN:
            alerts.append(Alert(
                id=str(uuid.uuid4()),
                service_name=health_check.service_name,
                alert_level=AlertLevel.CRITICAL,
                message=f"Service is down: {health_check.error_message}",
                created_at=datetime.now()
            ))
        
        # Service critical alert
        elif health_check.status == HealthStatus.CRITICAL:
            alerts.append(Alert(
                id=str(uuid.uuid4()),
                service_name=health_check.service_name,
                alert_level=AlertLevel.ERROR,
                message=f"Service is critical: {health_check.error_message}",
                created_at=datetime.now()
            ))
        
        # Store alerts
        for alert in alerts:
            await self._store_alert(alert)
            self.metrics["active_alerts"] += 1
    
    async def _store_health_check(self, health_check: HealthCheck):
        """Store health check in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO health_checks 
                (id, service_name, check_type, status, response_time_ms, error_message, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                health_check.id,
                health_check.service_name,
                health_check.check_type,
                health_check.status.value,
                health_check.response_time_ms,
                health_check.error_message,
                health_check.timestamp
            ))
            
            conn.commit()
    
    async def _store_performance_metric(self, metric: PerformanceMetric):
        """Store performance metric in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO performance_metrics 
                (id, service_name, metric_name, value, unit, timestamp)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                metric.id,
                metric.service_name,
                metric.metric_name,
                metric.value,
                metric.unit,
                metric.timestamp
            ))
            
            conn.commit()
    
    async def _store_alert(self, alert: Alert):
        """Store alert in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO alerts 
                (id, service_name, alert_level, message, resolved, created_at, resolved_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                alert.id,
                alert.service_name,
                alert.alert_level.value,
                alert.message,
                alert.resolved,
                alert.created_at,
                alert.resolved_at
            ))
            
            conn.commit()
    
    async def get_dashboard_data(self) -> Dict[str, Any]:
        """
        Get data for monitoring dashboard
        
        Agent-S Task: dashboard_agent
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get latest health status for each service
            cursor.execute("""
                SELECT service_name, status, response_time_ms, timestamp
                FROM health_checks 
                WHERE timestamp >= datetime('now', '-1 hour')
                ORDER BY timestamp DESC
            """)
            
            recent_health = cursor.fetchall()
            
            # Get active alerts
            cursor.execute("""
                SELECT service_name, alert_level, message, created_at
                FROM alerts 
                WHERE resolved = FALSE
                ORDER BY created_at DESC
            """)
            
            active_alerts = cursor.fetchall()
            
            # Get performance metrics (last hour)
            cursor.execute("""
                SELECT service_name, metric_name, AVG(value) as avg_value, unit
                FROM performance_metrics 
                WHERE timestamp >= datetime('now', '-1 hour')
                GROUP BY service_name, metric_name
            """)
            
            performance_metrics = cursor.fetchall()
            
            # Calculate uptime
            cursor.execute("""
                SELECT service_name, 
                       COUNT(CASE WHEN status = 'healthy' THEN 1 END) as healthy_checks,
                       COUNT(*) as total_checks
                FROM health_checks 
                WHERE timestamp >= datetime('now', '-24 hours')
                GROUP BY service_name
            """)
            
            uptime_data = cursor.fetchall()
            
            return {
                "timestamp": datetime.now(),
                "services": {
                    service: {
                        "status": status,
                        "response_time": response_time,
                        "last_check": timestamp,
                        "uptime_24h": (healthy_checks / total_checks * 100) if total_checks > 0 else 0
                    }
                    for service, status, response_time, timestamp in recent_health
                    for service_uptime, healthy_checks, total_checks in uptime_data
                    if service == service_uptime
                },
                "alerts": [
                    {
                        "service": service,
                        "level": level,
                        "message": message,
                        "created_at": created_at
                    }
                    for service, level, message, created_at in active_alerts
                ],
                "performance": {
                    service: {
                        metric: {
                            "value": avg_value,
                            "unit": unit
                        }
                        for service_metric, metric, avg_value, unit in performance_metrics
                        if service_metric == service
                    }
                    for service in self.services.keys()
                },
                "system_metrics": {
                    "total_services": len(self.services),
                    "services_up": self.metrics["services_up"],
                    "services_down": self.metrics["services_down"],
                    "active_alerts": self.metrics["active_alerts"]
                }
            }
    
    async def run_automated_monitoring(self) -> Dict[str, Any]:
        """
        Run automated monitoring cycle
        
        Agent-S Task: monitoring_orchestrator_agent
        """
        self.logger.info("Starting automated monitoring cycle...")
        
        monitoring_results = {
            "started_at": datetime.now(),
            "health_checks_run": 0,
            "metrics_collected": 0,
            "alerts_triggered": 0,
            "errors": []
        }
        
        try:
            # Run health checks
            health_checks = await self.run_health_checks()
            monitoring_results["health_checks_run"] = len(health_checks)
            
            # Collect performance metrics
            performance_metrics = await self.collect_performance_metrics()
            monitoring_results["metrics_collected"] = len(performance_metrics)
            
            # Count alerts triggered
            monitoring_results["alerts_triggered"] = self.metrics["active_alerts"]
            
            monitoring_results["completed_at"] = datetime.now()
            monitoring_results["success"] = True
            
            self.logger.info("Automated monitoring cycle completed")
            
        except Exception as e:
            self.logger.error(f"Error in automated monitoring cycle: {e}")
            monitoring_results["errors"].append(str(e))
            monitoring_results["success"] = False
        
        return monitoring_results

# Example usage and testing
async def main():
    """Example usage of the Monitoring System"""
    
    # Configuration
    config = {
        "alert_webhook_url": "https://hooks.slack.com/your-webhook-url",
        "email_alerts": "alerts@yourcompany.com"
    }
    
    # Initialize monitoring system
    monitoring = MonitoringSystem(config)
    
    # Run automated monitoring
    results = await monitoring.run_automated_monitoring()
    
    print("Monitoring Results:")
    print(json.dumps(results, indent=2, default=str))
    
    # Get dashboard data
    dashboard_data = await monitoring.get_dashboard_data()
    
    print("\nDashboard Data:")
    print(json.dumps(dashboard_data, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
