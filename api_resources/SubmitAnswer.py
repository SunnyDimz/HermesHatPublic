from flask_restful import Resource, reqparse
from flask import request, jsonify
import logging
from utils.utils import update_response_count  # Importing the update_response_count function

class AnswerResource(Resource):
    def post(self):
        logger = logging.getLogger('root')
        try:
            data = request.get_json()
            logger.info(f"Received answer: {data}")

            if not all(key in data for key in ('title', 'question_id', 'selected_answer')):
                return {'status': 'failure', 'message': 'Missing required fields'}, 400

            post_title = data.get('title')
            logger.info(f"Received answer for blog post {post_title}")
            question_id = data.get('question_id')
            logger.info(f"Received answer for question {question_id}")
            selected_answer = data.get('selected_answer')
            logger.info(f"Received answer {selected_answer}")

            result = update_response_count(post_title, question_id, selected_answer)  # Calling the utility function
            logger.info(f"Result: {result}")
            logger.info(f"Result Status: {result['status']}")

            if result['status'] == 'success':
                return {'status': 'success', 'message': 'Successfully updated the database'}, 200
            else:
                return {'status': 'failure', 'message': 'Failed to update the database'}, 500

        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return {'status': 'failure', 'message': 'An unexpected error occurred'}, 500
