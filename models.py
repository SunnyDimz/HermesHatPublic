from flask import Flask
from pymongo import MongoClient
from flask_pymongo import PyMongo
from bson import ObjectId
import os
from urllib.parse import quote_plus
from datetime import datetime
from dotenv import load_dotenv
from urllib.parse import urlparse
load_dotenv()
import logging
logging.basicConfig(filename='models.log', level=logging.INFO)
import ssl
import certifi
from config import app

mongo_password = os.getenv("MONGO_PASSWORD")

# URL encode the MongoDB password
encoded_mongo_password = quote_plus(mongo_password)
app.config["MONGO_URI"] = f"mongodb+srv://dborzhko:{encoded_mongo_password}@sunnydimz.lrqdhvy.mongodb.net/EconWizardDB"

try:
    mongo = PyMongo(app)
    print("MongoDB Databases:", mongo.cx.list_database_names())
    logging.debug("Successfully connected to MongoDB.")
except Exception as e:
    print(f"Could not connect to MongoDB: {e}")
    logging.error(f"Could not connect to MongoDB: {e}")

class BlogPost:
    def __init__(self, title, content, author, tags, related_links, media_bucket_links, date, summary):
        self.title = self.validate_title(title)
        self.content = self.validate_content(content)
        self.author = self.validate_author(author)
        self.tags = self.validate_tags(tags)
        self.related_links = self.validate_links(related_links)
        self.media_bucket_links = self.validate_links(media_bucket_links)
        self.date = self.validate_date(date)
        self.summary = self.validate_summary(summary)

    def validate_title(self, title):
        if not title or len(title) < 5:
            raise ValueError("Invalid title")
        return title
    
    def validate_content(self, content):
        if not content or len(content) < 10:
            raise ValueError("Invalid content")
        return content

    def validate_author(self, author):
        if not author or len(author) < 3:
            raise ValueError("Invalid author")
        return author

    def validate_tags(self, tags):
        if not tags or len(tags) == 0:
            raise ValueError("Tags cannot be empty")
        return tags

    def validate_links(self, related_links):
        logging.info(f"Validating links: {related_links}")
        for link in related_links:
            link = link.strip()  # Remove leading and trailing whitespaces
            parsed_url = urlparse(link)
            logging.info(f"Validating link: {link}")
            if not parsed_url.scheme == 'https':
                raise ValueError(f"Invalid URL '{link}', must be HTTPS")
        return related_links

    def validate_date(self, date_str):
        try:
            return datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            raise ValueError("Invalid date format, expected YYYY-MM-DD")

    def validate_summary(self, summary):
        if not summary or len(summary) < 10:
            raise ValueError("Invalid summary")
        return summary

    def save_to_mongo(self):
        try:
            blog_post_data = {
                "title": self.title,
                "content": self.content,
                "author": self.author,
                "tags": self.tags,
                "related_links": self.related_links,
                "media_bucket_links": self.media_bucket_links,
                "date": self.date,
                "summary": self.summary,
                "highlights": [],
                "comments": []
            }
            mongo.db.blog_posts.insert_one(blog_post_data)
            logging.info(f"Successfully saved {self.title} to MongoDB.")

        except Exception as e:
            logging.error(f"Error saving to MongoDB: {e}")
            raise e
    

class Highlight:
    def __init__(self, blog_post_id, user_id, highlight_type, highlighted_text):
        self.blog_post_id = blog_post_id
        self.user_id = user_id
        self.highlight_type = highlight_type
        self.highlighted_text = highlighted_text

    def save_to_mongo(self):
        highlight_data = {
            "user_id": self.user_id,
            "highlight_type": self.highlight_type,
            "highlighted_text": self.highlighted_text
        }
        mongo.db.blog_posts.update_one({"_id": ObjectId(self.blog_post_id)}, {"$push": {"highlights": highlight_data}})

class Comment:
    def __init__(self, blog_post_id, user_id, comment_text):
        self.blog_post_id = blog_post_id
        self.user_id = user_id
        self.comment_text = comment_text

    def save_to_mongo(self):
        comment_data = {
            "user_id": self.user_id,
            "comment_text": self.comment_text
        }
        mongo.db.blog_posts.update_one({"_id": ObjectId(self.blog_post_id)}, {"$push": {"comments": comment_data}})

class YouTubeVideo:
    def __init__(self, video_id, title, description, tags):
        self.video_id = video_id
        self.title = title
        self.description = description
        self.tags = tags

    def save_to_mongo(self):
        video_data = {
            "video_id": self.video_id,
            "title": self.title,
            "description": self.description,
            "tags": self.tags
        }
        mongo.db.youtube_videos.insert_one(video_data)
class User:
    def __init__(self, user_id, email):
        self.user_id = user_id
        self.email = email
    def save_to_mongo(self):
        user_data = {
            "_id": self.user_id,
            "email": self.email,
        }
        mongo.db.users.insert_one(user_data)
