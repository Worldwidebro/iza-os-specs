#!/usr/bin/env python3
"""
IZA OS Business Models Test Suite
Comprehensive testing for all 5 business models

This test suite validates:
- Business model functionality
- API endpoints
- Database operations
- Agent-S workflows
- Monetization integration
- Monitoring systems
"""

import asyncio
import pytest
import requests
import json
import sqlite3
from datetime import datetime
from pathlib import Path
import sys
import os

# Add src to path
sys.path.append(str(Path(__file__).parent.parent / "src"))

# Import business models
from business_models.templates.bm001_resume_builder import ResumeBuilder
from business_models.templates.bm002_etsy_print_on_demand import PrintOnDemandStore
from business_models.templates.bm003_local_seo_service import LocalSEOService
from business_models.templates.bm004_fitness_meal_coach import FitnessMealCoach
from business_models.templates.bm005_youtube_channel_factory import YouTubeChannelFactory

# Import systems
from monetization.monetization_system import MonetizationSystem
from monitoring.monitoring_system import MonitoringSystem

class TestBusinessModels:
    """Test suite for all business models"""
    
    @pytest.fixture
    def config(self):
        """Test configuration"""
        return {
            "test_mode": True,
            "database_path": ":memory:",
            "api_keys": {
                "openai_api_key": "test_key",
                "stripe_secret_key": "sk_test_key",
                "stripe_publishable_key": "pk_test_key"
            }
        }
    
    @pytest.fixture
    def resume_builder(self, config):
        """Resume builder instance"""
        return ResumeBuilder(config)
    
    @pytest.fixture
    def print_on_demand(self, config):
        """Print-on-demand store instance"""
        return PrintOnDemandStore(config)
    
    @pytest.fixture
    def seo_service(self, config):
        """SEO service instance"""
        return LocalSEOService(config)
    
    @pytest.fixture
    def fitness_coach(self, config):
        """Fitness coach instance"""
        return FitnessMealCoach(config)
    
    @pytest.fixture
    def youtube_factory(self, config):
        """YouTube factory instance"""
        return YouTubeChannelFactory(config)
    
    @pytest.fixture
    def monetization_system(self, config):
        """Monetization system instance"""
        return MonetizationSystem(config)
    
    @pytest.fixture
    def monitoring_system(self, config):
        """Monitoring system instance"""
        return MonitoringSystem(config)

class TestBM001ResumeBuilder(TestBusinessModels):
    """Test BM001 - Resume Builder"""
    
    @pytest.mark.asyncio
    async def test_resume_builder_initialization(self, resume_builder):
        """Test resume builder initialization"""
        assert resume_builder is not None
        assert resume_builder.config["test_mode"] is True
    
    @pytest.mark.asyncio
    async def test_resume_generation(self, resume_builder):
        """Test resume generation workflow"""
        # Test data
        resume_data = {
            "name": "John Doe",
            "email": "john@example.com",
            "experience": [
                {
                    "title": "Software Engineer",
                    "company": "Tech Corp",
                    "duration": "2 years",
                    "description": "Developed web applications"
                }
            ],
            "skills": ["Python", "JavaScript", "React"],
            "education": "Bachelor's in Computer Science"
        }
        
        # Generate resume
        result = await resume_builder.generate_resume(resume_data)
        
        assert result is not None
        assert "resume_id" in result
        assert result["status"] == "generated"
    
    @pytest.mark.asyncio
    async def test_ats_optimization(self, resume_builder):
        """Test ATS optimization"""
        job_description = "Looking for a Python developer with React experience"
        
        result = await resume_builder.optimize_for_ats(job_description)
        
        assert result is not None
        assert "optimization_score" in result
        assert result["optimization_score"] > 0
    
    @pytest.mark.asyncio
    async def test_automated_workflow(self, resume_builder):
        """Test automated workflow"""
        result = await resume_builder.run_automated_workflow()
        
        assert result is not None
        assert result["success"] is True
        assert "resumes_generated" in result

