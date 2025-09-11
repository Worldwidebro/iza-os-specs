#!/usr/bin/env python3
"""
IZA OS Monetization System
Unified Stripe integration for all business models

This module provides:
- Subscription management
- Payment processing
- Revenue tracking
- Customer management
- Analytics and reporting
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
from enum import Enum

# Stripe integration
try:
    import stripe
    STRIPE_AVAILABLE = True
except ImportError:
    STRIPE_AVAILABLE = False
    logging.warning("Stripe not available, using mock implementation")

class SubscriptionStatus(Enum):
    ACTIVE = "active"
    CANCELED = "canceled"
    PAST_DUE = "past_due"
    UNPAID = "unpaid"
    TRIALING = "trialing"

class PaymentStatus(Enum):
    SUCCEEDED = "succeeded"
    FAILED = "failed"
    PENDING = "pending"
    CANCELED = "canceled"

@dataclass
class Customer:
    """Customer data structure"""
    id: str
    email: str
    name: str
    business_model: str
    stripe_customer_id: Optional[str] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class Subscription:
    """Subscription data structure"""
    id: str
    customer_id: str
    business_model: str
    plan_name: str
    price_id: str
    status: SubscriptionStatus
    current_period_start: datetime
    current_period_end: datetime
    amount: float
    currency: str = "usd"
    stripe_subscription_id: Optional[str] = None
    created_at: datetime = None

@dataclass
class Payment:
    """Payment data structure"""
    id: str
    customer_id: str
    subscription_id: Optional[str]
    amount: float
    currency: str
    status: PaymentStatus
    stripe_payment_intent_id: Optional[str] = None
    created_at: datetime = None

class MonetizationSystem:
    """
    Unified monetization system for all IZA OS business models
    
    Features:
    - Stripe integration for payments
    - Subscription management
    - Revenue tracking and analytics
    - Customer lifecycle management
    - Automated billing and invoicing
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.db_path = Path("monetization.db")
        
        # Initialize database
        self._init_database()
        
        # Stripe configuration
        self.stripe_secret_key = config.get("stripe_secret_key", "")
        self.stripe_publishable_key = config.get("stripe_publishable_key", "")
        
        if STRIPE_AVAILABLE and self.stripe_secret_key:
            stripe.api_key = self.stripe_secret_key
            self.stripe_enabled = True
        else:
            self.stripe_enabled = False
            self.logger.warning("Stripe not configured, using mock implementation")
        
        # Business model pricing
        self.pricing_plans = self._load_pricing_plans()
        
        # Metrics
        self.metrics = {
            "total_customers": 0,
            "active_subscriptions": 0,
            "monthly_recurring_revenue": 0.0,
            "total_revenue": 0.0,
            "churn_rate": 0.0
        }
    
    def _init_database(self):
        """Initialize SQLite database for monetization"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Customers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id TEXT PRIMARY KEY,
                    email TEXT UNIQUE NOT NULL,
                    name TEXT,
                    business_model TEXT,
                    stripe_customer_id TEXT,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            # Subscriptions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    business_model TEXT,
                    plan_name TEXT,
                    price_id TEXT,
                    status TEXT,
                    current_period_start TIMESTAMP,
                    current_period_end TIMESTAMP,
                    amount REAL,
                    currency TEXT DEFAULT 'usd',
                    stripe_subscription_id TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id)
                )
            """)
            
            # Payments table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS payments (
                    id TEXT PRIMARY KEY,
                    customer_id TEXT,
                    subscription_id TEXT,
                    amount REAL,
                    currency TEXT DEFAULT 'usd',
                    status TEXT,
                    stripe_payment_intent_id TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY (customer_id) REFERENCES customers (id),
                    FOREIGN KEY (subscription_id) REFERENCES subscriptions (id)
                )
            """)
            
            # Revenue analytics table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS revenue_analytics (
                    id TEXT PRIMARY KEY,
                    business_model TEXT,
                    date DATE,
                    revenue REAL,
                    new_customers INTEGER,
                    churned_customers INTEGER,
                    active_subscriptions INTEGER,
                    created_at TIMESTAMP
                )
            """)
            
            conn.commit()
    
    def _load_pricing_plans(self) -> Dict[str, Dict[str, Any]]:
        """Load pricing plans for each business model"""
        return {
            "resume-builder": {
                "free": {
                    "price": 0.0,
                    "features": ["3 resumes per month", "Basic templates"],
                    "stripe_price_id": "price_free"
                },
                "pro": {
                    "price": 29.0,
                    "features": ["Unlimited resumes", "Premium templates", "ATS optimization"],
                    "stripe_price_id": "price_pro_resume"
                },
                "enterprise": {
                    "price": 99.0,
                    "features": ["Everything in Pro", "Team collaboration", "API access"],
                    "stripe_price_id": "price_enterprise_resume"
                }
            },
            "print-on-demand": {
                "starter": {
                    "price": 19.0,
                    "features": ["50 designs per month", "Basic analytics"],
                    "stripe_price_id": "price_starter_pod"
                },
                "professional": {
                    "price": 49.0,
                    "features": ["200 designs per month", "Advanced analytics", "Priority support"],
                    "stripe_price_id": "price_pro_pod"
                },
                "business": {
                    "price": 99.0,
                    "features": ["Unlimited designs", "White-label options", "API access"],
                    "stripe_price_id": "price_business_pod"
                }
            },
            "seo-service": {
                "basic": {
                    "price": 199.0,
                    "features": ["1 website", "Monthly reports", "Basic optimization"],
                    "stripe_price_id": "price_basic_seo"
                },
                "professional": {
                    "price": 499.0,
                    "features": ["3 websites", "Weekly reports", "Advanced optimization"],
                    "stripe_price_id": "price_pro_seo"
                },
                "enterprise": {
                    "price": 999.0,
                    "features": ["10 websites", "Daily reports", "Custom solutions"],
                    "stripe_price_id": "price_enterprise_seo"
                }
            },
            "fitness-coach": {
                "basic": {
                    "price": 19.99,
                    "features": ["Meal planning", "Basic workouts", "Progress tracking"],
                    "stripe_price_id": "price_basic_fitness"
                },
                "premium": {
                    "price": 39.99,
                    "features": ["Everything in Basic", "Personal trainer", "Nutrition coaching"],
                    "stripe_price_id": "price_premium_fitness"
                },
                "elite": {
                    "price": 79.99,
                    "features": ["Everything in Premium", "1-on-1 coaching", "Custom programs"],
                    "stripe_price_id": "price_elite_fitness"
                }
            },
            "youtube-factory": {
                "creator": {
                    "price": 49.0,
                    "features": ["1 channel", "10 videos per month", "Basic analytics"],
                    "stripe_price_id": "price_creator_youtube"
                },
                "producer": {
                    "price": 99.0,
                    "features": ["3 channels", "50 videos per month", "Advanced analytics"],
                    "stripe_price_id": "price_producer_youtube"
                },
                "studio": {
                    "price": 199.0,
                    "features": ["10 channels", "Unlimited videos", "White-label options"],
                    "stripe_price_id": "price_studio_youtube"
                }
            }
        }
    
    async def create_customer(self, customer_data: Dict[str, Any]) -> Customer:
        """
        Create a new customer
        
        Agent-S Task: customer_onboarding_agent
        """
        self.logger.info(f"Creating customer: {customer_data.get('email', 'Unknown')}")
        
        customer = Customer(
            id=str(uuid.uuid4()),
            email=customer_data.get("email", ""),
            name=customer_data.get("name", ""),
            business_model=customer_data.get("business_model", ""),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Create Stripe customer if enabled
        if self.stripe_enabled:
            try:
                stripe_customer = stripe.Customer.create(
                    email=customer.email,
                    name=customer.name,
                    metadata={
                        "business_model": customer.business_model,
                        "iza_customer_id": customer.id
                    }
                )
                customer.stripe_customer_id = stripe_customer.id
            except Exception as e:
                self.logger.error(f"Error creating Stripe customer: {e}")
        
        # Store customer
        await self._store_customer(customer)
        
        self.logger.info(f"Customer created: {customer.id}")
        return customer
    
    async def _store_customer(self, customer: Customer):
        """Store customer in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO customers 
                (id, email, name, business_model, stripe_customer_id, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                customer.id,
                customer.email,
                customer.name,
                customer.business_model,
                customer.stripe_customer_id,
                customer.created_at,
                customer.updated_at
            ))
            
            conn.commit()
    
    async def create_subscription(self, customer_id: str, plan_name: str, 
                                 business_model: str) -> Subscription:
        """
        Create a subscription for a customer
        
        Agent-S Task: subscription_agent
        """
        self.logger.info(f"Creating subscription for customer {customer_id}")
        
        # Get customer
        customer = await self._get_customer(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Get plan details
        plan_details = self.pricing_plans.get(business_model, {}).get(plan_name)
        if not plan_details:
            raise ValueError(f"Plan {plan_name} not found for business model {business_model}")
        
        # Create subscription
        subscription = Subscription(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            business_model=business_model,
            plan_name=plan_name,
            price_id=plan_details["stripe_price_id"],
            status=SubscriptionStatus.ACTIVE,
            current_period_start=datetime.now(),
            current_period_end=datetime.now() + timedelta(days=30),
            amount=plan_details["price"],
            currency="usd",
            created_at=datetime.now()
        )
        
        # Create Stripe subscription if enabled
        if self.stripe_enabled and customer.stripe_customer_id:
            try:
                stripe_subscription = stripe.Subscription.create(
                    customer=customer.stripe_customer_id,
                    items=[{
                        'price': plan_details["stripe_price_id"],
                    }],
                    metadata={
                        "business_model": business_model,
                        "iza_subscription_id": subscription.id
                    }
                )
                subscription.stripe_subscription_id = stripe_subscription.id
            except Exception as e:
                self.logger.error(f"Error creating Stripe subscription: {e}")
        
        # Store subscription
        await self._store_subscription(subscription)
        
        # Update metrics
        self.metrics["active_subscriptions"] += 1
        self.metrics["monthly_recurring_revenue"] += subscription.amount
        
        self.logger.info(f"Subscription created: {subscription.id}")
        return subscription
    
    async def _store_subscription(self, subscription: Subscription):
        """Store subscription in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO subscriptions 
                (id, customer_id, business_model, plan_name, price_id, status,
                 current_period_start, current_period_end, amount, currency,
                 stripe_subscription_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                subscription.id,
                subscription.customer_id,
                subscription.business_model,
                subscription.plan_name,
                subscription.price_id,
                subscription.status.value,
                subscription.current_period_start,
                subscription.current_period_end,
                subscription.amount,
                subscription.currency,
                subscription.stripe_subscription_id,
                subscription.created_at
            ))
            
            conn.commit()
    
    async def process_payment(self, customer_id: str, amount: float, 
                            subscription_id: Optional[str] = None) -> Payment:
        """
        Process a payment for a customer
        
        Agent-S Task: payment_processor_agent
        """
        self.logger.info(f"Processing payment for customer {customer_id}: ${amount}")
        
        # Get customer
        customer = await self._get_customer(customer_id)
        if not customer:
            raise ValueError(f"Customer {customer_id} not found")
        
        # Create payment record
        payment = Payment(
            id=str(uuid.uuid4()),
            customer_id=customer_id,
            subscription_id=subscription_id,
            amount=amount,
            currency="usd",
            status=PaymentStatus.PENDING,
            created_at=datetime.now()
        )
        
        # Process payment with Stripe if enabled
        if self.stripe_enabled and customer.stripe_customer_id:
            try:
                payment_intent = stripe.PaymentIntent.create(
                    amount=int(amount * 100),  # Convert to cents
                    currency='usd',
                    customer=customer.stripe_customer_id,
                    metadata={
                        "iza_payment_id": payment.id,
                        "business_model": customer.business_model
                    }
                )
                
                payment.stripe_payment_intent_id = payment_intent.id
                
                if payment_intent.status == 'succeeded':
                    payment.status = PaymentStatus.SUCCEEDED
                else:
                    payment.status = PaymentStatus.FAILED
                    
            except Exception as e:
                self.logger.error(f"Error processing Stripe payment: {e}")
                payment.status = PaymentStatus.FAILED
        else:
            # Mock payment processing
            payment.status = PaymentStatus.SUCCEEDED
        
        # Store payment
        await self._store_payment(payment)
        
        # Update metrics
        if payment.status == PaymentStatus.SUCCEEDED:
            self.metrics["total_revenue"] += amount
        
        self.logger.info(f"Payment processed: {payment.id} - {payment.status.value}")
        return payment
    
    async def _store_payment(self, payment: Payment):
        """Store payment in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO payments 
                (id, customer_id, subscription_id, amount, currency, status,
                 stripe_payment_intent_id, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                payment.id,
                payment.customer_id,
                payment.subscription_id,
                payment.amount,
                payment.currency,
                payment.status.value,
                payment.stripe_payment_intent_id,
                payment.created_at
            ))
            
            conn.commit()
    
    async def cancel_subscription(self, subscription_id: str) -> bool:
        """
        Cancel a subscription
        
        Agent-S Task: subscription_manager_agent
        """
        self.logger.info(f"Canceling subscription: {subscription_id}")
        
        # Get subscription
        subscription = await self._get_subscription(subscription_id)
        if not subscription:
            raise ValueError(f"Subscription {subscription_id} not found")
        
        # Cancel Stripe subscription if enabled
        if self.stripe_enabled and subscription.stripe_subscription_id:
            try:
                stripe.Subscription.modify(
                    subscription.stripe_subscription_id,
                    cancel_at_period_end=True
                )
            except Exception as e:
                self.logger.error(f"Error canceling Stripe subscription: {e}")
        
        # Update subscription status
        subscription.status = SubscriptionStatus.CANCELED
        
        # Store updated subscription
        await self._store_subscription(subscription)
        
        # Update metrics
        self.metrics["active_subscriptions"] -= 1
        self.metrics["monthly_recurring_revenue"] -= subscription.amount
        
        self.logger.info(f"Subscription canceled: {subscription_id}")
        return True
    
    async def _get_customer(self, customer_id: str) -> Optional[Customer]:
        """Get customer from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM customers WHERE id = ?", (customer_id,))
            row = cursor.fetchone()
            
            if row:
                return Customer(
                    id=row[0],
                    email=row[1],
                    name=row[2],
                    business_model=row[3],
                    stripe_customer_id=row[4],
                    created_at=datetime.fromisoformat(row[5]),
                    updated_at=datetime.fromisoformat(row[6])
                )
            
            return None
    
    async def _get_subscription(self, subscription_id: str) -> Optional[Subscription]:
        """Get subscription from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM subscriptions WHERE id = ?", (subscription_id,))
            row = cursor.fetchone()
            
            if row:
                return Subscription(
                    id=row[0],
                    customer_id=row[1],
                    business_model=row[2],
                    plan_name=row[3],
                    price_id=row[4],
                    status=SubscriptionStatus(row[5]),
                    current_period_start=datetime.fromisoformat(row[6]),
                    current_period_end=datetime.fromisoformat(row[7]),
                    amount=row[8],
                    currency=row[9],
                    stripe_subscription_id=row[10],
                    created_at=datetime.fromisoformat(row[11])
                )
            
            return None
    
    async def get_revenue_analytics(self, business_model: str = None, 
                                  days: int = 30) -> Dict[str, Any]:
        """
        Get revenue analytics
        
        Agent-S Task: analytics_agent
        """
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Build query
            query = """
                SELECT 
                    DATE(created_at) as date,
                    SUM(amount) as daily_revenue,
                    COUNT(DISTINCT customer_id) as daily_customers
                FROM payments 
                WHERE status = 'succeeded'
                AND created_at >= date('now', '-{} days')
            """.format(days)
            
            if business_model:
                query += " AND customer_id IN (SELECT id FROM customers WHERE business_model = ?)"
                cursor.execute(query, (business_model,))
            else:
                cursor.execute(query)
            
            daily_data = cursor.fetchall()
            
            # Calculate metrics
            total_revenue = sum(row[1] for row in daily_data)
            total_customers = len(set(row[2] for row in daily_data))
            
            # Get subscription metrics
            subscription_query = """
                SELECT COUNT(*), SUM(amount) 
                FROM subscriptions 
                WHERE status = 'active'
            """
            
            if business_model:
                subscription_query += " AND business_model = ?"
                cursor.execute(subscription_query, (business_model,))
            else:
                cursor.execute(subscription_query)
            
            subscription_count, mrr = cursor.fetchone()
            
            return {
                "business_model": business_model or "all",
                "period_days": days,
                "total_revenue": total_revenue,
                "total_customers": total_customers,
                "active_subscriptions": subscription_count or 0,
                "monthly_recurring_revenue": mrr or 0.0,
                "average_revenue_per_customer": total_revenue / max(total_customers, 1),
                "daily_data": [
                    {
                        "date": row[0],
                        "revenue": row[1],
                        "customers": row[2]
                    }
                    for row in daily_data
                ],
                "generated_at": datetime.now()
            }
    
    async def run_automated_billing(self) -> Dict[str, Any]:
        """
        Run automated billing cycle
        
        Agent-S Task: billing_agent
        """
        self.logger.info("Running automated billing cycle...")
        
        billing_results = {
            "started_at": datetime.now(),
            "subscriptions_processed": 0,
            "payments_collected": 0,
            "failed_payments": 0,
            "total_revenue": 0.0,
            "errors": []
        }
        
        try:
            # Get all active subscriptions
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                cursor.execute("""
                    SELECT * FROM subscriptions 
                    WHERE status = 'active' 
                    AND current_period_end <= datetime('now')
                """)
                
                expired_subscriptions = cursor.fetchall()
            
            # Process each expired subscription
            for sub_row in expired_subscriptions:
                try:
                    subscription_id = sub_row[0]
                    customer_id = sub_row[1]
                    amount = sub_row[8]
                    
                    # Process payment
                    payment = await self.process_payment(customer_id, amount, subscription_id)
                    
                    if payment.status == PaymentStatus.SUCCEEDED:
                        billing_results["payments_collected"] += 1
                        billing_results["total_revenue"] += amount
                        
                        # Renew subscription
                        await self._renew_subscription(subscription_id)
                    else:
                        billing_results["failed_payments"] += 1
                        
                        # Mark subscription as past due
                        await self._mark_subscription_past_due(subscription_id)
                    
                    billing_results["subscriptions_processed"] += 1
                    
                except Exception as e:
                    self.logger.error(f"Error processing subscription {subscription_id}: {e}")
                    billing_results["errors"].append(str(e))
            
            billing_results["completed_at"] = datetime.now()
            billing_results["success"] = True
            
            self.logger.info("Automated billing cycle completed")
            
        except Exception as e:
            self.logger.error(f"Error in automated billing cycle: {e}")
            billing_results["errors"].append(str(e))
            billing_results["success"] = False
        
        return billing_results
    
    async def _renew_subscription(self, subscription_id: str):
        """Renew a subscription for another period"""
        subscription = await self._get_subscription(subscription_id)
        if subscription:
            subscription.current_period_start = datetime.now()
            subscription.current_period_end = datetime.now() + timedelta(days=30)
            await self._store_subscription(subscription)
    
    async def _mark_subscription_past_due(self, subscription_id: str):
        """Mark subscription as past due"""
        subscription = await self._get_subscription(subscription_id)
        if subscription:
            subscription.status = SubscriptionStatus.PAST_DUE
            await self._store_subscription(subscription)

# Example usage and testing
async def main():
    """Example usage of the Monetization System"""
    
    # Configuration
    config = {
        "stripe_secret_key": "sk_test_your_stripe_secret_key",
        "stripe_publishable_key": "pk_test_your_stripe_publishable_key"
    }
    
    # Initialize monetization system
    monetization = MonetizationSystem(config)
    
    # Create a customer
    customer_data = {
        "email": "test@example.com",
        "name": "Test Customer",
        "business_model": "resume-builder"
    }
    
    customer = await monetization.create_customer(customer_data)
    
    # Create a subscription
    subscription = await monetization.create_subscription(
        customer.id, "pro", "resume-builder"
    )
    
    # Process a payment
    payment = await monetization.process_payment(
        customer.id, 29.0, subscription.id
    )
    
    print("Customer:", customer.id)
    print("Subscription:", subscription.id)
    print("Payment:", payment.id, payment.status.value)
    
    # Get analytics
    analytics = await monetization.get_revenue_analytics()
    print("\nAnalytics:", json.dumps(analytics, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
