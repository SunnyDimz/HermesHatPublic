import markdown
import logging
from models.models import BlogPost, mongo

def parse_metadata(md_content):
    metadata = {}
    lines = md_content.split("\n")
    logging.info(f"Lines: {lines}")
    for line in lines:
        if line.startswith("---"):
            logging.info("Reached end of metadata.")
            continue
        elif ":" in line:
            key, value = line.split(":", 1)
            logging.info(f"Found metadata: {key} - {value}")
            metadata[key.strip()] = value.strip()
            logging.info(f"Metadata: {metadata}")
    logging.info(f"Metadata: {metadata}")
    return metadata

def upload_markdown_to_mongo(md_file_path):
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Separate metadata from the main content
    meta_str, main_content = md_content.split("---\n", 1)
    html_content = markdown.markdown(main_content)

    # Parse metadata
    metadata = parse_metadata(meta_str)

    title = metadata.get("title", "Default Title")
    summary = metadata.get("summary", "Default Summary")
    author = metadata.get("author", "Default Author")
    created_at = metadata.get("created_at", "Default Creation Date")
    updated_at = metadata.get("updated_at", "Default Update Date")
    related_links = metadata.get("related_links", "").split(", ")
    media_links = metadata.get("media_links", "").split(", ")

    # Creating and saving the blog post
    blog_post = BlogPost(title, html_content, summary, author, created_at, updated_at, related_links, media_links)
    blog_post.save_to_mongo()
