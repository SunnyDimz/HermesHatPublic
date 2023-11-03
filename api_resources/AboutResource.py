from flask_restful import Resource, reqparse
from flask_mail import Message
from flask import flash, redirect, url_for
from flask_mail import Mail
from app import app
mail = Mail(app)
class AboutResource(Resource):
    def get(self):
        return {'message': 'About page content here'}, 200

    def post(self):
        parser = reqparse.RequestParser()
        parser.add_argument('name', required=True)
        parser.add_argument('email', required=True)
        parser.add_argument('message', required=True)
        args = parser.parse_args()

        msg = Message('New Contact Form Submission',
                      sender='your_email@gmail.com',  # Replace with your email
                      recipients=['your_email@gmail.com'])  # Replace with your email
        msg.body = f"From: {args['name']} <{args['email']}>\n\nMessage:\n{args['message']}"
        mail.send(msg)

        flash('Your message has been sent. Thank you!', 'success')
        return {'message': 'Your message has been sent'}, 200
