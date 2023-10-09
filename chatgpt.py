from flask import Flask, request, jsonify
import openai
import os
import sys
import logging
from config import app
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI API
openai_api_key = os.getenv('svoboda')
logging.info("Loading OpenAI API key")
openai.api_key = openai_api_key
logging.info("OpenAI API key loaded")

# Initialize rate limiter
limiter = Limiter(
    app=app,
    key_func=get_remote_address,
)
logging.info("Rate limiter initialized")

@app.route('/api/chat', methods=['POST'])
@limiter.limit("5 per minute")
def chat():
    """Chat with GPT-4"""
    try:
        data = request.get_json()
        if not data:
            logging.warning("No data received.")
            return jsonify({"error": "No data received"}), 400
        user_input = data.get('input', '').strip()
        blog_context = data.get('context', '').strip()
        token_limit = data.get('token_limit', 100)

        # Validate input and context length
        if len(user_input) > 100 or len(blog_context) > 100:
            logging.warning("Input or context too long.")
            return jsonify({"error": "Input or context too long"}), 400

        messages = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": f"{blog_context}"},
            {"role": "user", "content": f"{user_input}"}
        ]
        logging.info(f"Sending messages to GPT-4: {messages}")
        response = openai.ChatCompletion.create(
            model="gpt-4",
            messages=messages,
            max_tokens=token_limit
        )
        message = response['choices'][0]['message']['content'].strip()
        logging.info(f"Received message from GPT-4: {message}")

        return jsonify({"message": message})

    except Exception as e:
        logging.error(f"Error calling GPT-4 API: {e}")
        return jsonify({"error": "Error communicating with GPT-4 API"}), 500
