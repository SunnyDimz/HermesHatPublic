from flask_restful import Resource, reqparse
import stripe
from utils.webhooks import webhook_received  # Import the webhook_received function
from models.models import User  # Import your User model
from flask import session, g, jsonify
import os
import logging

logger = logging.getLogger('root')
class PaymentResource(Resource):
    # Stripe Webhook
    def post(self):
        try:
            logger.info("Received webhook from Stripe.")
            return webhook_received(), 200
        except Exception as e:
            logger.error(f"An error occurred during Stripe webhook processing: {e}")
            return {'message': 'An unexpected error occurred'}, 500

    # Create Checkout Session
    def put(self):
        try:
            stripe.api_key = os.getenv("STRIPE_SECRET")
            session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'unit_amount': 200,  # $2.00
                        'product_data': {
                            'name': 'Photos ZIP File',
                        },
                    },
                    'quantity': 1,
                }],
                mode='payment',
                success_url='http://localhost:5000/success',
                cancel_url='http://localhost:5000/cancel',
            )
            return {'id': session.id}, 200
        except Exception as e:
            logger.error(f"An error occurred during checkout session creation: {e}")
            return {'message': 'An unexpected error occurred'}, 500

    # Check Payment Status
    def get(self):
        try:
            if not g.user_logged_in:
                return {'status': 'failure', 'reason': 'User not logged in'}, 401

            google_token_from_session = session.get('google_token')
            existing_user = mongo.db.users.find_one({"google_token": google_token_from_session})

            if existing_user and existing_user.get("has_purchased_photos"):
                return {'status': 'success', 'has_paid': True}, 200
            else:
                return {'status': 'success', 'has_paid': False}, 200
        except Exception as e:
            logger.error(f"An error occurred during payment status check: {e}")
            return {'message': 'An unexpected error occurred'}, 500
