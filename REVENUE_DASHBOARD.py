#!/usr/bin/env python3
"""
🚀 REVENUE TRACKING DASHBOARD - IZA OS EMPIRE
═══════════════════════════════════════════════════════════════
Real-time revenue monitoring and analytics for the 7-day income engine

Features:
- Live revenue tracking
- Service performance analytics  
- Client conversion metrics
- Daily target progress
- Revenue optimization insights

Created: 2024-12-14
Emperor: divinejohns
"""

import asyncio
import json
import os
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Any, Optional
import pandas as pd
import logging

class RevenueDashboard:
    """Real-time revenue tracking and analytics dashboard"""
    
    def __init__(self):
        self.base_path = Path("/Users/divinejohns/memU")
        self.revenue_file = self.base_path / "business_data" / "revenue_tracking.csv"
        self.service_catalog = self.base_path / "IZA_OS_SERVICE_CATALOG.json"
        self.daily_targets = {
            1: 500,   # Day 1: Foundation & First Client
            2: 800,   # Day 2: Service Launch & Scaling
            3: 1200,  # Day 3: Multiple Clients & Workflows
            4: 1800,  # Day 4: Premium Services Deployment
            5: 2500,  # Day 5: Enterprise Outreach
            6: 3500,  # Day 6: Advanced Automation
            7: 5000   # Day 7: Revenue Optimization
        }
        
        # Ensure directories exist
        os.makedirs(self.revenue_file.parent, exist_ok=True)
        
        # Initialize revenue tracking file if it doesn't exist
        if not self.revenue_file.exists():
            self._initialize_revenue_file()
        else:
            # Normalize any legacy/mixed CSV schemas into the new schema
            self._normalize_revenue_csv()
            
        self.logger = self._setup_logging()
    
    def _setup_logging(self):
        """Setup dashboard logging"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - REVENUE_DASH - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.base_path / 'revenue_dashboard.log'),
                logging.StreamHandler()
            ]
        )
        return logging.getLogger(__name__)
    
    def _initialize_revenue_file(self):
        """Initialize revenue tracking CSV file"""
        headers = "date,service_id,client_name,revenue,expenses,profit,status,delivery_time,notes\n"
        with open(self.revenue_file, 'w') as f:
            f.write(headers)
        
        self.logger.info("✅ Revenue tracking file initialized")

    def _normalize_revenue_csv(self):
        """Normalize existing CSV to the new schema.
        Accepts old rows with 6 fields: date,venture_id,revenue,expenses,profit,sector
        And new rows with 9 fields: date,service_id,client_name,revenue,expenses,profit,status,delivery_time,notes
        Rewrites the file with the new header and normalized rows.
        """
        try:
            if not self.revenue_file.exists():
                return
            with open(self.revenue_file, 'r') as f:
                lines = [line.strip() for line in f.readlines() if line.strip()]
            if not lines:
                # Empty file, just write new header
                self._initialize_revenue_file()
                return
            # Detect if header is old schema
            header = lines[0]
            new_header = "date,service_id,client_name,revenue,expenses,profit,status,delivery_time,notes"
            rows = []
            for i, line in enumerate(lines[1:], start=2):
                parts = line.split(',')
                # Old schema len 6
                if len(parts) == 6:
                    date, venture_id, revenue, expenses, profit, sector = parts
                    rows.append([date, venture_id, "", revenue, expenses, profit, "COMPLETED", "", sector])
                # New schema len 9
                elif len(parts) == 9:
                    rows.append(parts)
                else:
                    # Attempt to recover if client_name contains comma(s) without quoting: join extras
                    if len(parts) > 9:
                        # Assume first is date, second is service_id, last 6 are revenue..notes; merge middle into client_name
                        date = parts[0]
                        service_id = parts[1]
                        tail = parts[-7:]  # revenue,expenses,profit,status,delivery_time,notes (notes may still contain commas)
                        client_name = ','.join(parts[2:-7])
                        merged = [date, service_id, client_name] + tail
                        # If still too long, truncate extras into notes
                        if len(merged) > 9:
                            merged = merged[:8] + [','.join(merged[8:])]
                        rows.append(merged)
                    else:
                        # Skip malformed row
                        continue
            # Rewrite file
            with open(self.revenue_file, 'w') as f:
                f.write(new_header + "\n")
                for r in rows:
                    f.write(','.join(str(x) for x in r) + "\n")
        except Exception as e:
            # If normalization fails, leave file as-is and log later when reading
            pass
    
    def add_revenue_entry(self, service_id: str, client_name: str, revenue: float, 
                         expenses: float = 0, status: str = "COMPLETED", 
                         delivery_time: str = "", notes: str = "") -> bool:
        """Add a new revenue entry"""
        try:
            date = datetime.now().strftime('%Y-%m-%d')
            profit = revenue - expenses
            
            entry = f"{date},{service_id},{client_name},{revenue},{expenses},{profit},{status},{delivery_time},{notes}\n"
            
            with open(self.revenue_file, 'a') as f:
                f.write(entry)
            
            self.logger.info(f"💰 Revenue entry added: {client_name} - ${revenue}")
            return True
            
        except Exception as e:
            self.logger.error(f"❌ Failed to add revenue entry: {e}")
            return False
    
    def get_daily_revenue(self, target_date: str = None) -> Dict[str, Any]:
        """Get revenue for a specific day"""
        if target_date is None:
            target_date = datetime.now().strftime('%Y-%m-%d')
        
        try:
            df = pd.read_csv(self.revenue_file, engine='python')
            daily_data = df[df['date'] == target_date]
            
            if daily_data.empty:
                return {
                    "date": target_date,
                    "total_revenue": 0,
                    "total_expenses": 0,
                    "total_profit": 0,
                    "transactions": 0,
                    "services": []
                }
            
            return {
                "date": target_date,
                "total_revenue": daily_data['revenue'].sum(),
                "total_expenses": daily_data['expenses'].sum(),
                "total_profit": daily_data['profit'].sum(),
                "transactions": len(daily_data),
                "services": daily_data.to_dict('records')
            }
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get daily revenue: {e}")
            return {"error": str(e)}
    
    def get_7day_progress(self) -> Dict[str, Any]:
        """Get complete 7-day progress analysis"""
        try:
            df = pd.read_csv(self.revenue_file, engine='python')
            
            # Calculate progress for last 7 days
            end_date = datetime.now()
            start_date = end_date - timedelta(days=7)
            
            progress = {
                "campaign_start": start_date.strftime('%Y-%m-%d'),
                "current_date": end_date.strftime('%Y-%m-%d'),
                "days_completed": 0,
                "total_revenue": 0,
                "total_target": sum(self.daily_targets.values()),
                "daily_breakdown": {},
                "performance_metrics": {},
                "optimization_insights": []
            }
            
            current_revenue = 0
            for day in range(1, 8):
                day_date = start_date + timedelta(days=day-1)
                day_str = day_date.strftime('%Y-%m-%d')
                
                daily_data = df[df['date'] == day_str]
                day_revenue = daily_data['revenue'].sum() if not daily_data.empty else 0
                current_revenue += day_revenue
                
                progress["daily_breakdown"][f"day_{day}"] = {
                    "date": day_str,
                    "target": self.daily_targets[day],
                    "actual": day_revenue,
                    "percentage": (day_revenue / self.daily_targets[day] * 100) if self.daily_targets[day] > 0 else 0,
                    "status": "✅ ACHIEVED" if day_revenue >= self.daily_targets[day] else "🎯 IN PROGRESS"
                }
                
                if day_date.date() <= datetime.now().date():
                    progress["days_completed"] += 1
            
            progress["total_revenue"] = current_revenue
            progress["overall_percentage"] = (current_revenue / progress["total_target"] * 100)
            
            # Calculate performance metrics
            progress["performance_metrics"] = self._calculate_performance_metrics(df)
            
            # Generate optimization insights
            progress["optimization_insights"] = self._generate_optimization_insights(progress)
            
            return progress
            
        except Exception as e:
            self.logger.error(f"❌ Failed to get 7-day progress: {e}")
            return {"error": str(e)}
    
    def _calculate_performance_metrics(self, df: pd.DataFrame) -> Dict[str, Any]:
        """Calculate key performance metrics"""
        if df.empty:
            return {
                "avg_deal_size": 0,
                "conversion_rate": 0,
                "avg_delivery_time": 0,
                "top_services": [],
                "growth_rate": 0
            }
        
        # Top performing services
        service_performance = df.groupby('service_id')['revenue'].sum().sort_values(ascending=False).head(5)
        
        return {
            "avg_deal_size": df['revenue'].mean(),
            "total_clients": df['client_name'].nunique(),
            "avg_profit_margin": ((df['profit'].sum() / df['revenue'].sum()) * 100) if df['revenue'].sum() > 0 else 0,
            "top_services": service_performance.to_dict(),
            "completion_rate": len(df[df['status'] == 'COMPLETED']) / len(df) * 100 if len(df) > 0 else 0
        }
    
    def _generate_optimization_insights(self, progress_data: Dict) -> List[str]:
        """Generate actionable optimization insights"""
        insights = []
        
        total_percentage = progress_data.get("overall_percentage", 0)
        
        if total_percentage < 50:
            insights.append("🚨 URGENT: Revenue below 50% target. Deploy additional agents and increase outreach.")
        elif total_percentage < 75:
            insights.append("⚠️ ATTENTION: Revenue at moderate performance. Focus on higher-value services.")
        else:
            insights.append("✅ EXCELLENT: Revenue on track. Consider scaling to premium services.")
        
        # Service-specific insights
        insights.append("💡 RECOMMENDATION: Prioritize Enterprise AI Transformation ($10K-$50K) services")
        insights.append("🎯 STRATEGY: Use N8N automation for faster client onboarding")
        insights.append("📈 OPTIMIZATION: Deploy Claude Templates for 50% faster delivery")
        
        return insights
    
    def display_dashboard(self):
        """Display comprehensive revenue dashboard"""
        print("🚀 IZA OS REVENUE DASHBOARD")
        print("═" * 80)
        print("💰 7-DAY INCOME GENERATION ENGINE - LIVE ANALYTICS")
        print("═" * 80)
        
        # Get current progress
        progress = self.get_7day_progress()
        today_revenue = self.get_daily_revenue()
        
        # Display 7-day overview
        print(f"\n📊 7-DAY CAMPAIGN OVERVIEW:")
        print(f"  🎯 Total Target: ${progress['total_target']:,}")
        print(f"  💰 Current Revenue: ${progress['total_revenue']:,}")
        print(f"  📈 Progress: {progress['overall_percentage']:.1f}%")
        print(f"  📅 Days Completed: {progress['days_completed']}/7")
        
        # Display daily breakdown
        print(f"\n📅 DAILY PROGRESS BREAKDOWN:")
        for day_key, day_data in progress['daily_breakdown'].items():
            day_num = day_key.split('_')[1]
            print(f"  Day {day_num}: ${day_data['actual']:,}/${day_data['target']:,} ({day_data['percentage']:.1f}%) {day_data['status']}")
        
        # Display today's performance
        print(f"\n📊 TODAY'S PERFORMANCE ({today_revenue['date']}):")
        print(f"  💰 Revenue: ${today_revenue['total_revenue']:,}")
        print(f"  💸 Expenses: ${today_revenue['total_expenses']:,}")
        print(f"  💵 Profit: ${today_revenue['total_profit']:,}")
        print(f"  📋 Transactions: {today_revenue['transactions']}")
        
        # Display performance metrics
        if 'performance_metrics' in progress:
            metrics = progress['performance_metrics']
            print(f"\n📈 PERFORMANCE METRICS:")
            print(f"  💰 Avg Deal Size: ${metrics.get('avg_deal_size', 0):,.2f}")
            print(f"  👥 Total Clients: {metrics.get('total_clients', 0)}")
            print(f"  📊 Profit Margin: {metrics.get('avg_profit_margin', 0):.1f}%")
            print(f"  ✅ Completion Rate: {metrics.get('completion_rate', 0):.1f}%")
        
        # Display top services
        if 'performance_metrics' in progress and 'top_services' in progress['performance_metrics']:
            top_services = progress['performance_metrics']['top_services']
            if top_services:
                print(f"\n🏆 TOP PERFORMING SERVICES:")
                for i, (service_id, revenue) in enumerate(top_services.items(), 1):
                    print(f"  {i}. {service_id}: ${revenue:,}")
        
        # Display optimization insights
        print(f"\n💡 OPTIMIZATION INSIGHTS:")
        for insight in progress['optimization_insights']:
            print(f"  {insight}")
        
        # Display service catalog summary
        self._display_service_catalog_summary()
        
        print(f"\n═" * 80)
        print(f"🎯 NEXT ACTIONS:")
        print(f"  1. Add revenue: dashboard.add_revenue_entry('CI-001', 'Client Name', 2500)")
        print(f"  2. View progress: dashboard.display_dashboard()")
        print(f"  3. Execute next day: python3 7_DAY_INCOME_GENERATION_ENGINE.py --day X")
        print(f"═" * 80)
    
    def _display_service_catalog_summary(self):
        """Display service catalog summary"""
        try:
            if self.service_catalog.exists():
                with open(self.service_catalog, 'r') as f:
                    catalog = json.load(f)
                
                print(f"\n🛍️ SERVICE CATALOG STATUS:")
                total_services = 0
                for category_name, category_data in catalog['service_categories'].items():
                    service_count = len(category_data['services'])
                    total_services += service_count
                    print(f"  📦 {category_data['category_name']}: {service_count} services")
                
                print(f"  🎯 Total Services Available: {total_services}")
                print(f"  💼 Package Deals: {len(catalog['package_deals'])}")
        
        except Exception as e:
            self.logger.error(f"❌ Failed to display service catalog: {e}")
    
    def quick_add_demo_revenue(self):
        """Add demo revenue entries for testing"""
        demo_entries = [
            ("CI-001", "TechCorp Inc", 2500, 200, "COMPLETED", "2 days", "Claude Templates setup for development team"),
            ("BA-001", "StartupXYZ", 5000, 500, "COMPLETED", "5 days", "Complete business automation suite"),
            ("CP-001", "RetailMega", 3500, 300, "IN_PROGRESS", "4 days", "AI chat platform for customer support")
        ]
        
        for entry in demo_entries:
            self.add_revenue_entry(*entry)
        
        print("✅ Demo revenue entries added successfully!")

def main():
    """Main dashboard function"""
    dashboard = RevenueDashboard()
    
    print("🚀 Starting Revenue Dashboard...")
    
    # Check if user wants to add demo data
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--demo":
        dashboard.quick_add_demo_revenue()
    
    # Display the dashboard
    dashboard.display_dashboard()

if __name__ == "__main__":
    main()