class TestBM002PrintOnDemand(TestBusinessModels):
    """Test BM002 - Print-on-Demand Store"""
    
    @pytest.mark.asyncio
    async def test_trend_research(self, print_on_demand):
        """Test trend research functionality"""
        trends = await print_on_demand.research_trends(["motivational", "funny"])
        
        assert trends is not None
        assert len(trends) > 0
        assert all(hasattr(trend, 'phrase') for trend in trends)
    
    @pytest.mark.asyncio
    async def test_design_generation(self, print_on_demand):
        """Test design generation"""
        # Mock trend data
        trends = [
            type('Trend', (), {
                'phrase': 'Test Phrase',
                'category': 'test',
                'related_keywords': ['test', 'design']
            })()
        ]
        
        designs = await print_on_demand.generate_designs(trends, count=1)
        
        assert designs is not None
        assert len(designs) > 0
        assert designs[0].title is not None
    
    @pytest.mark.asyncio
    async def test_order_processing(self, print_on_demand):
        """Test order processing"""
        order_data = {
            "id": "test_order_1",
            "product_id": "test_product_1",
            "customer_email": "test@example.com",
            "quantity": 1,
            "variant": "t-shirt",
            "total_amount": 19.99
        }
        
        result = await print_on_demand.process_order(order_data)
        
        assert result is not None
        assert "success" in result
    
    @pytest.mark.asyncio
    async def test_automated_workflow(self, print_on_demand):
        """Test automated workflow"""
        result = await print_on_demand.run_automated_workflow()
        
        assert result is not None
        assert result["success"] is True
        assert "trends_researched" in result

class TestBM003SEOService(TestBusinessModels):
    """Test BM003 - Local SEO Service"""
    
    @pytest.mark.asyncio
    async def test_client_onboarding(self, seo_service):
        """Test client onboarding"""
        client_data = {
            "business_name": "Test Business",
            "industry": "restaurant",
            "location": "San Francisco, CA",
            "website": "https://testbusiness.com",
            "target_keywords": ["restaurant san francisco", "best food near me"]
        }
        
        client = await seo_service.onboard_client(client_data)
        
        assert client is not None
        assert client.business_name == "Test Business"
        assert client.industry == "restaurant"
    
    @pytest.mark.asyncio
    async def test_seo_audit(self, seo_service):
        """Test SEO audit functionality"""
        # First create a client
        client_data = {
            "business_name": "Test Business",
            "industry": "restaurant",
            "location": "San Francisco, CA",
            "website": "https://testbusiness.com",
            "target_keywords": ["restaurant san francisco"]
        }
        client = await seo_service.onboard_client(client_data)
        
        # Run SEO audit
        audit = await seo_service.perform_seo_audit(client.id)
        
        assert audit is not None
        assert audit.client_id == client.id
        assert audit.priority_score > 0
    
    @pytest.mark.asyncio
    async def test_content_generation(self, seo_service):
        """Test content generation"""
        # Create client and audit first
        client_data = {
            "business_name": "Test Business",
            "industry": "restaurant",
            "location": "San Francisco, CA",
            "website": "https://testbusiness.com",
            "target_keywords": ["restaurant san francisco"]
        }
        client = await seo_service.onboard_client(client_data)
        audit = await seo_service.perform_seo_audit(client.id)
        
        # Generate content
        content_pieces = await seo_service.generate_content(client.id, audit.content_gaps)
        
        assert content_pieces is not None
        assert len(content_pieces) > 0
    
    @pytest.mark.asyncio
    async def test_automated_workflow(self, seo_service):
        """Test automated workflow"""
        # Create client first
        client_data = {
            "business_name": "Test Business",
            "industry": "restaurant",
            "location": "San Francisco, CA",
            "website": "https://testbusiness.com",
            "target_keywords": ["restaurant san francisco"]
        }
        client = await seo_service.onboard_client(client_data)
        
        # Run automated workflow
        result = await seo_service.run_automated_workflow(client.id)
        
        assert result is not None
        assert result["success"] is True
        assert result["client_id"] == client.id

