import stripe
import os
import json
from flask import request, Response, Flask
import logging

logging.basicConfig(level=logging.INFO)

# Add your Stripe API Key and Webhook Secret here
stripe.api_key = os.getenv("STRIPE_PUBLIC")
endpoint_secret = os.getenv("STRIPE_WEBHOOK")

def webhook_received():
    logging.info("Received a webhook event.")
    request_data = json.loads(request.data)
    signature = request.headers.get("stripe-signature")
    try:
        event = stripe.Webhook.construct_event(
            payload=request.data, sig_header=signature, secret=endpoint_secret
            
        )
        logging.info("Webhook constructed successfully.")
    except ValueError as e:
        return Response(status=400)
    except stripe.error.SignatureVerificationError as e:
        return Response(status=400)

    if event["type"] == "payment_intent.succeeded":
        payment_intent = event["data"]["object"]
        connected_account_id = event["account"]
        handle_successful_payment_intent(connected_account_id, payment_intent)
        logging.info("Payment intent succeeded.")

    return json.dumps({"success": True}), 200

def handle_successful_payment_intent(connected_account_id, payment_intent):
    # Fulfill the purchase
    # Your logic here
    print('Connected account ID: ' + connected_account_id)
    print(str(payment_intent))
