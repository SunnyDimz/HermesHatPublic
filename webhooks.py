import stripe
import os
import json
from flask import request, Response, Flask, jsonify
import logging
from config import app

logging.basicConfig(level=logging.INFO)

# Add your Stripe API Key and Webhook Secret here
stripe.api_key = os.getenv("STRIPE_SECRET")
endpoint_secret = os.getenv("STRIPE_WEBHOOK")

def webhook_received():
    payload = request.data.decode("utf-8")
    sig_header = request.headers.get("Stripe-Signature")

    event = None

    try:
        event = stripe.Webhook.construct_event(
            payload, sig_header, endpoint_secret
        )
        logging.info(f"payload: {payload}")
        logging.info(f"sig_header: {sig_header}")
        logging.info(f"Webhook received: {event}")
    except ValueError:
        # Invalid payload
        app.logger.error("Invalid payload")
        return jsonify({"status": "failure", "reason": "Invalid payload"}), 400
    except stripe.error.SignatureVerificationError:
        # Invalid signature
        app.logger.error("Invalid signature")
        return jsonify({"status": "failure", "reason": "Invalid signature"}), 400

    # Log the event or do something else
    app.logger.info(f"Received event: {event['type']}")

    # All done, return successful response
    return jsonify({"status": "success"})





