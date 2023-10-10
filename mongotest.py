import re
import markdown
import yaml  # Import the yaml library
from models import BlogPost

def parse_metadata_from_md(md_content):
    pattern = r"^---\n(.+?)\n---"
    match = re.search(pattern, md_content, re.DOTALL)
    if not match:
        raise ValueError("No metadata found in the markdown file.")
    
    metadata_str = match.group(1)
    # Use YAML to parse the metadata block
    metadata = yaml.safe_load(metadata_str)
    
    return metadata

def upload_markdown_to_mongo(md_file_path):
    with open(md_file_path, 'r', encoding='utf-8') as f:
        md_content = f.read()

    # Parse metadata
    metadata = parse_metadata_from_md(md_content)

    # Extract the main content by removing the metadata part
    main_content = md_content.split("---\n", 2)[2]
    
    # Convert the markdown content to HTML
    html_content = markdown.markdown(main_content)

    # Creating and saving the blog post
    blog_post = BlogPost(
        title=metadata.get("title", "Default Title"),
        blog_post_id=metadata.get("blog_post_id", "Default Blog Post ID"),
        content=html_content,
        author=metadata.get("author", "Default Author"),
        tags=metadata.get("tags", []),
        related_links=metadata.get("related_links", []),
        media_bucket_links=metadata.get("media_links", []),
        date=metadata.get("created_at", "Default Creation Date"),
        summary=metadata.get("summary", "Default Summary"),
        questions=metadata.get("questions", []),  # Add questions here
        suggested_questions=metadata.get("suggested_questions", [])  # Add suggested questions here
    )
    blog_post.save_to_mongo()

#md_file_path = "blog_posts/economics/natural_rate_of_interest.md"
#md_file_path = "blog_posts/politics/Americas_Interest_Ukraine.md"
md_file_path = "blog_posts/history/Ukraine_Next_Generation.md"


upload_markdown_to_mongo(md_file_path)
