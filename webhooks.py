import stripe
import os
import json
from flask import request, Response, Flask, jsonify
import logging
from config import app
from flask_socketio import SocketIO, emit, join_room
from jwt
from utils import verify_jwt
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
    connected_account_id = event.get('account', None)
    if connected_account_id is None:
        app.logger.warning("No 'account' field in the received event.")
    # Handle the event
    if event['type'] == 'checkout.session.completed':
        session = event['data']['object']

        # Log for debugging
        app.logger.info(f"Payment was successful: {session}")

        # Check payment status
        if session.get('payment_status') == 'paid':
            # TODO: Update your database, send email notifications, etc.
            app.logger.info(f"Payment for session {session['id']} was successful.")
        else:
            app.logger.warning(f"Payment for session {session['id']} failed.")
        # Log the event or do something else
    app.logger.info(f"Received event: {event['type']}")
    return jsonify(success=True), 200


# Initialize SocketIO
socketio = SocketIO(app)

# On WebSocket connection
@socketio.on('connect')
def handle_connect():
    # Extract the token from the query string or other means
    token = request.args.get('token')
    
    # Validate the token and get the user_id
    user_id = verify_jwt(token)
    
    if user_id:
        # Join a room identified by the user_id
        join_room(user_id)
        emit('status', {'data': 'Connected'})
    else:
        # Reject the connection
        return False