class TestBM004FitnessCoach(TestBusinessModels):
    """Test BM004 - Fitness & Meal Planning Coach"""
    
    @pytest.mark.asyncio
    async def test_user_profile_creation(self, fitness_coach):
        """Test user profile creation"""
        user_data = {
            "name": "Test User",
            "age": 30,
            "gender": "male",
            "height_cm": 175.0,
            "weight_kg": 80.0,
            "fitness_level": "intermediate",
            "goal_type": "weight_loss",
            "dietary_restrictions": ["none"],
            "allergies": [],
            "activity_level": "moderately_active"
        }
        
        user = await fitness_coach.create_user_profile(user_data)
        
        assert user is not None
        assert user.name == "Test User"
        assert user.fitness_level.value == "intermediate"
    
    @pytest.mark.asyncio
    async def test_meal_plan_generation(self, fitness_coach):
        """Test meal plan generation"""
        # Create user first
        user_data = {
            "name": "Test User",
            "age": 30,
            "gender": "male",
            "height_cm": 175.0,
            "weight_kg": 80.0,
            "fitness_level": "intermediate",
            "goal_type": "weight_loss",
            "dietary_restrictions": ["none"],
            "allergies": [],
            "activity_level": "moderately_active"
        }
        user = await fitness_coach.create_user_profile(user_data)
        
        # Generate meal plan
        meal_plan = await fitness_coach.generate_meal_plan(user.id)
        
        assert meal_plan is not None
        assert meal_plan.user_id == user.id
        assert meal_plan.total_calories > 0
    
    @pytest.mark.asyncio
    async def test_workout_plan_generation(self, fitness_coach):
        """Test workout plan generation"""
        # Create user first
        user_data = {
            "name": "Test User",
            "age": 30,
            "gender": "male",
            "height_cm": 175.0,
            "weight_kg": 80.0,
            "fitness_level": "intermediate",
            "goal_type": "weight_loss",
            "dietary_restrictions": ["none"],
            "allergies": [],
            "activity_level": "moderately_active"
        }
        user = await fitness_coach.create_user_profile(user_data)
        
        # Generate workout plan
        workout_plan = await fitness_coach.generate_workout_plan(user.id)
        
        assert workout_plan is not None
        assert workout_plan.user_id == user.id
        assert workout_plan.duration_minutes > 0
    
    @pytest.mark.asyncio
    async def test_automated_workflow(self, fitness_coach):
        """Test automated workflow"""
        # Create user first
        user_data = {
            "name": "Test User",
            "age": 30,
            "gender": "male",
            "height_cm": 175.0,
            "weight_kg": 80.0,
            "fitness_level": "intermediate",
            "goal_type": "weight_loss",
            "dietary_restrictions": ["none"],
            "allergies": [],
            "activity_level": "moderately_active"
        }
        user = await fitness_coach.create_user_profile(user_data)
        
        # Run automated workflow
        result = await fitness_coach.run_automated_workflow(user.id)
        
        assert result is not None
        assert result["success"] is True
        assert result["user_id"] == user.id

class TestBM005YouTubeFactory(TestBusinessModels):
    """Test BM005 - YouTube Channel Factory"""
    
    @pytest.mark.asyncio
    async def test_channel_creation(self, youtube_factory):
        """Test channel creation"""
        channel_data = {
            "name": "Test Channel",
            "niche": "tech",
            "channel_url": "https://youtube.com/@testchannel",
            "api_credentials": {
                "client_id": "test_client_id",
                "client_secret": "test_client_secret"
            },
            "upload_schedule": "weekly",
            "target_keywords": ["programming", "tutorial"]
        }
        
        channel = await youtube_factory.create_channel(channel_data)
        
        assert channel is not None
        assert channel.name == "Test Channel"
        assert channel.niche == "tech"
    
    @pytest.mark.asyncio
    async def test_trend_discovery(self, youtube_factory):
        """Test trend discovery"""
        trends = await youtube_factory.discover_niche_trends("tech")
        
        assert trends is not None
        assert len(trends) > 0
    
    @pytest.mark.asyncio
    async def test_script_generation(self, youtube_factory):
        """Test script generation"""
        # Create channel first
        channel_data = {
            "name": "Test Channel",
            "niche": "tech",
            "channel_url": "https://youtube.com/@testchannel",
            "api_credentials": {},
            "upload_schedule": "weekly",
            "target_keywords": ["programming"]
        }
        channel = await youtube_factory.create_channel(channel_data)
        
        # Generate script
        script = await youtube_factory.generate_video_script(channel.id, "Python Tutorial")
        
        assert script is not None
        assert script.channel_id == channel.id
        assert script.title is not None
    
    @pytest.mark.asyncio
    async def test_automated_workflow(self, youtube_factory):
        """Test automated workflow"""
        # Create channel first
        channel_data = {
            "name": "Test Channel",
            "niche": "tech",
            "channel_url": "https://youtube.com/@testchannel",
            "api_credentials": {},
            "upload_schedule": "weekly",
            "target_keywords": ["programming"]
        }
        channel = await youtube_factory.create_channel(channel_data)
        
        # Run automated workflow
        result = await youtube_factory.run_automated_workflow(channel.id)
        
        assert result is not None
        assert result["success"] is True
        assert result["channel_id"] == channel.id

