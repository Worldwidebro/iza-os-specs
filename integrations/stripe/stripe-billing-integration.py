#!/usr/bin/env python3
"""
Stripe Usage-Based Billing Integration
Implementation of Improvement #21
"""

import stripe
import os
from datetime import datetime
import json

class StripeBillingIntegration:
    def __init__(self):
        stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
        self.webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')
    
    def create_usage_based_product(self, name, description):
        """Create a usage-based product in Stripe"""
        try:
            # Create product
            product = stripe.Product.create(
                name=name,
                description=description,
                type='service'
            )
            
            # Create usage-based price
            price = stripe.Price.create(
                product=product.id,
                unit_amount=100,  # $1.00 per unit
                currency='usd',
                recurring={
                    'interval': 'month',
                    'usage_type': 'metered',
                    'aggregate_usage': 'sum'
                },
                billing_scheme='per_unit'
            )
            
            return {
                'product_id': product.id,
                'price_id': price.id,
                'status': 'success'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def track_usage(self, subscription_item_id, quantity, timestamp=None):
        """Track usage for billing"""
        try:
            usage_record = stripe.SubscriptionItem.create_usage_record(
                subscription_item_id,
                quantity=quantity,
                timestamp=timestamp or int(datetime.now().timestamp()),
                action='increment'
            )
            return {'status': 'success', 'usage_record_id': usage_record.id}
        except Exception as e:
            return {'status': 'error', 'message': str(e)}
    
    def create_customer_subscription(self, customer_email, price_id):
        """Create customer and subscription"""
        try:
            # Create customer
            customer = stripe.Customer.create(email=customer_email)
            
            # Create subscription
            subscription = stripe.Subscription.create(
                customer=customer.id,
                items=[{'price': price_id}],
                payment_behavior='default_incomplete',
                expand=['latest_invoice.payment_intent']
            )
            
            return {
                'customer_id': customer.id,
                'subscription_id': subscription.id,
                'client_secret': subscription.latest_invoice.payment_intent.client_secret,
                'status': 'success'
            }
        except Exception as e:
            return {'status': 'error', 'message': str(e)}

# Auto-setup for all tools
def setup_billing_for_all_tools():
    billing = StripeBillingIntegration()
    
    tools = [
        {'name': 'AI Customer Support', 'description': 'Claude-powered support automation'},
        {'name': 'Content Syndication', 'description': 'Automated content distribution'},
        {'name': 'Compliance Suite', 'description': 'Automated compliance monitoring'},
        {'name': 'Knowledge API', 'description': 'Obsidian knowledge base API'},
        {'name': 'Referral Engine', 'description': 'Viral growth automation'}
    ]
    
    results = []
    for tool in tools:
        result = billing.create_usage_based_product(tool['name'], tool['description'])
        results.append({**tool, **result})
    
    return results

if __name__ == '__main__':
    print('🔄 Setting up Stripe billing for all tools...')
    results = setup_billing_for_all_tools()
    
    for result in results:
        if result['status'] == 'success':
            print(f'✅ {result["name"]}: Product ID {result["product_id"]}')
        else:
            print(f'❌ {result["name"]}: {result["message"]}')
