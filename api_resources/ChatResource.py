from flask_restful import Resource, reqparse
from flask_limiter.util import get_remote_address
from flask import session, jsonify, request
import logging
import os
import openai
from flask_limiter import Limiter

# Initialize logging
logging.basicConfig(level=logging.INFO)

# Initialize OpenAI API
openai_api_key = os.getenv('svoboda')
logging.info("Loading OpenAI API key")
openai.api_key = openai_api_key
logging.info("OpenAI API key loaded")

# Initialize rate limiter
limiter = Limiter(
    key_func=get_remote_address,
)
logging.info("Rate limiter initialized")

class ChatGPTResource(Resource):
    decorators = [limiter.limit("5 per minute")]

    def post(self):
        try:
            data = request.get_json()
            parser = reqparse.RequestParser()
            parser.add_argument('input', type=str, required=True)
            parser.add_argument('token_limit', type=int, default=150)
            args = parser.parse_args()

            user_input = args['input'].strip()
            token_limit = args['token_limit']
            blog_context = session.get('current_blog_content', '')
            token_limit = data.get('token_limit', 150)
            if 'chat_history' not in session:
                session['chat_history'] = []
            session['chat_history'].append({
                "role": "user",
                "content": user_input
            })
            # Validate input and context length
            if len(user_input) > 100:
                logging.warning("Input or context too long.")
                return jsonify({"error": "Input or context too long"}), 400
            messages = [
                {"role": "system", "content": "You're an assistant teaching users about topics in history, economics, philosophy, politics, technology, and current events. We want to engage users and have them ask questions.Limit your results to 100 tokens."},
                {"role": "user", "content": f"{blog_context}"},
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
            # Add the assistant's message to the chat historya
            session['chat_history'].append({
                "role": "assistant",
                "content": message
            })
            return {'message': message}, 200
        except Exception as e:
            logging.error(f"Error calling GPT-4 API: {e}")
            return {'error': 'Error communicating with GPT-4 API'}, 500
