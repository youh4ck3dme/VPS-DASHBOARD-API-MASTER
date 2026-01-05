# Stripe Subscription Service
# CarScraper Pro plány: FREE, HOBBY (29€), PRO (79€)

import os
import stripe
import logging
from typing import Optional, Dict
from flask import url_for, current_app

logger = logging.getLogger(__name__)


# Stripe Price IDs - nastav v .env alebo vytvor cez Stripe Dashboard
STRIPE_PRICES = {
    'hobby': os.environ.get('STRIPE_PRICE_HOBBY', 'price_hobby_29eur'),
    'pro': os.environ.get('STRIPE_PRICE_PRO', 'price_pro_79eur')
}

PLAN_FEATURES = {
    'free': {
        'name': 'Free',
        'price': 0,
        'scrapes_per_day': 5,
        'telegram': False,
        'ai_analysis': False,
        'api_access': False
    },
    'hobby': {
        'name': 'Hobby',
        'price': 29,
        'scrapes_per_day': 20,
        'telegram': True,
        'ai_analysis': True,
        'api_access': False
    },
    'pro': {
        'name': 'Pro',
        'price': 79,
        'scrapes_per_day': 100,
        'telegram': True,
        'ai_analysis': True,
        'api_access': True
    }
}


def init_stripe(app=None):
    """Inicializuje Stripe s API kľúčom"""
    api_key = None
    if app:
        api_key = app.config.get('STRIPE_SECRET_KEY')
    else:
        api_key = os.environ.get('STRIPE_SECRET_KEY')
    
    if api_key:
        stripe.api_key = api_key
        logger.info("Stripe inicializovaný")
        return True
    else:
        logger.warning("STRIPE_SECRET_KEY nie je nastavený")
        return False


def create_checkout_session(
    user_id: int,
    plan: str,
    success_url: str,
    cancel_url: str
) -> Optional[Dict]:
    """
    Vytvorí Stripe Checkout Session pre subscription
    
    Args:
        user_id: ID používateľa
        plan: 'hobby' alebo 'pro'
        success_url: URL po úspešnej platbe
        cancel_url: URL po zrušení
    
    Returns:
        Dict s checkout session alebo None
    """
    if plan not in ['hobby', 'pro']:
        logger.error(f"Neplatný plán: {plan}")
        return None
    
    price_id = STRIPE_PRICES.get(plan)
    if not price_id or price_id.startswith('price_'):
        # Pre demo účely - vytvor inline price
        logger.warning(f"Používam inline price pre {plan}")
        price_data = {
            'currency': 'eur',
            'unit_amount': PLAN_FEATURES[plan]['price'] * 100,
            'recurring': {'interval': 'month'},
            'product_data': {
                'name': f'CarScraper Pro - {PLAN_FEATURES[plan]["name"]}'
            }
        }
        line_item = {
            'price_data': price_data,
            'quantity': 1
        }
    else:
        line_item = {
            'price': price_id,
            'quantity': 1
        }
    
    try:
        session = stripe.checkout.Session.create(
            mode='subscription',
            line_items=[line_item],
            success_url=success_url + '?session_id={CHECKOUT_SESSION_ID}',
            cancel_url=cancel_url,
            metadata={
                'user_id': str(user_id),
                'plan': plan
            },
            subscription_data={
                'metadata': {
                    'user_id': str(user_id),
                    'plan': plan
                }
            }
        )
        
        logger.info(f"Checkout session vytvorená pre user {user_id}, plán {plan}")
        return {
            'session_id': session.id,
            'url': session.url
        }
    
    except stripe.error.StripeError as e:
        logger.error(f"Stripe error: {e}")
        return None


def handle_webhook_event(payload: bytes, sig_header: str, webhook_secret: str) -> Optional[Dict]:
    """
    Spracuje Stripe webhook event
    
    Returns:
        Dict s event dátami alebo None
    """
    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, webhook_secret
        )
    except ValueError:
        logger.error("Invalid webhook payload")
        return None
    except stripe.error.SignatureVerificationError:
        logger.error("Invalid webhook signature")
        return None
    
    event_type = event['type']
    data = event['data']['object']
    
    logger.info(f"Webhook event: {event_type}")
    
    if event_type == 'checkout.session.completed':
        return {
            'action': 'subscription_created',
            'user_id': data['metadata'].get('user_id'),
            'plan': data['metadata'].get('plan'),
            'subscription_id': data.get('subscription'),
            'customer_id': data.get('customer')
        }
    
    elif event_type == 'customer.subscription.updated':
        return {
            'action': 'subscription_updated',
            'subscription_id': data.get('id'),
            'status': data.get('status'),
            'plan': data['metadata'].get('plan')
        }
    
    elif event_type == 'customer.subscription.deleted':
        return {
            'action': 'subscription_cancelled',
            'subscription_id': data.get('id'),
            'user_id': data['metadata'].get('user_id')
        }
    
    return {'action': 'unknown', 'type': event_type}


def cancel_subscription(subscription_id: str) -> bool:
    """Zruší subscription"""
    try:
        stripe.Subscription.delete(subscription_id)
        logger.info(f"Subscription {subscription_id} zrušená")
        return True
    except stripe.error.StripeError as e:
        logger.error(f"Chyba pri rušení subscription: {e}")
        return False


def get_subscription_status(subscription_id: str) -> Optional[Dict]:
    """Získa stav subscription"""
    try:
        sub = stripe.Subscription.retrieve(subscription_id)
        return {
            'id': sub.id,
            'status': sub.status,
            'current_period_end': sub.current_period_end,
            'cancel_at_period_end': sub.cancel_at_period_end
        }
    except stripe.error.StripeError as e:
        logger.error(f"Chyba pri získavaní subscription: {e}")
        return None
