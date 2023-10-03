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
from bleach import clean

mongo_password = os.getenv("MONGO_PASSWORD")

# URL encode the MongoDB password
encoded_mongo_password = quote_plus(mongo_password)
app.config["MONGO_URI"] = f"mongodb+srv://dborzhko:{encoded_mongo_password}@sunnydimz.lrqdhvy.mongodb.net/EconWizardDB"

try:
    mongo = PyMongo(app)
    client = MongoClient(app.config["MONGO_URI"])
    db = client.EconWizardDB
    blog_posts = db.blog_posts
    print("MongoDB Databases:", mongo.cx.list_database_names())
    logging.debug("Successfully connected to MongoDB.")
except Exception as e:
    print(f"Could not connect to MongoDB: {e}")
    logging.error(f"Could not connect to MongoDB: {e}")

class BlogPost:
    def __init__(self, title,blog_post_id, content, author, tags, related_links, media_bucket_links, date, summary, questions = []):
        self.title = self.validate_title(title)
        self.blog_post_id = blog_post_id
        self.content = self.validate_content(content)
        self.author = self.validate_author(author)
        self.tags = self.validate_tags(tags)
        self.related_links = self.validate_links(related_links)
        self.media_bucket_links = self.validate_links(media_bucket_links)
        self.date = self.validate_date(date)
        self.summary = self.validate_summary(summary)
        self.questions = [{"question": q["question"], "question_id": q["question_id"], "options": q["options"], "responses": [], "response_count": {option: 0 for option in q["options"]}} for q in questions]

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
                "blog_post_id": self.blog_post_id,
                "content": self.content,
                "author": self.author,
                "tags": self.tags,
                "related_links": self.related_links,
                "media_bucket_links": self.media_bucket_links,
                "date": self.date,
                "summary": self.summary,
                "highlights": [],
                "comments": [],
                "questions": self.questions
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
    def __init__(self, blog_post_id, user_id, comment_text, parent_comment_id=None):
        self.blog_post_id = blog_post_id
        self.user_id = user_id
        self.comment_text = self.validate_comment_text(comment_text)
        self.parent_comment_id = parent_comment_id
        self.reactions = {"thumbs_up": 0, "thumbs_down": 0, "question_mark": 0}

    def validate_comment_text(self, comment_text):
        # Validation to prevent attacks
        if not comment_text or len(comment_text) < 2:
            raise ValueError("Invalid comment")
        # Sanitize the comment text
        allowed_tags = ['b', 'i', 'u', 'em', 'strong']
        return clean(comment_text, tags=allowed_tags, strip=True)
    def save_to_mongo(self):
        comment_data = {
            "blog_post_id": self.blog_post_id,
            "user_id": self.user_id,
            "comment_text": self.comment_text,
            "parent_comment_id": self.parent_comment_id,
            "reactions": self.reactions,
            "timestamp": datetime.now()
        }
        mongo.db.comments.insert_one(comment_data)


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
    def __init__(self, user_id, email, google_token = None, has_purchased_photos=False):
        self.user_id = user_id
        self.email = email
        self.google_token = google_token
        self.has_purchased_photos = has_purchased_photos

    def save_to_mongo(self):
        user_data = {
            "_id": self.user_id,
            "email": self.email,
            "google_token": self.token,
            "has_purchased_photos": self.has_purchased_photos,
        }
        mongo.db.users.insert_one(user_data)

    @classmethod
    def update_purchase_status(cls, user_id, status=True):
        try:
            mongo.db.users.update_one(
                {"_id": user_id},
                {"$set": {"has_purchased_photos": status}}
            )
        except Exception as e:
            logging.error(f"Failed to update purchase status: {e}")

class FredData:
    def __init__(self, code, realtime_start, realtime_end, observation_start, observation_end, units, count, observations):
        self.code = code
        self.realtime_start = realtime_start
        self.realtime_end = realtime_end
        self.observation_start = observation_start
        self.observation_end = observation_end
        self.units = units
        self.count = count
        self.observations = observations

    def save_to_mongo(self):
        try:
            fred_data = {
                "code": self.code,
                "realtime_start": self.realtime_start,
                "realtime_end": self.realtime_end,
                "observation_start": self.observation_start,
                "observation_end": self.observation_end,
                "units": self.units,
                "count": self.count,
                "observations": self.observations
            }
            print(fred_data)
            print(type(fred_data))
            mongo.db.fred_data.insert_one(fred_data)
            logging.info(f"Successfully saved {self.code} to MongoDB.")
        except Exception as e:
            logging.error(f"Error saving to MongoDB: {e}")
            raise e
