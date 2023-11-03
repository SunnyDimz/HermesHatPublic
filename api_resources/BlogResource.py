from flask_restful import Resource
import os
import yaml
from markdown import markdown
from flask import session
import logging
from utils.youtube_api import fetch_youtube_video_details

# Inside BlogResource.py or wherever your BlogResource class is defined
def get_blog_data(section, post):
    markdown_file_path = os.path.join("blog_posts", section, f"{post}.md")
    try:
        with open(markdown_file_path, 'r') as f:
            metadata_str, content_str = f.read().split("---", 2)[1:]
            metadata = yaml.safe_load(metadata_str)
            youtube_details = []  # You can populate this as before
            related_links = metadata.get('related_links', [])
            suggested_questions=metadata.get('suggested_questions', [])
            media_bucket_links = metadata.get('media_bucket_links', [])
            content_html = markdown(content_str)
            session['current_blog_content'] = metadata.get('summary', "")
            for link in media_bucket_links:
                api_key = os.getenv("api_key")
                details = fetch_youtube_video_details(link, api_key)  # Your function to fetch YouTube video details
                youtube_details.append(details)
            return {'data': {
                        'metadata': metadata,
                        'related_links': related_links,
                        'content_html': content_html,
                        'youtube_details': youtube_details,
                        'suggested_questions': suggested_questions,
                        'media_bucket_links': media_bucket_links
                    }, 'status_code': 200}
    except FileNotFoundError:
        return {'message': 'Post not found', 'status_code': 404}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {'message': 'An error occurred', 'status_code': 500}

class BlogResource(Resource):
    def get(self, section, post):
        blog_data = get_blog_data(section, post)
        return blog_data, 200