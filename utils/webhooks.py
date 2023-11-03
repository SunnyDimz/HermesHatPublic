import stripe
import os
import json
from flask import request, Response, Flask, jsonify
import logging
from config import app  # Replace this with your actual config import
from flask_socketio import SocketIO, emit, join_room
import jwt
from utils.jwt_utils import verify_jwt  # Replace this with your actual jwt verification import
from models.models import mongo, db  # Replace this with your actual db import
logging.basicConfig(level=logging.INFO)

# Initialize Stripe API Key and Webhook Secret
stripe.api_key = os.getenv("STRIPE_SECRET")
endpoint_secret = os.getenv("STRIPE_WEBHOOK")

# Initialize SocketIO
socketio = SocketIO(app)

def webhook_received():
    try:
        payload = request.data.decode("utf-8")
        sig_header = request.headers.get("Stripe-Signature")

        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        
        # Handle the event
        if event['type'] == 'checkout.session.completed':
            session = event['data']['object']
            app.logger.info(f"Payment was successful: {session}")

            if session.get('payment_status') == 'paid':
                customer_email = session.get("customer_details", {}).get("email")
                if customer_email:
                    existing_user = db.users.find_one({"email": customer_email})
                    if existing_user:
                        db.users.update_one(
                            {"_id": existing_user["_id"]},
                            {"$set": {"has_purchased_photos": True}}
                        )
                        app.logger.info(f"Updated payment status for user {existing_user['_id']}.")
                    else:
                        app.logger.warning(f"No user found for the email {customer_email}.")
                else:
                    app.logger.warning("Email not found in the payment session.")
        
        return jsonify(success=True), 200

    except stripe.error.CardError as e:
        app.logger.error(f"CardError: {e.user_message}")
    except stripe.error.RateLimitError as e:
        app.logger.error("RateLimitError: Too many requests made to the API too quickly.")
    except stripe.error.InvalidRequestError as e:
        app.logger.error("InvalidRequestError: Invalid parameters were supplied to Stripe's API.")
    except stripe.error.AuthenticationError as e:
        app.logger.error("AuthenticationError: Authentication with Stripe's API failed.")
    except stripe.error.APIConnectionError as e:
        app.logger.error("APIConnectionError: Network communication with Stripe failed.")
    except stripe.error.StripeError as e:
        app.logger.error(f"StripeError: {e.user_message}")
    except Exception as e:
        app.logger.error(f"An unexpected error occurred: {e}")

    return jsonify({"status": "failure", "reason": "An error occurred while processing your request."}), 400

@socketio.on('connect')
def handle_connect():
    token = request.args.get('token')
    user_id = verify_jwt(token)
    
    if user_id:
        join_room(user_id)
        emit('status', {'data': 'Connected'})
    else:
        return False
