from flask_restful import Resource
import os
from markdown import markdown
from flask import session
import logging

# Placeholder for importing your YouTube API utility
# from utils.youtube_api import fetch_youtube_video_details

# Inside BlogResource.py or wherever your BlogResource class is defined
def get_blog_data(section, post):
    """
    Retrieves blog data including metadata, related links, content in HTML,
    and YouTube video details for a given section and post.

    Parameters:
    - section: The category or section of the blog post.
    - post: The specific blog post name or identifier.

    Returns a dictionary with the blog post data and status code.
    """
    # Placeholder path for blog posts, replace with actual path or method to retrieve posts
    markdown_file_path = os.path.join("path_to_blog_posts", section, f"{post}.md")
    try:
        with open(markdown_file_path, 'r') as f:
            # Assuming the markdown file contains a YAML metadata block separated by '---'
            metadata_str, content_str = f.read().split("---", 2)[1:]
            metadata = yaml.safe_load(metadata_str)
            content_html = markdown(content_str)
            session['current_blog_content'] = metadata.get('summary', "")
            
            # The following block of code should be replaced with your logic to fetch YouTube details
            # For the public version, you might want to remove this and just explain what it does
            youtube_details = []
            # for link in media_bucket_links:
            #     api_key = your_method_to_get_api_key()  # Replace with your method to get the API key
            #     details = fetch_youtube_video_details(link, api_key)
            #     youtube_details.append(details)

            return {
                'data': {
                    'metadata': metadata,
                    'content_html': content_html,
                    # 'youtube_details': youtube_details,  # Include if you're fetching YouTube details
                },
                'status_code': 200
            }
    except FileNotFoundError:
        logging.error("Blog post not found.")
        return {'message': 'Blog post not found', 'status_code': 404}
    except Exception as e:
        logging.error(f"An error occurred: {e}")
        return {'message': 'An error occurred while retrieving the blog post', 'status_code': 500}

class BlogResource(Resource):
    def get(self, section, post):
        """
        GET endpoint for retrieving a specific blog post.

        Parameters:
        - section: The category or section to which the blog post belongs.
        - post: The name or identifier of the blog post.
        
        Returns the blog post data along with the appropriate HTTP status code.
        """
        blog_data = get_blog_data(section, post)
        return blog_data, blog_data['status_code']