class TestMonetizationSystem(TestBusinessModels):
    """Test Monetization System"""
    
    @pytest.mark.asyncio
    async def test_customer_creation(self, monetization_system):
        """Test customer creation"""
        customer_data = {
            "email": "test@example.com",
            "name": "Test Customer",
            "business_model": "resume-builder"
        }
        
        customer = await monetization_system.create_customer(customer_data)
        
        assert customer is not None
        assert customer.email == "test@example.com"
        assert customer.business_model == "resume-builder"
    
    @pytest.mark.asyncio
    async def test_subscription_creation(self, monetization_system):
        """Test subscription creation"""
        # Create customer first
        customer_data = {
            "email": "test@example.com",
            "name": "Test Customer",
            "business_model": "resume-builder"
        }
        customer = await monetization_system.create_customer(customer_data)
        
        # Create subscription
        subscription = await monetization_system.create_subscription(
            customer.id, "pro", "resume-builder"
        )
        
        assert subscription is not None
        assert subscription.customer_id == customer.id
        assert subscription.plan_name == "pro"
    
    @pytest.mark.asyncio
    async def test_payment_processing(self, monetization_system):
        """Test payment processing"""
        # Create customer first
        customer_data = {
            "email": "test@example.com",
            "name": "Test Customer",
            "business_model": "resume-builder"
        }
        customer = await monetization_system.create_customer(customer_data)
        
        # Process payment
        payment = await monetization_system.process_payment(customer.id, 29.0)
        
        assert payment is not None
        assert payment.customer_id == customer.id
        assert payment.amount == 29.0
    
    @pytest.mark.asyncio
    async def test_revenue_analytics(self, monetization_system):
        """Test revenue analytics"""
        analytics = await monetization_system.get_revenue_analytics()
        
        assert analytics is not None
        assert "total_revenue" in analytics
        assert "total_customers" in analytics

class TestMonitoringSystem(TestBusinessModels):
    """Test Monitoring System"""
    
    @pytest.mark.asyncio
    async def test_health_checks(self, monitoring_system):
        """Test health checks"""
        health_checks = await monitoring_system.run_health_checks()
        
        assert health_checks is not None
        assert len(health_checks) > 0
    
    @pytest.mark.asyncio
    async def test_performance_metrics(self, monitoring_system):
        """Test performance metrics collection"""
        metrics = await monitoring_system.collect_performance_metrics()
        
        assert metrics is not None
        assert len(metrics) > 0
    
    @pytest.mark.asyncio
    async def test_dashboard_data(self, monitoring_system):
        """Test dashboard data generation"""
        dashboard_data = await monitoring_system.get_dashboard_data()
        
        assert dashboard_data is not None
        assert "timestamp" in dashboard_data
        assert "services" in dashboard_data

class TestIntegration:
    """Integration tests"""
    
    @pytest.mark.asyncio
    async def test_end_to_end_workflow(self):
        """Test end-to-end workflow across all business models"""
        config = {
            "test_mode": True,
            "database_path": ":memory:",
            "api_keys": {"stripe_secret_key": "test_key"}
        }
        
        # Initialize all systems
        monetization = MonetizationSystem(config)
        monitoring = MonitoringSystem(config)
        
        # Test monetization workflow
        customer_data = {
            "email": "integration@example.com",
            "name": "Integration Test",
            "business_model": "resume-builder"
        }
        customer = await monetization.create_customer(customer_data)
        
        subscription = await monetization.create_subscription(
            customer.id, "pro", "resume-builder"
        )
        
        payment = await monetization.process_payment(customer.id, 29.0)
        
        # Test monitoring workflow
        health_checks = await monitoring.run_health_checks()
        metrics = await monitoring.collect_performance_metrics()
        
        # Verify integration
        assert customer is not None
        assert subscription is not None
        assert payment is not None
        assert health_checks is not None
        assert metrics is not None

# Performance tests
class TestPerformance:
    """Performance tests"""
    
    @pytest.mark.asyncio
    async def test_concurrent_operations(self):
        """Test concurrent operations"""
        config = {"test_mode": True, "database_path": ":memory:"}
        
        # Test concurrent customer creation
        monetization = MonetizationSystem(config)
        
        tasks = []
        for i in range(10):
            customer_data = {
                "email": f"test{i}@example.com",
                "name": f"Test Customer {i}",
                "business_model": "resume-builder"
            }
            tasks.append(monetization.create_customer(customer_data))
        
        customers = await asyncio.gather(*tasks)
        
        assert len(customers) == 10
        assert all(customer is not None for customer in customers)

if __name__ == "__main__":
    # Run tests
    pytest.main([__file__, "-v", "--tb=short"])
