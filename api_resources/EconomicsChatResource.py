from flask_restful import Resource, reqparse
from flask_limiter.util import get_remote_address
from flask import session, jsonify, request
import logging
import os
import openai
from flask_limiter import Limiter

def extract_fred_code(message):
    # Look for the keyword "CODE: " in the message
    start = message.find("CODE: ")
    if start == -1:
        return None  # No code found
    
    # Find the starting and ending positions of the code
    start += len("CODE: ")
    end = message.find(" ", start)  # Assuming a space terminates the code
    if end == -1:
        end = len(message)  # If no space is found, take until the end of the string

    # Extract the FRED code
    fred_code = message[start:end]
    return fred_code

class EconomicsChatGPTResource(Resource):
    # Initialize rate limiter
    limiter = Limiter(
        key_func=get_remote_address,
    )
    logging.info("Rate limiter initialized")
    decorators = [limiter.limit("10 per minute")]

    def post(self):
        try:
            data = request.get_json()
            question = data.get('input')

            parser = reqparse.RequestParser()
            parser.add_argument('input', type=str, required=True)
            parser.add_argument('token_limit', type=int, default=300)  # Updated token limit
            args = parser.parse_args()

            user_input = args['input'].strip()
            print(user_input)
            token_limit = args['token_limit']

            if 'chat_history' not in session:
                session['chat_history'] = []

            session['chat_history'].append({
                "role": "user",
                "content": user_input
            })

            if len(user_input) > 300:  # Updated length check
                logging.warning("Input or context too long.")
                return jsonify({"error": "Input or context too long"}), 400

            # Updated system message to be economics-focused and potentially include FRED codes.
            messages = [
                {"role": "system", "content": "You're an assistant specialized in economics. Your role is to answer questions about economics topics and reference a signle appropriate FRED code if possible. Prefix the code with CODE:. Results are limited to 300 tokens, provide the code in the beginning."},
                {"role": "user", "content": f"{user_input}"}
            ]

            messages.extend(session['chat_history'])
            logging.info(f"Sending messages to GPT-4: {messages}")
            
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=messages,
                max_tokens=token_limit
            )
            
            message = response['choices'][0]['message']['content'].strip()
            logging.info(f"Received message from GPT-4: {message}")
            
            # Extract FRED code
            fred_code = extract_fred_code(message)

            session['chat_history'].append({
                "role": "assistant",
                "content": message
            })
            if fred_code:
                session['fred_code'] = fred_code

            return {'message': message}, 200

        except Exception as e:
            logging.error(f"Error calling GPT-4 API: {e}")
            return {'error': 'Error communicating with GPT-4 API'}, 500
