#!/usr/bin/env python3
"""
AI Boss Holdings - Stripe Webhook Handler
Real-time payment event processing
"""

from flask import Flask, request, jsonify
import stripe
import os
import logging

app = Flask(__name__)
stripe.api_key = os.getenv('STRIPE_SECRET_KEY')
webhook_secret = os.getenv('STRIPE_WEBHOOK_SECRET')

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

 @app.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        logger.error("Invalid payload")
        return jsonify({'error': 'Invalid payload'}), 400
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid signature")
        return jsonify({'error': 'Invalid signature'}), 400
    
    # Handle the event
    if event['type'] == 'payment_intent.succeeded':
        payment_intent = event['data']['object']
        handle_successful_payment(payment_intent)
    elif event['type'] == 'customer.subscription.created':
        subscription = event['data']['object']
        handle_new_subscription(subscription)
    elif event['type'] == 'customer.subscription.updated':
        subscription = event['data']['object']
        handle_subscription_update(subscription)
    elif event['type'] == 'invoice.payment_failed':
        invoice = event['data']['object']
        handle_failed_payment(invoice)
    else:
        logger.info(f"Unhandled event type: {event['type']}")
    
    return jsonify({'status': 'success'})

def handle_successful_payment(payment_intent):
    """Process successful payment"""
    amount = payment_intent['amount'] / 100
    customer = payment_intent.get('customer')
    
    logger.info(f"💰 Payment succeeded: ${amount} from customer {customer}")
    
    # Grant access to AI Boss Holdings platform
    # Update revenue tracking
    # Trigger fulfillment
    
def handle_new_subscription(subscription):
    """Process new subscription"""
    customer_id = subscription['customer']
    status = subscription['status']
    
    logger.info(f"🎯 New subscription: {customer_id} - {status}")
    
    # Grant subscription access
    # Send welcome email
    # Update customer profile

def handle_subscription_update(subscription):
    """Process subscription changes"""
    customer_id = subscription['customer']
    status = subscription['status']
    
    logger.info(f"🔄 Subscription updated: {customer_id} - {status}")

def handle_failed_payment(invoice):
    """Process failed payment"""
    customer_id = invoice['customer']
    amount = invoice['amount_due'] / 100
    
    logger.info(f"❌ Payment failed: ${amount} for customer {customer_id}")
    
    # Implement dunning management
    # Send payment retry email
    # Update customer status

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=4242, debug=True)
