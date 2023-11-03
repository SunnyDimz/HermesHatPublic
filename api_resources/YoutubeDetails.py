from flask_restful import Resource, reqparse
from utils.youtube_api import fetch_youtube_video_details_batch  # Import the fetch_youtube_video_details_batch function
import logging
from flask import request
import os

logger = logging.getLogger('root')
class YouTubeDetailsResource(Resource):
    def get(self):
        try:
            section = request.args.get('section')
            section_video_ids = {
            'philosophy' : ['Auuk1y4DRgk', 'nsgAsw4XGvU', 'xL_sMXfzzyA', '7Kuk35VNSEc', '8rf3uqDj00A', 't-gH7Waedtk', 'Smq5uRhM_IA', '5IEYW5wuK3Y', 'x4vd21slhmw', 'MaobMHescwg', 'xpVQ3l5P0A4', 'tJnWHVwvYSQ'],
            'economics' : ['bOMksnSaAJ4', 'B_nGEj8wIP0', 'V6S6pMsKzlI', 'fTiba4ElD0U', 'p6FJRoTf-Us', 'Si4iyyJDa7c', 'F34YdEU7zZg', 'ynHzdVrzgxg', 'Q_3r49XXRw4', 'TEzi0SMCu5A', 'o6UXRZ2XwgU', '27Tf8RN3uiM', 'sGYl17DiEwo', 'Cjj-fCKGdts', '3qVa31BtNi8', 'F3EBfS9IcB4', '1EJVCRm9nHg', 'JSumJxQ5oy4', '3t6a7Gj0ubc', 'NqUSDi-mvqw', 'XRVmg9HV-sQ'],
            'history' : ['FIbdbrN9cwo', '0iRvEPcQV3I', '9DvmLMUfGss', 'NxpuT1SNurU', 'KDLTUMIR4jg', '3ww4ofe0v70', 'ejezcZD38Dw', 'Ya0bG4_xRQg', 'jhi2icRXbHo', 'UKLWzj29vl4', 'BQSjO5-sSOY', '1QlM7TXkl00', '3__jvGa5L6Y', 'qwtB2ovhMuk', 'EUELed7UuDQ', 'hzH5IDnLaBA'],
            'politics' : ['PcZCot2wyTE', 'RNKkcAOYCVY', 'lTyZAul60ok', 'nO44vzTLa7g', 'TAMWsWvcbtg', 'Es0YGdROxVE', 'fgRTkN9U-uA', 'OET1UGhJIYI', 'rqthAe5-4Zg', 'Atk7V3W6oUc'],
            }
            video_ids = section_video_ids.get(section, [])
            logger.info(f"Fetching YouTube video details for section: {section}")
            api_key = os.getenv("api_key")
            details = fetch_youtube_video_details_batch(video_ids, api_key)  # Calling the utility function
            return {'details': details}, 200
        except Exception as e:
            logger.error(f"An error occurred: {e}")
            return {'message': 'An unexpected error occurred'}, 500
